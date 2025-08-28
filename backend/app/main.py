import os
import time
import uuid
import json
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    PredictRequest, PredictResponse, ImageGenerationRequest,
    ImageGenerationResponse, UserChoiceIn, ABTestStoredResult
)
from .config import RESULTS_PATH
from .utils import append_jsonl, _load_jsonl, _feature_sentence, _to_class
from .llm_utils import _generate_local_c_analysis_text
from .business_logic import (
    sample_personas, llm_persona_scores, fast_persona_scores,
    weighted_ctr_from_scores, _knn_follow, generate_third_copy, calibrate_ctr
)

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
    try:
        rows, winner_kw = llm_persona_scores(req, personas)
    except Exception as e:
        print(f"[Gemini] ❌ LLM 실패, fallback: {e}")
        rows, winner_kw = fast_persona_scores(req, personas)

    # 3) 가중 CTR
    ctr_a, ctr_b, reasons_a, reasons_b = weighted_ctr_from_scores(rows)

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

    ctr_c = (ctr_a + ctr_b) / 2.0
    ctr_c = min(1.0, ctr_c + 0.02)
    ctr_c = calibrate_ctr(ctr_c, category)

    c_analysis = _generate_local_c_analysis_text(req, third, ctr_c, ctr_a, ctr_b)

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

# --------------------------------------------------------------------
# ✅ 사용자 선택 기록 (핵심 수정)
# --------------------------------------------------------------------
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

# --------------------------------------------------------------------
# (옵션) 인덱스 재구축
# --------------------------------------------------------------------
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
