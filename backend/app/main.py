from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import json
from pathlib import Path
from dotenv import load_dotenv  # type: ignore
from openai import OpenAI

# Load environment variables from backend/.env
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

class ImageGenerationRequest(BaseModel):
    marketing_text: str
    product_category: Optional[str] = None
    target_audience: Optional[str] = None

class ImageGenerationResponse(BaseModel):
    image_url: str
    prompt: str


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


def _build_prompt(payload: PredictRequest) -> str:
    audience = ", ".join(filter(None, [
        "/".join(payload.age_groups) if payload.age_groups else "",
        "/".join(payload.genders) if payload.genders else "",
        payload.interests or ""
    ])).strip(", ")

    prompt = f"""
한국어(해요/예요체)로만 답변해요. '합니다/하십시오'체는 절대 사용하지 마세요. 두 광고 문구 A/B의 CTR을 예측하고 이유를 설명해요. 시장지식, 명확성, 관련성, 구체성, 후킹(수치, 긴박감, 사회적 증거)을 근거로 평가해요.

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

    # Validate required keys (no hardcoded defaults)
    required_keys = ["ctr_a", "ctr_b", "analysis_a", "analysis_b", "ai_suggestion"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        raise HTTPException(status_code=502, detail=f"LLM response missing keys: {', '.join(missing)}")

    def _cleanup_text(text: str) -> str:
        s = (text or "").strip()
        # If JSON-like, try to parse and flatten to readable lines
        if s.startswith("{") or s.startswith("["):
            try:
                obj = json.loads(s)
                if isinstance(obj, dict):
                    s = "; ".join([f"{k}: {v}" for k, v in obj.items()])
                elif isinstance(obj, list):
                    s = ". ".join(map(str, obj))
            except Exception:
                pass
        # Normalize to 해요/예요체 (avoid ~합니다/하십시오체)
        lines = [ln.strip() for ln in s.split("\n") if ln.strip()]
        fixed = []
        for ln in lines:
            # common replacements from formal to 해요체
            repl = (
                ln.replace("합니다요", "해요")
                  .replace("합니다.", "해요.")
                  .replace("합니다!", "해요!")
                  .replace("합니다?", "해요?")
                  .replace("합니다", "해요")
                  .replace("하십시오요", "하세요")
                  .replace("하십시오.", "하세요.")
                  .replace("십시오.", "세요.")
                  .replace("하십시오!", "하세요!")
                  .replace("십시오!", "세요!")
                  .replace("하십시오?", "하세요?")
                  .replace("십시오?", "세요?")
                  .replace("하십시오", "하세요")
                  .replace("됩니다.", "돼요.")
                  .replace("됩니다!", "돼요!")
                  .replace("됩니다?", "돼요?")
                  .replace("됩니다", "돼요")
                  .replace("한다.", "해요.")
                  .replace("한다!", "해요!")
                  .replace("한다?", "해요?")
                  .replace("한다", "해요")
                  .replace("이다.", "예요.")
                  .replace("이다!", "예요!")
                  .replace("이다?", "예요?")
                  .replace("이다", "예요")
                  .replace("입니다.", "예요.")
                  .replace("입니다!", "예요!")
                  .replace("입니다?", "예요?")
                  .replace("입니다", "예요")
            )
            # ensure polite ending if still missing
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


@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        if not req.marketing_a and not req.marketing_b:
            raise HTTPException(status_code=400, detail="At least one of marketing_a or marketing_b must be provided")
        
        # Validate API key first
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY in environment")
        
        prompt = _build_prompt(req)
        result = _call_llm(prompt)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/api/generate-image", response_model=ImageGenerationResponse)
def generate_image(req: ImageGenerationRequest):
    try:
        # Build image generation prompt
        category_hint = f" for {req.product_category}" if req.product_category else ""
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

        # Generate image using DALL-E
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