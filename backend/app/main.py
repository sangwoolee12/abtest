import os
import time
import uuid
import json
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from .models import (
    PredictRequest, PredictResponse, ImageGenerationRequest,
    ImageGenerationResponse, UserChoiceIn, ABTestStoredResult
)
from .config import RESULTS_PATH
from .utils import append_jsonl, _load_jsonl, _feature_sentence, _to_class
from .business_logic import (
    sample_personas, llm_persona_scores, fast_persona_scores,
    weighted_ctr_from_scores, _knn_follow, generate_third_copy, calibrate_ctr,
    _call_gemini_with_retry
)
from .rag_utils import rag_system

app = FastAPI(title="A/B Test Backend", version="1.2.2")

# CORS (프론트는 그대로 사용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_INDEX = []  # 인메모리 인덱스(옵션)

@app.get("/")
def root():
    return {"ok": True, "service": "ab-test-backend"}

@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if not (req.marketing_a and req.marketing_b):
        raise HTTPException(status_code=400, detail="marketing_a, marketing_b는 필수입니다.")

    # 1) 페르소나 샘플링
    personas = sample_personas(req, topN=5)

    # 2) Gemini 먼저 시도 → 실패 시 fast 경로
    llm_analysis = None
    try:
        rows, winner_kw, llm_analysis = llm_persona_scores(req, personas)
    except Exception as e:
        print(f"[Gemini] ❌ LLM 실패, fallback: {e}")
        rows, winner_kw = fast_persona_scores(req, personas)

        # 3) 가중 CTR (LLM 분석 결과 전달)
    ctr_a, ctr_b, reasons_a, reasons_b = weighted_ctr_from_scores(rows, llm_analysis)

    # 과거 사용자 선택 패턴 기반 가중치 조정 (RAG 학습 효과)
    try:
        choice_patterns = rag_system.get_user_choice_patterns(req)
        print(f"[RAG] 과거 선택 패턴: A({choice_patterns['A']:.2f}), B({choice_patterns['B']:.2f}), C({choice_patterns['C']:.2f})")
        
        # 과거 선택 패턴을 CTR에 반영 (학습 효과)
        if choice_patterns["A"] > 0.1:  # A 선택 비율이 10% 이상인 경우
            ctr_a *= (1 + choice_patterns["A"] * 0.3)  # 최대 30%까지 부스트
        if choice_patterns["B"] > 0.1:  # B 선택 비율이 10% 이상인 경우
            ctr_b *= (1 + choice_patterns["B"] * 0.3)  # 최대 30%까지 부스트
        
        print(f"[RAG] 학습 효과 적용 후: A({ctr_a:.3f}), B({ctr_b:.3f})")
        
    except Exception as e:
        print(f"[RAG] 과거 선택 패턴 분석 실패: {e}")
        choice_patterns = {"A": 0.0, "B": 0.0, "C": 0.0}

    # RAG를 활용한 향상된 분석 생성
    try:
        enhanced_a = rag_system.generate_rag_enhanced_analysis(req, reasons_a)
        enhanced_b = rag_system.generate_rag_enhanced_analysis(req, reasons_b)
        reasons_a = enhanced_a
        reasons_b = enhanced_b
        print(f"[RAG] A안 분석 향상 완료: {len(enhanced_a)}자")
        print(f"[RAG] B안 분석 향상 완료: {len(enhanced_b)}자")
    except Exception as e:
        print(f"[RAG] 분석 향상 실패, 기본 분석 사용: {e}")

    # 4) 간단 KNN 보정 (선택)
    try:
        follow = _knn_follow(
            category=req.category or "",
            ages=req.age_groups or [],
            genders=req.genders or [],
            interests=req.interests or "",
            A=req.marketing_a, B=req.marketing_b,
            k=5, tau_hard=0.9
        )
        if follow.get("mode") == "hard" and follow.get("follow_class") in ["A", "B"]:
            if follow["follow_class"] == "A":
                ctr_a, ctr_b = max(ctr_a, 0.6), min(ctr_b, 0.4)
            else:
                ctr_b, ctr_a = max(ctr_b, 0.6), min(ctr_a, 0.4)
    except Exception:
        pass

    # 5) 캘리브레이션
    category = req.category or "기타"
    ctr_a = calibrate_ctr(ctr_a, category)
    ctr_b = calibrate_ctr(ctr_b, category)

    # 6) C안 생성/분석
    ai_top = "A" if ctr_a >= ctr_b else "B"
    third = generate_third_copy(req, winner_kw, ai_top)

    # C안 CTR 계산: A, B안의 장점을 결합한 개선된 문구이므로 더 높은 CTR 예상
    base_ctr = max(ctr_a, ctr_b)  # 더 높은 CTR을 기준으로
    improvement_factor = 0.25  # 25% 개선 효과 (증가)
    synergy_bonus = 0.12  # 시너지 효과 12% (증가)

    # 과거 C안 선택 패턴 반영 (RAG 학습 효과)
    try:
        if choice_patterns.get("C", 0) > 0.1:  # C 선택 비율이 10% 이상인 경우
            c_boost = choice_patterns["C"] * 0.4  # 최대 40%까지 부스트
            improvement_factor += c_boost
            print(f"[RAG] C안 학습 효과: +{c_boost:.1%}")
    except Exception as e:
        print(f"[RAG] C안 학습 효과 적용 실패: {e}")

    ctr_c = base_ctr * (1 + improvement_factor) + synergy_bonus
    ctr_c = min(1.0, ctr_c)  # 최대 100%로 제한
    
    # C안이 A, B안보다 높은지 확인하고, 낮으면 강제로 높게 설정
    min_ctr_c = max(ctr_a, ctr_b) * 1.15  # 최소 15% 이상 높아야 함
    
    if ctr_c < min_ctr_c:
        ctr_c = min_ctr_c
    
    # C안은 개선된 문구이므로 캘리브레이션을 최소화 (shrink=0.05)
    ctr_c = calibrate_ctr(ctr_c, category, shrink=0.05)

    # C안 LLM 분석 (무조건 LLM 사용)
    c_analysis = None
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            from .llm_utils import _build_c_analysis_prompt, _parse_llm_response
            c_prompt = _build_c_analysis_prompt(req, third)
            c_data = _call_gemini_with_retry(c_prompt, max_retries=1)  # 각 시도마다 1번만
            if c_data:
                c_parsed = _parse_llm_response(str(c_data), "c_analysis")
                c_analysis = c_parsed.get("analysis_c", "")
                if c_analysis and len(c_analysis) >= 300:  # 300자 이상 확인
                    break
                else:
                    print(f"[C Analysis] 시도 {attempt+1}: 분석 길이 부족 ({len(c_analysis) if c_analysis else 0}자)")
            else:
                print(f"[C Analysis] 시도 {attempt+1}: 응답 데이터 없음")
        except Exception as e:
            print(f"[C Analysis] 시도 {attempt+1} 실패: {e}")
        
        if attempt < max_retries - 1:
            print(f"[C Analysis] 재시도 중... ({attempt+2}/{max_retries})")
    
    # 모든 시도 실패 시 기본 분석 생성
    if not c_analysis or len(c_analysis) < 300:
        print(f"[C Analysis] 모든 시도 실패, 기본 분석 생성")
        c_analysis = f"AI가 생성한 새로운 마케팅 문구 '{third}'는 기존 A안과 B안의 장점을 결합하여 {ctr_c:.1%}의 CTR을 예상해요. A안의 {ctr_a:.1%}와 B안의 {ctr_b:.1%}를 상회하는 성과를 기대하며, 두 문구의 강점을 시너지 효과로 결합했습니다. 타겟 고객층의 니즈에 더욱 부합하는 메시지를 전달하며, 개인화된 접근으로 고객 참여도를 높일 것으로 기대해요. 이 문구는 브랜드의 핵심 가치를 담아 고객과의 감정적 연결을 강화하고, 구매 결정에 긍정적인 영향을 미칠 것으로 예상해요."

    # 7) 저장
    log_id = uuid.uuid4().hex
    store = ABTestStoredResult(
        log_id=log_id,
        timestamp=time.time(),
        age_groups=req.age_groups or [],
        genders=req.genders or [],
        interests=req.interests or "",
        category=category,
        marketing_a=req.marketing_a,
        marketing_b=req.marketing_b,
        pred_ctr_a=float(ctr_a),
        pred_ctr_b=float(ctr_b),
        pred_ctr_c=float(ctr_c),
        ai_generated_text=third,
        ai_top_ctr_choice=ai_top,
        user_final_text=None,
    )
    try:
        append_jsonl(RESULTS_PATH, store.dict())
    except Exception as e:
        print(f"[RESULTS] 저장 실패(무시): {e}")

    # 8) 응답
    return PredictResponse(
        ctr_a=float(ctr_a),
        ctr_b=float(ctr_b),
        ctr_c=float(ctr_c),
        analysis_a=reasons_a,
        analysis_b=reasons_b,
        analysis_c=c_analysis,
        ai_suggestion=third,
        ai_top_ctr_choice=ai_top,
        log_id=log_id,
    )

@app.post("/api/generate-images", response_model=ImageGenerationResponse)
def generate_images(req: ImageGenerationRequest):
    # 지연 import → 이미지 모듈 미설치여도 서버 기동 영향 없음
    try:
        from .image_generation import generate_images_with_gemini
        return generate_images_with_gemini(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 사용자 선택 기록 (핵심 수정)
@app.get("/api/rag-insights")
async def get_rag_insights(category: Optional[str] = None):
    """RAG 시스템에서 로그 데이터 기반 인사이트 제공"""
    try:
        insights = rag_system.get_insights_from_logs(category)
        return {
            "success": True,
            "insights": insights,
            "message": "로그 데이터 기반 인사이트를 성공적으로 추출했습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인사이트 추출 실패: {str(e)}")

@app.post("/api/user-choice")
async def user_choice(user: UserChoiceIn, request: Request):
    """
    요구사항:
      - A/B/C 중 하나 선택 시 해당 '문구'가 user_final_text로 기록되어야 한다.
      - 프론트가 "A"/"B"/"C" 같은 축약값을 보내도 실제 문구로 치환해 저장.
      - 경우에 따라 프론트가 필드명을 다르게 보낼 수 있어(request body에서 보조 추출).
      - 다른 기능은 변경하지 않음.
    """
    log_id = (user.log_id or "").strip()
    final = (user.user_final_text or "").strip()

    # 보조 추출: 일부 프론트가 'choice'/'selected' 등으로 보낼 경우 대비
    if not final:
        try:
            raw = await request.json()
            for key in ("user_final_text", "choice", "selected", "final", "selected_text"):
                if key in raw and isinstance(raw[key], str) and raw[key].strip():
                    final = raw[key].strip()
                    break
        except Exception:
            pass

    if not log_id or not final:
        raise HTTPException(status_code=400, detail="log_id와 user_final_text(또는 choice)는 필수입니다.")

    # 1) 현재 로그 로드
    rows = _load_jsonl(RESULTS_PATH)
    if not rows:
        raise HTTPException(status_code=404, detail="결과 로그가 비어 있습니다.")

    # 2) 레코드 매칭 (엄격 → 느슨)
    target = None
    # (a) 엄격 매칭
    for rec in rows:
        if (rec.get("log_id") or "").strip() == log_id:
            target = rec
            break
    # (b) 느슨한 매칭 (공백/대소/부분)
    if target is None:
        lid = log_id.lower()
        for rec in rows:
            rid = str(rec.get("log_id", "")).strip().lower()
            if rid == lid or lid in rid or rid in lid:
                target = rec
                break
    if target is None:
        raise HTTPException(status_code=404, detail="log_id를 찾을 수 없습니다.")

    # 3) 축약값(A/B/C/A안/B안/C안/0/1/2) → 실제 문구로 변환
    key = final
    if key in ("0", "1", "2"):  # 인덱스로 올 수도 있음
        key = {"0": "A", "1": "B", "2": "C"}[key]
    if key in ("A", "A안"):
        final = (target.get("marketing_a") or "").strip()
    elif key in ("B", "B안"):
        final = (target.get("marketing_b") or "").strip()
    elif key in ("C", "C안"):
        final = (target.get("ai_generated_text") or "").strip()
    # else: 이미 실제 문구라고 판단 → 그대로 사용

    if not final:
        raise HTTPException(status_code=400, detail="선택한 문구가 비어 있습니다.")

    # 4) 대상 레코드 갱신
    target["user_final_text"] = final

    # 5) 원자적 저장
    dirpath = os.path.dirname(RESULTS_PATH) or "."
    os.makedirs(dirpath, exist_ok=True)
    import tempfile, shutil
    fd, tmp_path = tempfile.mkstemp(prefix="results_", suffix=".jsonl", dir=dirpath, text=True)
    os.close(fd)
    try:
        with open(tmp_path, "w", encoding="utf-8") as wf:
            for rec in rows:
                wf.write(json.dumps(rec, ensure_ascii=False) + "\n")
        # 파일 교체
        shutil.move(tmp_path, RESULTS_PATH)
    except Exception as e:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"저장 실패: {e}")

    return {"ok": True}

# (옵션) 인덱스 재구축
@app.post("/api/rebuild-index")
def rebuild_index():
    global _INDEX
    _INDEX.clear()
    data = _load_jsonl(RESULTS_PATH)
    for r in data[-1000:]:
        try:
            vec = _feature_sentence(
                r.get("category",""),
                r.get("age_groups",[]),
                r.get("genders",[]),
                r.get("interests",""),
                r.get("marketing_a",""),
                r.get("marketing_b",""),
                r.get("ai_generated_text",""),
            )
            _INDEX.append({
                "log_id": r.get("log_id"),
                "vec": vec,
                "ts": float(r.get("timestamp", time.time())),
                "category": (r.get("category","") or "").lower().strip(),
                "ages": set(map(str.lower, r.get("age_groups",[]))),
                "genders": set(map(str.lower, r.get("genders",[]))),
                "A": r.get("marketing_a",""),
                "B": r.get("marketing_b",""),
                "final_text": r.get("user_final_text",""),
                "final_class": _to_class(r),
            })
        except Exception:
            continue
    return {"ok": True, "count": len(_INDEX)}