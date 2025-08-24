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
# === RAG/팔로우 로직에 필요한 임포트/상수 ===
from dataclasses import dataclass
import numpy as np

EMBED_MODEL = "text-embedding-3-small"     # 임베딩용
LLM_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
LLM_TEMP    = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))


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

# === 페르소나 시드 ===
@dataclass
class Persona:
    id: str
    name: str
    weight: float
    categories: list[str]
    ages: list[str]       # "10s","20s","30s","40s","50s+"
    genders: list[str]    # "male","female","other"
    interests: list[str]
    notes: str = ""

PERSONAS: list[Persona] = [
    Persona("p1","운동 매니아",1.2,["sportswear","fitness","health"],["20s","30s"],["male"],["헬스","러닝","다이어트"]),
    Persona("p2","가성비 중시 직장인",1.0,["electronics","home","beauty","fashion"],["20s","30s"],["male","female"],["할인","혜택","퀵배송"]),
    Persona("p3","감성 소비자",0.9,["beauty","fashion","lifestyle"],["20s"],["female"],["인스타","감성","브랜딩"]),
    Persona("p4","실용 주부",1.1,["home","food","kids"],["30s","40s"],["female"],["가성비","편의성","안전"]),
    Persona("p5","얼리어답터",1.0,["electronics","gadgets"],["20s","30s"],["male"],["신제품","스펙","리뷰"]),
    Persona("p6","등산 마니아",1.0,["outdoor","sportswear"],["40s","50s+"],["male","female"],["등산","트레킹","방수"]),
]

# === 임베딩 & 유사도 ===
def _embed_text(text: str) -> np.ndarray:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    r = client.embeddings.create(model=EMBED_MODEL, input=text[:8000])
    return np.array(r.data[0].embedding, dtype=np.float32)

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    da, db = np.linalg.norm(a), np.linalg.norm(b)
    if da == 0 or db == 0: return 0.0
    return float(np.dot(a, b) / (da * db))

def _feature_sentence(category:str, ages:list[str], genders:list[str], interests:str, A:str, B:str)->str:
    return (f"category={category}; ages={','.join(ages or [])}; genders={','.join(genders or [])}; "
            f"interests={interests}; A={A}; B={B}")

# === 페르소나 샘플링 ===
def _overlap_ratio(a:set[str], b:set[str])->float:
    if not a or not b: return 0.0
    return len(a & b) / max(1, len(a))

def _persona_match_score(pr: "PredictRequest", ps: Persona) -> float:
    cat = 1.0 if (pr.category or "").strip().lower() in [c.lower() for c in ps.categories] else 0.0
    age = _overlap_ratio(set(map(str.lower, pr.age_groups or [])), set(map(str.lower, ps.ages)))
    gen = _overlap_ratio(set(map(str.lower, pr.genders or [])), set(map(str.lower, ps.genders)))
    ints = 0.0
    if pr.interests:
        rq = set(map(str.lower, [x.strip() for x in pr.interests.split(",") if x.strip()]))
        ints = _overlap_ratio(rq, set(map(str.lower, ps.interests)))
    return 0.4*cat + 0.25*age + 0.25*gen + 0.10*ints

def sample_personas(pr: "PredictRequest", topN: int = 5) -> list[Persona]:
    scored = [(p, _persona_match_score(pr, p)) for p in PERSONAS]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p for p,_ in scored[:topN]]

# === 페르소나 LLM 스코어링(1~5) 배치 ===
def _build_persona_scoring_prompt(pr: "PredictRequest", personas: list[Persona]) -> str:
    persona_blocks = []
    for p in personas:
        persona_blocks.append(
            f"- id:{p.id}, name:{p.name}, weight:{p.weight}, "
            f"age:{'/'.join(p.ages)}, gender:{'/'.join(p.genders)}, "
            f"interests:{'/'.join(p.interests)}, categories:{'/'.join(p.categories)}"
        )
    return f"""
당신은 페르소나 마케팅 분석가입니다.
각 페르소나 입장에서 아래 두 카피(A/B)에 대한 "클릭 의향 점수"(1~5, 정수)와 근거 키워드를 JSON으로만 반환하세요.

[입력 타겟]
- category: {pr.category}
- ages: {", ".join(pr.age_groups or [])}
- genders: {", ".join(pr.genders or [])}
- interests: {pr.interests}

[카피]
- A: {pr.marketing_a}
- B: {pr.marketing_b}

[페르소나]
{chr(10).join(persona_blocks)}

[반환 형식: STRICT JSON]
{{
  "results": [
    {{ "persona_id": "p1", "score_a": 1, "score_b": 5, "reasons": ["가성비","긴급성","신뢰"] }}
  ],
  "winner_reason_keywords": ["핵심1","핵심2","핵심3"]
}}
""".strip()

def llm_persona_scores(pr: "PredictRequest", personas: list[Persona]):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = _build_persona_scoring_prompt(pr, personas)
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=LLM_TEMP,
        messages=[
            {"role":"system","content":"You are a helpful marketing analyst. Return STRICT JSON only."},
            {"role":"user","content": prompt}
        ],
    )
    content = (resp.choices[0].message.content or "").strip()
    try:
        data = json.loads(content)
    except:
        l = content.find("{"); r = content.rfind("}")
        if l>=0 and r>l:
            data = json.loads(content[l:r+1])
        else:
            raise HTTPException(status_code=502, detail="LLM JSON parse failed")

    rows = data.get("results", [])
    kw  = data.get("winner_reason_keywords", [])
    # id → weight
    wmap = {p.id: p.weight for p in personas}
    clean = []
    for r in rows:
        pid = r.get("persona_id","")
        if pid not in wmap: 
            continue
        sa  = max(1, min(5, int(r.get("score_a", 3))))
        sb  = max(1, min(5, int(r.get("score_b", 3))))
        rs  = (r.get("reasons") or [])[:3]
        clean.append({"persona_id": pid, "w": wmap[pid], "sa": sa, "sb": sb, "reasons": rs})
    return clean, kw

def weighted_ctr_from_scores(rows: list[dict]):
    if not rows:
        return 0.5, 0.5, [], []
    wsum = sum(r["w"] for r in rows) or 1.0
    a = sum(r["w"]*r["sa"] for r in rows) / wsum
    b = sum(r["w"]*r["sb"] for r in rows) / wsum
    ctr_a = a/5.0
    ctr_b = b/5.0
    ra, rb = [], []
    for r in rows:
        if r["sa"] > r["sb"]: ra += r["reasons"]
        elif r["sb"] > r["sa"]: rb += r["reasons"]
    from collections import Counter
    top = lambda xs: [w for w,_ in Counter(xs).most_common(5)]
    return ctr_a, ctr_b, top(ra), top(rb)

# === 제3문구 생성(규칙 준수) ===
FORBIDDEN = ["무료증정","100% 환불","전액보장"]
CTA_LIST  = ["지금 바로 확인하세요","지금 시작해보세요","오늘만 혜택을 받아보세요"]

def _build_third_copy_prompt(pr: "PredictRequest", winner_keywords: list[str], winner: str) -> str:
    return f"""
아래 조건을 만족하는 한국어 마케팅 헤드라인을 1개 생성하세요. STRICT JSON으로만 반환합니다.
[목표]
- 승자 카피({winner})의 강점을 반영해 더 높은 CTR이 예상되는 문구 1개
[승자 요인 키워드]
{", ".join(winner_keywords)}
[제약]
- 최대 28자
- CTA 반드시 1개 포함(예: {", ".join(CTA_LIST)})
- 금칙어 포함 금지: {", ".join(FORBIDDEN)}
- 과장/허위 불가, 명확하고 간결하게
[반환]
{{ "text": "최종 문구" }}
""".strip()

def _violates_rules(text: str) -> bool:
    t = (text or "").strip()
    if any(bad in t for bad in FORBIDDEN): return True
    if len(t) > 28: return True
    if not any(cta in t for cta in CTA_LIST): return True
    return False

def generate_third_copy(pr: "PredictRequest", winner_keywords: list[str], winner: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=LLM_TEMP,
        messages=[
            {"role":"system","content":"Return STRICT JSON only."},
            {"role":"user","content": _build_third_copy_prompt(pr, winner_keywords, winner)}
        ],
    )
    content = (resp.choices[0].message.content or "").strip()
    try:
        data = json.loads(content)
    except:
        l = content.find("{"); r = content.rfind("}")
        data = json.loads(content[l:r+1]) if l>=0 and r>l else {"text": ""}
    text = (data.get("text") or "").strip()
    if _violates_rules(text):
        if not any(cta in text for cta in CTA_LIST):
            text = (text[:max(0, 28-len(CTA_LIST[0])-1)] + " " + CTA_LIST[0]).strip()
        text = text[:28]
        for bad in FORBIDDEN:
            text = text.replace(bad, "")
        text = text.strip()
    return text

# === CTR 캘리브레이션 (현실 범위로 매핑) ===
CALIBRATION = {
    # 카테고리별(예시) 현실 범위: 최소~최대 CTR (비율)
    "default":   {"min": 0.003, "max": 0.050, "prior_mu": 0.012},  # 0.3% ~ 5.0%, 평균 1.2%
    "sportswear":{"min": 0.004, "max": 0.050, "prior_mu": 0.015},
    "fashion":   {"min": 0.004, "max": 0.060, "prior_mu": 0.018},
    "beauty":    {"min": 0.004, "max": 0.055, "prior_mu": 0.017},
    "electronics":{"min": 0.003, "max": 0.040, "prior_mu": 0.010},
    "outdoor":   {"min": 0.003, "max": 0.045, "prior_mu": 0.012},
    "home":      {"min": 0.003, "max": 0.040, "prior_mu": 0.011},
    "food":      {"min": 0.005, "max": 0.060, "prior_mu": 0.020},
    "lifestyle": {"min": 0.004, "max": 0.050, "prior_mu": 0.015},
}

def _calib_entry(cat: Optional[str]):
    if not cat:
        return CALIBRATION["default"]
    key = (cat or "").lower().strip()
    return CALIBRATION.get(key, CALIBRATION["default"])

def calibrate_ctr(raw_score: float, category: Optional[str], shrink: float = 0.35) -> float:
    """
    raw_score: 0~1 상대 스코어
    1) 카테고리별 현실 범위 [min,max]로 선형 매핑
    2) prior 평균(prior_mu)로 shrink (가중 평균)
    """
    e = _calib_entry(category)
    s = max(0.0, min(1.0, float(raw_score)))
    mapped = e["min"] + s * (e["max"] - e["min"])
    calibrated = (1.0 - shrink) * mapped + shrink * e["prior_mu"]
    return float(max(e["min"], min(e["max"], calibrated)))

# === 과거 '최종선택' 레코드 인덱스 ===
_INDEX = []  # {log_id, vec, ts, category, ages:set, genders:set, A, B, final_text, final_class}

def _to_class(rec) -> str:
    ft = (rec.get("user_final_text") or "").strip()
    if not ft: return ""
    if ft == (rec.get("marketing_a") or ""): return "A"
    if ft == (rec.get("marketing_b") or ""): return "B"
    return "C"

def _load_jsonl(path: Path):
    if not path.exists(): return []
    out=[]
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try: out.append(json.loads(line))
            except: pass
    return out

def _rebuild_index():
    global _INDEX
    _INDEX = []
    for r in _load_jsonl(RESULTS_PATH):
        if "pred_ctr_a" not in r or "pred_ctr_b" not in r: 
            continue
        c = _to_class(r)
        if not c: 
            continue
        feat = _feature_sentence(
            r.get("category",""), r.get("age_groups",[]), r.get("genders",[]),
            r.get("interests",""), r.get("marketing_a",""), r.get("marketing_b","")
        )
        try:
            vec = _embed_text(feat)
        except Exception:
            continue
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
            "final_class": c,
        })

def _recency_weight(ts: float, alpha: float = 0.03) -> float:
    days = max(0.0, (time.time() - ts) / 86400.0)
    return 1.0 / (1.0 + alpha * days)

def _knn_follow(category:str, ages:list[str], genders:list[str], interests:str, A:str, B:str, 
                k:int=8, tau_hard:float=0.92):
    if not _INDEX:
        return {"mode":"none"}
    feat = _feature_sentence(category, ages or [], genders or [], interests or "", A or "", B or "")
    try:
        q = _embed_text(feat)
    except Exception:
        return {"mode":"none"}

    sims = []
    for item in _INDEX:
        sim = _cosine(q, item["vec"])
        sims.append((sim, item))
    sims.sort(key=lambda x: x[0], reverse=True)
    top = sims[:k]
    if not top: return {"mode":"none"}

    top1_sim, top1_item = top[0]
    if top1_sim >= tau_hard:
        return {"mode":"hard", "follow_class": top1_item["final_class"], "sim": top1_sim}

    total_w=0.0
    votes={"A":0.0,"B":0.0,"C":0.0}
    for sim, item in top:
        cat_boost = 1.15 if item["category"] == (category or "").lower().strip() else 1.0
        w = (0.7*sim + 0.3*_recency_weight(item["ts"])) * cat_boost
        votes[item["final_class"]] += w
        total_w += w
    if total_w <= 0: return {"mode":"none"}
    for k_ in votes: votes[k_] /= total_w
    return {"mode":"soft", "probs": votes, "top_sim": top1_sim}


# -----------------------------
# 환경 로드 및 앱
# -----------------------------
_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
if _ENV_PATH.exists():
    load_dotenv(dotenv_path=_ENV_PATH)

app = FastAPI(title="ab-test-backend")

# CORS for frontend (local and production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-netlify-app.netlify.app",  # 실제 배포 URL로 교체
    ],
    allow_origin_regex=r"https://.*\.netlify\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서버 기동 시 인덱스 구성(키 없으면 스킵)
try:
    _rebuild_index()
except Exception as e:
    print(f"[WARN] follow-index build skipped: {e}")


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
# LLM 프롬프트/호출 (예비; 현재 predict는 페르소나 방식 사용)
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
    # 1) 페르소나 샘플링
    personas = sample_personas(req, topN=5)

    # 2) LLM 평가(배치) → 정규화 CTR(0~1 상대 스코어)
    rows, winner_kw = llm_persona_scores(req, personas)
    ctr_a, ctr_b, reasons_a, reasons_b = weighted_ctr_from_scores(rows)

    # 3) 과거 유사 상황 팔로우(하드/소프트)로 보정
    follow = _knn_follow(
        category=req.category,
        ages=req.age_groups or [],
        genders=req.genders or [],
        interests=req.interests or "",
        A=req.marketing_a, B=req.marketing_b,
        k=8, tau_hard=0.92
    )
    if follow.get("mode") == "hard":
        if follow["follow_class"] == "A":
            ctr_a, ctr_b = max(ctr_a, 0.65), min(ctr_b, 0.35)
        elif follow["follow_class"] == "B":
            ctr_b, ctr_a = max(ctr_b, 0.65), min(ctr_a, 0.35)
        else:
            ctr_a, ctr_b = 0.45, 0.45
    elif follow.get("mode") == "soft":
        probs = follow["probs"]
        lam = 0.35
        ctr_a = (1-lam)*ctr_a + lam*probs.get("A",0.0)
        ctr_b = (1-lam)*ctr_b + lam*probs.get("B",0.0)

    # 4) 현실 CTR 범위로 캘리브레이션 (비율값)
    ctr_a = calibrate_ctr(ctr_a, req.category, shrink=0.35)
    ctr_b = calibrate_ctr(ctr_b, req.category, shrink=0.35)

    ai_top = "A" if ctr_a >= ctr_b else "B"

    # 5) 승자 요인 반영 제3문구
    third = generate_third_copy(
        req,
        winner_kw or (reasons_a if ai_top=="A" else reasons_b),
        ai_top
    )

    # 6) 분석문구(간단 요약)
    analysis_a = f"이유 키워드 상위: {', '.join(reasons_a) or '없음'}"
    analysis_b = f"이유 키워드 상위: {', '.join(reasons_b) or '없음'}"

    # 7) 저장(JSONL) 및 응답
    result = PredictResponse(
        ctr_a=float(ctr_a),
        ctr_b=float(ctr_b),
        analysis_a=analysis_a,
        analysis_b=analysis_b,
        ai_suggestion=third,
        ai_top_ctr_choice=ai_top,
        log_id=str(uuid.uuid4()),
    )
    stored = ABTestStoredResult(
        log_id=result.log_id,
        age_groups=req.age_groups or [],
        genders=req.genders or [],
        interests=req.interests or "",
        category=req.category or "",
        marketing_a=req.marketing_a,
        marketing_b=req.marketing_b,
        pred_ctr_a=float(result.ctr_a),
        pred_ctr_b=float(result.ctr_b),
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
class ImageGenerationRequest(BaseModel):
    marketing_text: str
    product_category: Optional[str] = None
    target_audience: Optional[str] = None

class ImageGenerationResponse(BaseModel):
    image_url: str
    prompt: str

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
    # 인덱스에 즉시 반영
    if ok:
        for r in _load_jsonl(RESULTS_PATH)[::-1]:  # 최근부터 탐색
            if r.get("log_id") == payload.log_id and r.get("user_final_text"):
                try:
                    vec = _embed_text(_feature_sentence(
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
