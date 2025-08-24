from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
from pathlib import Path
from dotenv import load_dotenv  # type: ignore
from openai import OpenAI
import uuid, time

# -----------------------------
# 저장 경로/유틸
# -----------------------------
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_PATH = DATA_DIR / "abtest_results.jsonl"

def append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def update_user_choice_inplace(log_id: str, user_final_text: str) -> bool:
    """
    JSONL에서 해당 log_id의 '본 레코드(예측 레코드)'만 찾아 user_final_text를 갱신.
    - 기존에 append해둔 user_choice_update 이벤트 라인은 정리(삭제).
    - 대상이 없으면 False.
    """
    src = RESULTS_PATH
    tmp = RESULTS_PATH.with_suffix(".jsonl.tmp")

    if not src.exists():
        return False

    updated = False
    with src.open("r", encoding="utf-8") as fin, tmp.open("w", encoding="utf-8") as fout:
        for line in fin:
            try:
                obj = json.loads(line)
            except Exception:
                # 깨진 라인은 유지
                fout.write(line)
                continue

            # 과거 이벤트 라인은 정리
            if obj.get("type") == "user_choice_update" and obj.get("log_id") == log_id:
                continue

            # 본 레코드: log_id 일치 + 예측 필드 존재
            if (not updated) and obj.get("log_id") == log_id and "pred_ctr_a" in obj and "pred_ctr_b" in obj:
                obj["user_final_text"] = user_final_text
                updated = True

            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")

    os.replace(tmp, src)
    return updated

# -----------------------------
# 저장 레코드 스키마
# -----------------------------
class ABTestStoredResult(BaseModel):
    # 운영 편의
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=lambda: time.time())

    # 세그먼트/입력
    age_groups: List[str] = []
    genders: List[str] = []
    interests: str
    category: str
    marketing_a: str
    marketing_b: str

    # 예측값
    pred_ctr_a: float
    pred_ctr_b: float

    # AI 산출물
    ai_generated_text: str       # 제3의 문구(= AI가 새로 만든 카피)
    ai_top_ctr_choice: str       # "A" or "B" (A/B 중 더 높은 예측)

    # 사용자 최종 선택(예측 시점엔 None)
    user_final_text: Optional[str] = None

# -----------------------------
# 환경 로드 및 앱
# -----------------------------
_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
if _ENV_PATH.exists():
    load_dotenv(dotenv_path=_ENV_PATH)

app = FastAPI(title="ab-test-backend")

# CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# 스키마
# -----------------------------
class PredictRequest(BaseModel):
    age_groups: List[str] = Field(default_factory=list)
    genders: List[str] = Field(default_factory=list)
    interests: Optional[str] = None
    category: Optional[str] = None
    marketing_a: str = Field("", description="Text for option A")
    marketing_b: str = Field("", description="Text for option B")

class PredictResponse(BaseModel):
    ctr_a: float
    ctr_b: float
    analysis_a: str
    analysis_b: str
    ai_suggestion: str
    # 응답 보강 필드
    ai_top_ctr_choice: Optional[str] = None
    log_id: Optional[str] = None

class ImageGenerationRequest(BaseModel):
    marketing_text: str
    product_category: Optional[str] = None
    target_audience: Optional[str] = None

class ImageGenerationResponse(BaseModel):
    image_url: str
    prompt: str

# -----------------------------
# 기본 라우트/헬스체크
# -----------------------------
@app.get("/")
def root():
    return {"ok": True, "service": "ab-test-backend"}

@app.get("/api/health")
def health():
    return {"ok": True, "service": "ab-test-backend"}

@app.get("/api/test-openai")
def test_openai():
    try:
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            return {"ok": False, "error": "Missing OPENAI_API_KEY"}
        
        client = OpenAI(api_key=api_key)
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        return {"ok": True, "openai_working": True, "response": response.choices[0].message.content}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# -----------------------------
# LLM 프롬프트/호출
# -----------------------------
def _build_prompt(payload: PredictRequest) -> str:
    audience = ", ".join(filter(None, [
        "/".join(payload.age_groups) if payload.age_groups else "",
        "/".join(payload.genders) if payload.genders else "",
        payload.interests or ""
    ])).strip(", ")

    prompt = f"""
한국어(해요/예요체)로만 답변해요. '합니다/십시오'체는 절대 사용하지 마세요. 두 광고 문구 A/B의 CTR을 예측하고 이유를 설명해요. 시장지식, 명확성, 관련성, 구체성, 후킹(수치, 긴박감, 사회적 증거)을 근거로 평가해요.

타겟: {audience or 'N/A'}
제품/카테고리: {payload.category or 'N/A'}

옵션 A: {payload.marketing_a}
옵션 B: {payload.marketing_b}

반드시 다음 키를 가진 JSON만 출력해요: ctr_a, ctr_b, analysis_a, analysis_b, ai_suggestion.
규칙:
- ctr_a/ctr_b는 0~1 사이 실수예요 (예: 0.123은 12.3%).
- analysis_a/analysis_b는 문장형 한국어 텍스트예요. JSON/코드/마크다운 금지.
- ai_suggestion은 이 타겟에 맞춘 한 줄 문구예요.
""".strip()
    return prompt

def _call_llm(prompt: str) -> PredictResponse:
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY in environment")

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

    client = OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful marketing analyst. Return STRICT JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {exc}")
    content = (resp.choices[0].message.content or "").strip()

    try:
        data = json.loads(content)
    except Exception as exc:
        # Try to extract JSON substring if the model added prose
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != -1:
                data = json.loads(content[start:end])
            else:
                raise
        except Exception:
            raise HTTPException(status_code=502, detail=f"LLM parsing failed: {exc}")

    # Validate required keys
    required_keys = ["ctr_a", "ctr_b", "analysis_a", "analysis_b", "ai_suggestion"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise HTTPException(status_code=502, detail=f"LLM response missing keys: {', '.join(missing)}")

    def _cleanup_text(text: str) -> str:
        s = (text or "").strip()
        # Flatten JSON-y text
        if s.startswith("{") or s.startswith("["):
            try:
                obj = json.loads(s)
                if isinstance(obj, dict):
                    s = "; ".join([f"{k}: {v}" for k, v in obj.items()])
                elif isinstance(obj, list):
                    s = ". ".join(map(str, obj))
            except Exception:
                pass
        # Normalize to 해요/예요체
        lines = [ln.strip() for ln in s.split("\n") if ln.strip()]
        fixed = []
        for ln in lines:
            repl = (
                ln.replace("합니다요", "해요")
                  .replace("합니다.", "해요.")
                  .replace("합니다!", "해요!")
                  .replace("합니다?", "해요?")
                  .replace("합니다", "해요")
                  .replace("십시오", "세요")
                  .replace("하십시오", "하세요")
                  .replace("됩니다", "돼요")
                  .replace("한다", "해요")
                  .replace("이다", "예요")
                  .replace("입니다", "예요")
            )
            # 기본 존댓말 보정
            if repl.endswith(("요", "요.", "요!", "요?", "세요", "세요.", "세요!", "세요?", "예요", "예요.", "예요!", "예요?")):
                fixed.append(repl)
            else:
                punct = ""
                if repl.endswith((".", "!", "?")):
                    punct = repl[-1]
                    repl = repl[:-1]
                fixed.append(repl + "요" + punct)
        return "\n".join(fixed)

    try:
        return PredictResponse(
            ctr_a=float(data["ctr_a"]),
            ctr_b=float(data["ctr_b"]),
            analysis_a=_cleanup_text(str(data["analysis_a"])),
            analysis_b=_cleanup_text(str(data["analysis_b"])),
            ai_suggestion=_cleanup_text(str(data["ai_suggestion"])),
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM response type error: {exc}")

# -----------------------------
# 예측 엔드포인트
# -----------------------------
@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        if not req.marketing_a and not req.marketing_b:
            raise HTTPException(status_code=400, detail="At least one of marketing_a or marketing_b must be provided")
        
        # Validate API key first
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY in environment")
        
        # 1) 프롬프트 생성 & LLM 호출
        prompt = _build_prompt(req)
        result = _call_llm(prompt)   # PredictResponse 객체

        # 2) A/B 중 더 높은 예측 CTR
        ai_top_ctr_choice = "A" if float(result.ctr_a) >= float(result.ctr_b) else "B"

        # 3) JSONL 한 줄 저장 (None 방어)
        stored = ABTestStoredResult(
            age_groups=req.age_groups,
            genders=req.genders,
            interests=(req.interests or ""),
            category=(req.category or ""),
            marketing_a=req.marketing_a,
            marketing_b=req.marketing_b,
            pred_ctr_a=float(result.ctr_a),
            pred_ctr_b=float(result.ctr_b),
            ai_generated_text=result.ai_suggestion,  # 제3의 문구
            ai_top_ctr_choice=ai_top_ctr_choice,
            user_final_text=None,
        )
        row = stored.model_dump() if hasattr(stored, "model_dump") else stored.dict()
        append_jsonl(RESULTS_PATH, row)

        # 4) 응답 보강 후 반환
        result.ai_top_ctr_choice = ai_top_ctr_choice
        result.log_id = stored.log_id
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# -----------------------------
# 이미지 생성
# -----------------------------
@app.post("/api/generate-image", response_model=ImageGenerationResponse)
def generate_image(req: ImageGenerationRequest):
    try:
        audience_hint = f" targeting {req.target_audience}" if req.target_audience else ""
        image_prompt = f"""
Create a modern, professional advertisement visual for a {req.product_category or 'product'} campaign{audience_hint}. 
The design should feature the headline text: "{req.marketing_text}"

Style requirements:
- Clean, modern layout with high legibility
- Professional typography and composition
- Suitable for digital advertising (social media, display ads)
- Brand-friendly and visually appealing
- Korean text should be clearly readable
- Use a color palette that works well with the product category

The image should be suitable for marketing materials and maintain visual hierarchy with the headline as the focal point.
""".strip()

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        return ImageGenerationResponse(
            image_url=response.data[0].url,
            prompt=image_prompt
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# -----------------------------
# 사용자 최종 선택 기록 (인플레이스 업데이트)
# -----------------------------
class UserChoiceIn(BaseModel):
    log_id: str
    user_final_text: str  # 사용자가 고른 실제 텍스트(A/B/제3 무엇이든 문자열)

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
    return {"ok": True, "updated_inline": ok}
