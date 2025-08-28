import os
import time
import uuid
import json
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 내부 모듈 import
from .models import (
    PredictRequest, PredictResponse, ImageGenerationRequest, 
    ImageGenerationResponse, UserChoiceIn, ABTestStoredResult
)
from .config import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE, 
    EMBED_MODEL, RESULTS_PATH, PERSONAS, CALIBRATION
)
from .utils import (
    append_jsonl, _load_jsonl, update_user_choice_inplace,
    _feature_sentence, _to_class
)
from .llm_utils import (
    _build_prompt, _build_c_analysis_prompt, _clean_llm_response,
    _parse_llm_response, _generate_local_c_analysis, 
    _generate_local_c_analysis_text
)
from .business_logic import (
    sample_personas, llm_persona_scores, weighted_ctr_from_scores,
    _knn_follow, generate_third_copy, calibrate_ctr
)
from .image_generation import (
    generate_images_with_gemini
)

# -----------------------------
# FastAPI 앱 초기화
# -----------------------------
app = FastAPI(title="A/B Test Backend", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# LangChain Gemini 초기화
# -----------------------------
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    
    # LLM 초기화
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=GEMINI_TEMPERATURE,
        google_api_key=GEMINI_API_KEY
    )
    
    # Embedding 모델 초기화
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBED_MODEL,
        google_api_key=GEMINI_API_KEY
    )
    
    print(f"✅ Gemini API Key loaded: {GEMINI_API_KEY[:20]}...")
    print(f"   Model: {GEMINI_MODEL}, Temperature: {GEMINI_TEMPERATURE}")
    print("✅ LangChain Gemini components initialized successfully")
    
except Exception as e:
    print(f"❌ LangChain Gemini 초기화 실패: {e}")
    llm = None
    embeddings = None

# -----------------------------
# 과거 '최종선택' 레코드 인덱스
# -----------------------------
_INDEX = []  # {log_id, vec, ts, category, ages:set, genders:set, A, B, final_text, final_class}

# -----------------------------
# 기본 엔드포인트
# -----------------------------
@app.get("/")
def root():
    return {"ok": True, "service": "ab-test-backend"}

# -----------------------------
# 예측 엔드포인트
# -----------------------------
@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    # 1) 페르소나 샘플링
    personas = sample_personas(req, topN=5)

    # 2) LLM 평가 → 정규화 CTR
    try:
        rows, winner_kw = llm_persona_scores(req, personas)
        ctr_a, ctr_b, reasons_a, reasons_b = weighted_ctr_from_scores(rows)
    except Exception as e:
        print(f"페르소나 평가 실패: {e}")
        ctr_a, ctr_b = 0.45, 0.55
        reasons_a, reasons_b = "기본 분석", "기본 분석"
        winner_kw = None

    # 3) 간단한 KNN 보정 (빠른 처리)
    try:
        follow = _knn_follow(
            category=req.category,
            ages=req.age_groups or [],
            genders=req.genders or [],
            interests=req.interests or "",
            A=req.marketing_a, B=req.marketing_b,
            k=5, tau_hard=0.9  # k와 임계값 줄임
        )
        if follow.get("mode") == "hard" and follow.get("follow_class") in ["A", "B"]:
            if follow["follow_class"] == "A":
                ctr_a, ctr_b = max(ctr_a, 0.6), min(ctr_b, 0.4)
            else:
                ctr_b, ctr_a = max(ctr_b, 0.6), min(ctr_a, 0.4)
    except:
        pass  # KNN 실패 시 무시하고 진행

    # 4) 현실 CTR 범위로 캘리브레이션 (비율값)
    ctr_a = calibrate_ctr(ctr_a, req.category, shrink=0.35)
    ctr_b = calibrate_ctr(ctr_b, req.category, shrink=0.35)

    # 5) 간단한 제3문구 생성
    try:
        third = generate_third_copy(req, winner_kw or "마케팅", "A" if ctr_a >= ctr_b else "B")
    except:
        third = f"AI 제안: {req.marketing_a}와 {req.marketing_b}의 장점을 결합한 새로운 접근"

    # 6) C안의 CTR 예측 (승자 요인을 반영하여 높은 CTR 예상)
    ctr_c = max(ctr_a, ctr_b) * 1.1  # 승자보다 10% 높게 예측
    ctr_c = min(ctr_c, 0.95)  # 최대 95%로 제한
    ctr_c = calibrate_ctr(ctr_c, req.category, shrink=0.35)

    # 7) 최고 CTR 결정
    if ctr_c >= max(ctr_a, ctr_b):
        ai_top = "C"
    elif ctr_a >= ctr_b:
        ai_top = "A"
    else:
        ai_top = "B"

    # 8) LLM 상세분석 생성 (빠른 처리)
    detailed_analysis = None
    if llm:
        try:
            prompt = _build_prompt(req)
            response = llm.invoke(prompt)
            data = json.loads(_clean_llm_response(response.content))
            detailed_analysis = PredictResponse(
                ctr_a=float(data["ctr_a"]), ctr_b=float(data["ctr_b"]), ctr_c=0.0,
                analysis_a=data["analysis_a"], analysis_b=data["analysis_b"], analysis_c="",
                ai_suggestion=data["ai_suggestion"]
            )
        except:
            detailed_analysis = None
    
    # 9) C안 분석 생성 (빠른 처리)
    c_analysis = ""
    if llm:
        try:
            prompt = _build_c_analysis_prompt(req, third)
            response = llm.invoke(prompt)
            data = json.loads(_clean_llm_response(response.content))
            c_analysis = data.get('analysis_c', '')
        except:
            c_analysis = _generate_local_c_analysis_text(req, third, ctr_c, ctr_a, ctr_b)
    else:
        c_analysis = _generate_local_c_analysis_text(req, third, ctr_c, ctr_a, ctr_b)
    
    # 11) 저장(JSONL) 및 응답
    # detailed_analysis가 None인 경우 기본값 사용
    if detailed_analysis is None:
        analysis_a = "기본 분석: 마케팅 문구의 효과를 평가하기 위해 추가 분석이 필요합니다."
        analysis_b = "기본 분석: 마케팅 문구의 효과를 평가하기 위해 추가 분석이 필요합니다."
    else:
        analysis_a = detailed_analysis.analysis_a
        analysis_b = detailed_analysis.analysis_b
    
    result = PredictResponse(
        ctr_a=float(ctr_a),
        ctr_b=float(ctr_b),
        ctr_c=float(ctr_c),
        analysis_a=analysis_a,
        analysis_b=analysis_b,
        analysis_c=c_analysis,
        ai_suggestion=third,
        ai_top_ctr_choice=ai_top,
        log_id=str(uuid.uuid4()),
    )
    stored = ABTestStoredResult(
        log_id=result.log_id,
        timestamp=time.time(),
        age_groups=req.age_groups or [],
        genders=req.genders or [],
        interests=req.interests or "",
        category=req.category or "",
        marketing_a=req.marketing_a,
        marketing_b=req.marketing_b,
        pred_ctr_a=float(result.ctr_a),
        pred_ctr_b=float(result.ctr_b),
        pred_ctr_c=float(result.ctr_c),
        ai_generated_text=result.ai_suggestion,
        ai_top_ctr_choice=ai_top,
        user_final_text=None,
    )
    row = stored.model_dump() if hasattr(stored,"model_dump") else stored.dict()
    append_jsonl(RESULTS_PATH, row)
    return result

# -----------------------------
# 이미지 생성
# -----------------------------
@app.post("/api/generate-images", response_model=ImageGenerationResponse)
def generate_images(req: ImageGenerationRequest):
    # Gemini 2.5 Flash Image Preview 모델을 사용하여 이미지 생성
    return generate_images_with_gemini(req)

# -----------------------------
# 사용자 최종 선택 기록 (인플레이스 업데이트)
# -----------------------------
@app.post("/api/log-user-choice")
def log_user_choice(payload: UserChoiceIn):
    ok = update_user_choice_inplace(payload.log_id, payload.user_final_text)

    # 혹시 원본 레코드를 못 찾으면 이벤트 라인으로라도 남겨 둠
    if not ok:
        append_jsonl(RESULTS_PATH, {
            "type": "user_choice_update",
            "log_id": payload.log_id,
            "timestamp": time.time(),
            "user_final_text": payload.user_final_text,
        })
    # 인덱스에 즉시 반영
    if ok:
        for r in _load_jsonl(RESULTS_PATH)[::-1]:  # 최근부터 탐색
            if r.get("log_id") == payload.log_id and r.get("user_final_text"):
                try:
                    vec = embeddings.embed_query(_feature_sentence(
                        r.get("category",""), r.get("age_groups",[]), r.get("genders",[]),
                        r.get("interests",""), r.get("marketing_a",""), r.get("marketing_b","")
                    ))
                except Exception:
                    vec = None
                if vec is not None:
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
                break

    return {"ok": True, "updated_inline": ok}
