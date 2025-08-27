from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import json
from pathlib import Path
from dotenv import load_dotenv  # type: ignore
import uuid
import time

# === LangChain 관련 임포트 ===
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import BaseOutputParser, StrOutputParser
from langchain.chains import LLMChain, SequentialChain
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import BaseTool
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema.messages import AIMessage, HumanMessage

# Google Generative AI 클라이언트 (이미지 생성용)
import google.generativeai as genai

# === 데이터 처리 및 유틸리티 ===
from dataclasses import dataclass
import numpy as np
from collections import Counter

# 환경 변수 로드 확인
load_dotenv()

# LangChain 설정
LLM_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # 빠르고 효율적인 모델
LLM_TEMP = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
EMBED_MODEL = "models/embedding-001"  # 올바른 Gemini embedding 모델명

# Gemini API 키 확인
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables!")
    print("   Please set GEMINI_API_KEY in your .env file or environment")
else:
    print(f"✅ Gemini API Key loaded: {GEMINI_API_KEY[:8]}...")
    print(f"   Model: {LLM_MODEL}, Temperature: {LLM_TEMP}")

# LangChain LLM 및 Embeddings 초기화
try:
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        temperature=LLM_TEMP,
        google_api_key=GEMINI_API_KEY
    )
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBED_MODEL,
        google_api_key=GEMINI_API_KEY
    )
    
    # Google Generative AI 클라이언트 초기화
    genai.configure(api_key=GEMINI_API_KEY)
    
    print("✅ LangChain Gemini components initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize LangChain Gemini components: {e}")
    llm = None
    embeddings = None


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
    pred_ctr_c: float

    # AI 산출물
    ai_generated_text: str       # 제3의 문구(= AI가 새로 만든 카피)
    ai_top_ctr_choice: str       # "A", "B", or "C" (가장 높은 예측)

    # 사용자 최종 선택(예측 시점엔 None)
    user_final_text: Optional[str] = None

# === LangChain 프롬프트 템플릿 정의 ===
PERSONA_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """당신은 30년 경력의 페르소나 마케팅 분석가입니다. 
각 페르소나 입장에서 마케팅 문구에 대한 심도 깊은 분석을 제공하되, 
각 분석 내용을 300자 이상의 상세한 보고서 형태로 작성해주세요.

STRICT JSON 형식으로만 반환해주세요."""),
    ("human", """[입력 타겟]
- category: {category}
- ages: {ages}
- genders: {genders}
- interests: {interests}

[카피]
- A: {marketing_a}
- B: {marketing_b}

[페르소나]
{personas}

[반환 형식: STRICT JSON with detailed analysis]
{{
  "results": [
    {{
      "persona_id": "p1",
      "score_a": 1,
      "score_b": 5,
      "detailed_analysis": {{
        "a_analysis": "A안에 대한 300자 이상의 상세한 분석 내용. 페르소나 특성과의 연관성, 클릭 의향에 미치는 요소들을 구체적으로 설명해요.",
        "b_analysis": "B안에 대한 300자 이상의 상세한 분석 내용. 페르소나 특성과의 연관성, 클릭 의향에 미치는 요소들을 구체적으로 설명해요.",
        "overall_evaluation": "전체적인 마케팅 효과와 개선 방향, 페르소나별 맞춤 전략에 대한 300자 이상의 종합 평가를 제공해요."
      }},
      "reasons": ["핵심요인1", "핵심요인2", "핵심요인3"]
    }}
  ],
  "winner_reason_keywords": ["키워드1", "키워드2", "키워드3"]
}}

각 분석 항목을 300자 이상의 심도 깊은 내용으로 작성해주세요. 모든 문장은 반드시 '-요'로 끝나야 해요.""")
])

COPY_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """당신은 30년 경력의 마케팅 분석가입니다. 
두 광고 문구 A/B의 CTR을 예측하고 각각에 대해 300자 이상의 심도 깊은 분석을 제공해요. 
시장지식, 명확성, 관련성, 구체성, 후킹(수치, 긴박감, 사회적 증거)을 근거로 평가해요.

한국어로 답변하되, 모든 문장을 '-요'로 끝나게 작성해요."""),
    ("human", """타겟: {audience}
제품/카테고리: {category}

A안: {marketing_a}
B안: {marketing_b}

반드시 다음 키를 가진 JSON만 출력해요: ctr_a, ctr_b, analysis_a, analysis_b, ai_suggestion.
규칙:
- ctr_a/ctr_b는 0~1 사이 실수예요 (예: 0.123은 12.3%).
- analysis_a/analysis_b는 각각 300자 이상의 심도 깊은 분석이 포함된 문장형 한국어 텍스트예요.
- ai_suggestion은 이 타겟에 맞춘 한 줄 문구예요.
- 모든 문장은 반드시 '-요'로 끝나야 해요.

각 분석은 다음 요소들을 포함하여 300자 이상으로 작성해주세요:
- 마케팅 문구의 강점과 약점 분석
- 타겟 오디언스와의 연관성 평가
- CTR 예측에 영향을 미치는 핵심 요소 분석
- 개선 방향과 최적화 전략 제시""")
])

THIRD_COPY_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """당신은 30년 경력의 마케팅 카피라이터이자 분석가입니다. 
아래 조건을 만족하는 한국어 마케팅 헤드라인을 1개 생성하되, 
생성 과정과 근거를 300자 이상의 상세한 분석과 함께 제공해주세요. 
STRICT JSON으로만 반환합니다. 모든 문장은 반드시 '-요'로 끝나야 해요."""),
    ("human", """[목표]
- 승자 카피({winner})의 강점을 반영해 더 높은 CTR이 예상되는 문구 1개

[승자 요인 키워드]
{winner_keywords}

[제약]
- 35자에서 45자 사이
- CTA 반드시 1개 포함(예: {cta_examples})
- 금칙어 포함 금지: {forbidden_words}
- 과장/허위 불가, 명확하면서 창의성있게

[반환 형식]
{{
  "text": "최종 문구",
  "detailed_analysis": {{
    "creation_process": "300자 이상의 문구 생성 과정과 전략적 사고 과정을 상세히 설명해요.",
    "winner_integration": "300자 이상의 승자 카피 강점 통합 방법과 효과 분석을 제공해요.",
    "ctr_optimization": "300자 이상의 CTR 향상을 위한 핵심 요소와 개선 방향 분석을 제시해요.",
    "target_audience_consideration": "300자 이상의 타겟 오디언스 특성을 반영한 문구 설계 근거를 설명해요."
  }}
}}

각 분석 항목을 300자 이상의 심도 깊은 내용으로 작성해주세요. 모든 문장은 반드시 '-요'로 끝나야 해요.""")
])

C_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", """당신은 30년 경력의 마케팅 분석가입니다. 
AI가 생성한 마케팅 문구에 대해 300자 이상의 심도 깊은 분석을 제공해요.

한국어로 답변하되, 모든 문장을 '-요'로 끝나게 작성해요."""),
    ("human", """타겟: {audience}
제품/카테고리: {category}

AI 생성 문구: {ai_text}

다음 요소들을 포함하여 300자 이상으로 작성해주세요:
- AI 생성 문구의 강점과 차별화 요소 분석
- A안, B안 대비 개선된 점과 우수성 평가
- 타겟 오디언스와의 연관성 및 매력도 분석
- CTR 예측이 높은 이유와 핵심 성공 요인 분석
- 실제 마케팅에서의 활용 가능성과 효과성 평가

JSON 형식으로 analysis_c 키에 분석 내용을 담아주세요.""")
])

# === 페르소나 시드 ===
@dataclass
class Persona:
    id: str
    name: str
    weight: float
    categories: list[str]
    ages: list[str]       # "10s","20s","30s","40s","50s"
    genders: list[str]    # "male","female"
    interests: list[str]
    notes: str = ""

PERSONAS: list[Persona] = [
    Persona("p1","뷰티/화장품",1.2,["beauty","cosmetics","skincare"],["20s"],["female"],["생활","노하우","쇼핑"]),
    Persona("p2","게임",1.0,["gaming","electronics","entertainment"],["20s"],["male"],["취미","여가","여행"]),
    Persona("p3","패션/잡화",0.9,["fashion","accessories","lifestyle"],["30s"],["female"],["생활","노하우","쇼핑"]),
    Persona("p4","부동산/재테크",1.1,["real_estate","investment","finance"],["30s"],["male"],["지식", "동향"]),
    Persona("p5","여행/숙박/항공",1.0,["travel","accommodation","aviation"],["40s"],["female"],["취미","여가","여행"]),
    Persona("p6","스포츠/레저",1.0,["sports","outdoor","leisure"],["40s"],["male"],["취미","여가","여행"]),
    Persona("p7","식음료/요리",1.0,["food","beverage","cooking"],["50s"],["female"],["생활","노하우","쇼핑"]),
    Persona("p8","정치/사회",1.0,["politics","social_issues","news"],["50s"],["male"],["지식", "동향"]),
]

# === LangChain 기반 임베딩 & 유사도 ===
def _embed_text(text: str) -> np.ndarray:
    if not embeddings:
        raise Exception("LangChain embeddings not initialized")
    try:
        embedding = embeddings.embed_query(text[:8000])
        return np.array(embedding, dtype=np.float32)
    except Exception as e:
        print(f"Embedding failed: {e}")
        # Fallback: 간단한 해시 기반 벡터 생성
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        return np.array([int(hash_obj.hexdigest()[:8], 16) % 1000 / 1000.0 for _ in range(1536)], dtype=np.float32)

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
너는 30년 경력의 페르소나 마케팅 분석가야.
각 페르소나 입장에서 아래 두 카피(A/B)에 대한 심도 깊은 분석을 JSON 형식으로 반환하되, 각 분석 내용을 300자 이상의 상세한 보고서 형태로 작성해주세요.

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

[반환 형식: STRICT JSON with detailed analysis]
{{
  "results": [
    {{
      "persona_id": "p1",
      "score_a": 1,
      "score_b": 5,
      "detailed_analysis": {{
        "a_analysis": "A안에 대한 300자 이상의 상세한 분석 내용. 페르소나 특성과의 연관성, 클릭 의향에 미치는 요소들을 구체적으로 설명해요.",
        "b_analysis": "B안에 대한 300자 이상의 상세한 분석 내용. 페르소나 특성과의 연관성, 클릭 의향에 미치는 요소들을 구체적으로 설명해요.",
        "overall_evaluation": "전체적인 마케팅 효과와 개선 방향, 페르소나별 맞춤 전략에 대한 300자 이상의 종합 평가를 제공해요."
      }},
      "reasons": ["핵심요인1", "핵심요인2", "핵심요인3"]
    }}
  ],
  "winner_reason_keywords": ["핵심1", "핵심2", "핵심3"]
}}

각 페르소나별로 detailed_analysis의 각 항목을 300자 이상의 심도 깊은 내용으로 작성해주세요. 모든 문장은 반드시 '-요'로 끝나야 해요.
""".strip()

def llm_persona_scores(pr: "PredictRequest", personas: list[Persona]) -> tuple[list[dict], list[str]]:
    if not llm:
        raise Exception("LangChain LLM not initialized")
    
    try:
        # 페르소나 정보를 문자열로 변환
        persona_blocks = []
        for p in personas:
            persona_blocks.append(
                f"- id:{p.id}, name:{p.name}, weight:{p.weight}, "
                f"age:{'/'.join(p.ages)}, gender:{'/'.join(p.genders)}, "
                f"interests:{'/'.join(p.interests)}, categories:{'/'.join(p.categories)}"
            )
        
        # LangChain 체인 실행
        chain = PERSONA_ANALYSIS_TEMPLATE | llm | StrOutputParser()
        
        result = chain.invoke({
            "category": pr.category or "",
            "ages": ", ".join(pr.age_groups or []),
            "genders": ", ".join(pr.genders or []),
            "interests": pr.interests or "",
            "marketing_a": pr.marketing_a,
            "marketing_b": pr.marketing_b,
            "personas": "\n".join(persona_blocks)
        })
        
        # JSON 파싱
        try:
            data = json.loads(result)
        except:
            l = result.find("{"); r = result.rfind("}")
            if l >= 0 and r > l:
                data = json.loads(result[l:r+1])
            else:
                raise Exception("LLM JSON parse failed")
        
        rows = data.get("results", [])
        kw = data.get("winner_reason_keywords", [])
        
        # id → weight 매핑
        wmap = {p.id: p.weight for p in personas}
        clean = []
        
        for r in rows:
            pid = r.get("persona_id", "")
            if pid not in wmap: 
                continue
            sa = max(1, min(5, int(r.get("score_a", 3))))
            sb = max(1, min(5, int(r.get("score_b", 3))))
            rs = (r.get("reasons") or [])[:3]
            clean.append({"persona_id": pid, "w": wmap[pid], "sa": sa, "sb": sb, "reasons": rs})
        
        return clean, kw
        
    except Exception as e:
        print(f"LangChain persona scoring failed: {e}")
        raise

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
아래 조건을 만족하는 한국어 마케팅 헤드라인을 1개 생성하되, 생성 과정과 근거를 300자 이상의 상세한 분석과 함께 제공해주세요. STRICT JSON으로만 반환합니다. 모든 문장은 반드시 '-요'로 끝나야 해요.

[목표]
- 승자 카피({winner})의 강점을 반영해 더 높은 CTR이 예상되는 문구 1개

[승자 요인 키워드]
{", ".join(winner_keywords)}

[제약]
- 35자에서 45자 사이
- CTA 반드시 1개 포함(예: {", ".join(CTA_LIST)})
- 금칙어 포함 금지: {", ".join(FORBIDDEN)}
- 과장/허위 불가, 명확하면서 창의성있게

[반환 형식]
{{
  "text": "최종 문구",
  "detailed_analysis": {{
    "creation_process": "300자 이상의 문구 생성 과정과 전략적 사고 과정을 상세히 설명해요.",
    "winner_integration": "300자 이상의 승자 카피 강점 통합 방법과 효과 분석을 제공해요.",
    "ctr_optimization": "300자 이상의 CTR 향상을 위한 핵심 요소와 개선 방향 분석을 제시해요.",
    "target_audience_consideration": "300자 이상의 타겟 오디언스 특성을 반영한 문구 설계 근거를 설명해요."
  }}
}}

각 분석 항목을 300자 이상의 심도 깊은 내용으로 작성해주세요. 모든 문장은 반드시 '-요'로 끝나야 해요.
""".strip()

def _violates_rules(text: str) -> bool:
    t = (text or "").strip()
    if any(bad in t for bad in FORBIDDEN): return True
    if len(t) > 28: return True
    if not any(cta in t for cta in CTA_LIST): return True
    return False

def generate_third_copy(pr: "PredictRequest", winner_keywords: list[str], winner: str) -> str:
    if not llm:
        raise Exception("LangChain LLM not initialized")
    
    try:
        # LangChain 체인 실행
        chain = THIRD_COPY_TEMPLATE | llm | StrOutputParser()
        
        result = chain.invoke({
            "winner": winner,
            "winner_keywords": ", ".join(winner_keywords),
            "cta_examples": ", ".join(CTA_LIST),
            "forbidden_words": ", ".join(FORBIDDEN)
        })
        
        # JSON 파싱
        try:
            data = json.loads(result)
        except:
            l = result.find("{"); r = result.rfind("}")
            data = json.loads(result[l:r+1]) if l >= 0 and r > l else {"text": ""}
        
        text = (data.get("text") or "").strip()
        
        # 규칙 검증 및 수정
        if _violates_rules(text):
            if not any(cta in text for cta in CTA_LIST):
                text = (text[:max(0, 28-len(CTA_LIST[0])-1)] + " " + CTA_LIST[0]).strip()
            text = text[:28]
            for bad in FORBIDDEN:
                text = text.replace(bad, "")
            text = text.strip()
        
        return text
        
    except Exception as e:
        print(f"LangChain third copy generation failed: {e}")
        # Fallback: 기본 문구 생성
        return f"AI가 생성한 마케팅 문구: {pr.marketing_a}와 {pr.marketing_b}의 장점을 결합한 새로운 접근"

# === CTR 캘리브레이션 (현실 범위로 매핑) ===
CALIBRATION = {
    # 카테고리별(예시) 현실 범위: 최소~최대 CTR (비율)
    "default":   {"min": 0.003, "max": 0.050, "prior_mu": 0.012},  # 0.3% ~ 5.0%, 평균 1.2%
    
    # PERSONAS 기반 카테고리별 CTR 범위
    "beauty":    {"min": 0.004, "max": 0.055, "prior_mu": 0.017},  # 뷰티/화장품
    "cosmetics": {"min": 0.004, "max": 0.055, "prior_mu": 0.017},  # 뷰티/화장품
    "skincare":  {"min": 0.004, "max": 0.055, "prior_mu": 0.017},  # 뷰티/화장품
    
    "gaming":    {"min": 0.003, "max": 0.040, "prior_mu": 0.010},  # 게임
    "electronics":{"min": 0.003, "max": 0.040, "prior_mu": 0.010},  # 게임
    "entertainment":{"min": 0.003, "max": 0.040, "prior_mu": 0.010}, # 게임
    
    "fashion":   {"min": 0.004, "max": 0.060, "prior_mu": 0.018},  # 패션/잡화
    "accessories":{"min": 0.004, "max": 0.060, "prior_mu": 0.018},  # 패션/잡화
    "lifestyle": {"min": 0.004, "max": 0.050, "prior_mu": 0.015},  # 패션/잡화
    
    "real_estate":{"min": 0.002, "max": 0.030, "prior_mu": 0.008}, # 부동산/재테크
    "investment": {"min": 0.002, "max": 0.030, "prior_mu": 0.008}, # 부동산/재테크
    "finance":   {"min": 0.002, "max": 0.030, "prior_mu": 0.008},  # 부동산/재테크
    
    "travel":    {"min": 0.005, "max": 0.065, "prior_mu": 0.022},  # 여행/숙박/항공
    "accommodation":{"min": 0.005, "max": 0.065, "prior_mu": 0.022}, # 여행/숙박/항공
    "aviation": {"min": 0.005, "max": 0.065, "prior_mu": 0.022},  # 여행/숙박/항공
    
    "sports":    {"min": 0.003, "max": 0.045, "prior_mu": 0.012},  # 스포츠/레저
    "outdoor":   {"min": 0.003, "max": 0.045, "prior_mu": 0.012},  # 스포츠/레저
    "leisure":   {"min": 0.003, "max": 0.045, "prior_mu": 0.012},  # 스포츠/레저
    
    "food":      {"min": 0.005, "max": 0.060, "prior_mu": 0.020},  # 식음료/요리
    "beverage":  {"min": 0.005, "max": 0.060, "prior_mu": 0.020},  # 식음료/요리
    "cooking":   {"min": 0.005, "max": 0.060, "prior_mu": 0.020},  # 식음료/요리
    
    "politics":  {"min": 0.001, "max": 0.020, "prior_mu": 0.005},  # 정치/사회
    "social_issues":{"min": 0.001, "max": 0.020, "prior_mu": 0.005}, # 정치/사회
    "news":      {"min": 0.001, "max": 0.020, "prior_mu": 0.005},  # 정치/사회
    
    # 기존 카테고리들 (호환성 유지)
    "sportswear":{"min": 0.004, "max": 0.050, "prior_mu": 0.015},
    "home":      {"min": 0.003, "max": 0.040, "prior_mu": 0.011},
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

# === LangChain 에이전트 시스템 ===
class MarketingAnalysisTool(BaseTool):
    name: str = "marketing_analysis"
    description: str = "마케팅 문구의 CTR을 예측하고 상세 분석을 제공합니다"
    
    def _run(self, marketing_a: str, marketing_b: str, category: str, target_info: str) -> str:
        """마케팅 분석 도구 실행"""
        try:
            # 간단한 키워드 기반 분석
            keywords_a = set(marketing_a.lower().split())
            keywords_b = set(marketing_b.lower().split())
            
            # 카테고리 관련 키워드 가중치
            category_keywords = {
                "beauty": ["뷰티", "화장품", "스킨케어", "미용"],
                "fashion": ["패션", "의류", "스타일", "트렌드"],
                "electronics": ["전자", "기술", "디지털", "스마트"],
                "food": ["음식", "맛", "요리", "식사"]
            }
            
            cat_keywords = category_keywords.get(category.lower(), [])
            
            # 간단한 점수 계산
            score_a = sum(1 for word in keywords_a if word in cat_keywords)
            score_b = sum(1 for word in keywords_b if word in cat_keywords)
            
            return f"A안 점수: {score_a}, B안 점수: {score_b}, 카테고리: {category}"
            
        except Exception as e:
            return f"분석 실패: {str(e)}"

# 마케팅 분석 에이전트 생성
def create_marketing_agent():
    """마케팅 분석을 위한 LangChain 에이전트 생성"""
    if not llm:
        return None
    
    tools = [MarketingAnalysisTool()]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 전문적인 마케팅 분석가입니다. 
사용자의 요청에 따라 마케팅 문구를 분석하고 최적화 방안을 제시해주세요.

사용 가능한 도구: {tools}
도구 이름: {tool_names}"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_structured_chat_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor

# 에이전트 인스턴스 생성
marketing_agent = create_marketing_agent()

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

# CORS for frontend (local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://localhost:8080",
    ],
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
    ctr_c: float
    analysis_a: str
    analysis_b: str
    analysis_c: str
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



@app.get("/api/debug-env")
def debug_environment():
    """환경 변수 디버깅을 위한 엔드포인트"""
    return {
        "gemini_api_key_exists": bool(os.getenv("GEMINI_API_KEY")),
        "gemini_api_key_prefix": os.getenv("GEMINI_API_KEY", "")[:8] + "..." if os.getenv("GEMINI_API_KEY") else "None",
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        "gemini_temperature": os.getenv("GEMINI_TEMPERATURE", "0.2"),
        "env_file_exists": os.path.exists(".env"),
        "current_working_dir": os.getcwd(),
        "python_path": os.environ.get("PYTHONPATH", "Not set")
    }

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
한국어로 답변하되, 모든 문장을 '-요'로 끝나게 작성해요. 두 광고 문구 A/B의 CTR을 예측하고 각각에 대해 300자 이상의 심도 깊은 분석을 제공해요. 시장지식, 명확성, 관련성, 구체성, 후킹(수치, 긴박감, 사회적 증거)을 근거로 평가해요.

타겟: {audience or 'N/A'}
제품/카테고리: {payload.category or 'N/A'}

A안: {payload.marketing_a}
B안: {payload.marketing_b}

반드시 다음 키를 가진 JSON만 출력해요: ctr_a, ctr_b, analysis_a, analysis_b, ai_suggestion.
규칙:
- ctr_a/ctr_b는 0~1 사이 실수예요 (예: 0.123은 12.3%).
- analysis_a/analysis_b는 각각 300자 이상의 심도 깊은 분석이 포함된 문장형 한국어 텍스트예요. JSON/코드/마크다운 금지.
- ai_suggestion은 이 타겟에 맞춘 한 줄 문구예요.
- 모든 문장은 반드시 '-요'로 끝나야 해요.

각 분석은 다음 요소들을 포함하여 300자 이상으로 작성해주세요:
- 마케팅 문구의 강점과 약점 분석
- 타겟 오디언스와의 연관성 평가
- CTR 예측에 영향을 미치는 핵심 요소 분석
- 개선 방향과 최적화 전략 제시
""".strip()
    return prompt

def _call_llm(prompt: str) -> PredictResponse:
    if not llm:
        raise HTTPException(status_code=500, detail="LangChain LLM not initialized")

    try:
        # LangChain 체인 실행
        chain = COPY_ANALYSIS_TEMPLATE | llm | StrOutputParser()
        
        # 프롬프트에서 필요한 정보 추출
        # 프롬프트 형식에 맞게 파싱하여 필요한 변수들을 추출
        # 여기서는 간단한 방법으로 처리하되, 실제로는 더 정교한 파싱이 필요할 수 있음
        
        # 기본값 설정
        audience = "일반 사용자"
        category = "일반"
        marketing_a = "A안"
        marketing_b = "B안"
        
        # 프롬프트에서 정보 추출 시도
        if "타겟:" in prompt:
            audience = prompt.split("타겟:")[1].split("\n")[0].strip()
        if "제품/카테고리:" in prompt:
            category = prompt.split("제품/카테고리:")[1].split("\n")[0].strip()
        if "A안:" in prompt:
            marketing_a = prompt.split("A안:")[1].split("\n")[0].strip()
        if "B안:" in prompt:
            marketing_b = prompt.split("B안:")[1].split("\n")[0].strip()
        
        result = chain.invoke({
            "audience": audience,
            "category": category,
            "marketing_a": marketing_a,
            "marketing_b": marketing_b
        })
        
        # JSON 파싱
        try:
            data = json.loads(result)
        except Exception as exc:
            # Try to extract JSON substring if the model added prose
            try:
                start = result.find("{")
                end = result.rfind("}") + 1
                if start != -1 and end != -1:
                    data = json.loads(result[start:end])
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
            return s

        return PredictResponse(
            ctr_a=float(data["ctr_a"]),
            ctr_b=float(data["ctr_b"]),
            analysis_a=_cleanup_text(str(data["analysis_a"])),
            analysis_b=_cleanup_text(str(data["analysis_b"])),
            ai_suggestion=_cleanup_text(str(data["ai_suggestion"])),
        )
        
    except Exception as exc:
        print(f"LangChain LLM call failed: {exc}")
        raise HTTPException(status_code=502, detail=f"LangChain LLM error: {exc}")

def _call_llm_for_c_analysis(req: "PredictRequest", ai_text: str) -> PredictResponse:
    """C안 분석을 위한 LangChain 함수"""
    if not llm:
        raise HTTPException(status_code=500, detail="LangChain LLM not initialized")
    
    try:
        # LangChain 체인 실행
        chain = C_ANALYSIS_TEMPLATE | llm | StrOutputParser()
        
        # 타겟 정보 구성
        audience = f"{', '.join(req.age_groups or [])} {', '.join(req.genders or [])} {req.interests or ''}"
        
        result = chain.invoke({
            "audience": audience,
            "category": req.category or "",
            "ai_text": ai_text
        })
        
        # JSON 파싱
        try:
            data = json.loads(result)
        except Exception as exc:
            # Try to extract JSON substring if the model added prose
            try:
                start = result.find("{")
                end = result.rfind("}") + 1
                if start != -1 and end != -1:
                    data = json.loads(result[start:end])
                else:
                    raise
            except Exception:
                raise HTTPException(status_code=502, detail=f"C analysis LLM parsing failed: {exc}")

        # analysis_c 키 확인
        if "analysis_c" not in data:
            raise HTTPException(status_code=502, detail="C analysis LLM response missing analysis_c key")

        # 기본 PredictResponse 반환 (C안 분석만 포함)
        return PredictResponse(
            ctr_a=0.0,
            ctr_b=0.0,
            ctr_c=0.0,
            analysis_a="",
            analysis_b="",
            analysis_c=str(data["analysis_c"]),
            ai_suggestion=""
        )
        
    except Exception as exc:
        print(f"LangChain C analysis failed: {exc}")
        raise HTTPException(status_code=502, detail=f"LangChain C analysis error: {exc}")

# -----------------------------
# 예측 엔드포인트
# -----------------------------
@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        # 1) 페르소나 샘플링
        personas = sample_personas(req, topN=5)

        # 2) LLM 평가(배치) → 정규화 CTR(0~1 상대 스코어)
        rows, winner_kw = llm_persona_scores(req, personas)
        ctr_a, ctr_b, reasons_a, reasons_b = weighted_ctr_from_scores(rows)
    except Exception as e:
        # Gemini API 할당량 초과 등 에러 시 기본값 사용
        error_msg = str(e)
        print(f"페르소나 평가 실패, 기본값 사용: {error_msg}")
        
        # 에러 타입별 상세 정보
        if "quota" in error_msg.lower() or "rate_limits" in error_msg.lower():
            print("💰 Gemini API 할당량 초과: 무료 티어는 분당 2회 요청 제한이 있습니다")
            print("   잠시 후 다시 시도하거나 유료 플랜으로 업그레이드하세요")
        elif "internal error" in error_msg.lower():
            print("🔧 Gemini API 내부 오류: 잠시 후 다시 시도해주세요")
        elif "api_key" in error_msg.lower():
            print("🔑 Gemini API 키 문제: .env 파일에 GEMINI_API_KEY를 설정해주세요")
        else:
            print(f"❌ 기타 에러: {error_msg}")
        
        ctr_a, ctr_b = 0.45, 0.55  # 기본 CTR 값
        reasons_a, reasons_b = "기본 분석", "기본 분석"
        winner_kw = None

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

    # 5) 승자 요인 반영 제3문구
    try:
        third = generate_third_copy(
            req,
            winner_kw or (reasons_a if ctr_a >= ctr_b else reasons_b),
            "A" if ctr_a >= ctr_b else "B"
        )
    except Exception as e:
        print(f"제3문구 생성 실패, 기본값 사용: {e}")
        third = f"AI가 생성한 마케팅 문구: {req.marketing_a}와 {req.marketing_b}의 장점을 결합한 새로운 접근"

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

            # 8) LLM으로 상세한 분석문구 생성 (A안, B안)
    detailed_analysis = None
    try:
        detailed_analysis = _call_llm(_build_prompt(req))
    except Exception as e:
        print(f"A안, B안 분석 생성 실패, 기본값 사용: {e}")
        detailed_analysis = None
    
    # 9) C안 분석 생성 (Gemini API 실패 시 로컬 분석 생성)
    c_analysis_response = None
    try:
        c_analysis_response = _call_llm_for_c_analysis(req, third)
    except Exception as e:
        print(f"C안 분석 생성 실패, 로컬 분석 생성: {e}")
        # Gemini API 실패 시 로컬에서 분석 생성
        c_analysis_response = _generate_local_c_analysis(req, third, ctr_c, ctr_a, ctr_b)
    
    # 10) C안의 상세 분석 생성
    if c_analysis_response and hasattr(c_analysis_response, 'analysis_c'):
        c_analysis = c_analysis_response.analysis_c
    else:
        # fallback: 로컬 분석 생성
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
class ImageGenerationRequest(BaseModel):
    prompt: str
    n: int = 1
    size: str = "1024x1024"

class ImageGenerationResponse(BaseModel):
    images: List[str]

@app.post("/api/generate-images", response_model=ImageGenerationResponse)
def generate_images(req: ImageGenerationRequest):
    try:
        # LangChain을 사용하여 이미지 생성 프롬프트 최적화
        if not llm:
            raise Exception("LangChain LLM not initialized")
        
        # 이미지 프롬프트 최적화를 위한 LangChain 체인
        image_prompt_template = ChatPromptTemplate.from_messages([
            ("system", """당신은 전문적인 광고 이미지 프롬프트 작성자입니다. 
마케팅 문구를 바탕으로 DALL-E 3가 이해할 수 있는 명확하고 구체적인 이미지 프롬프트를 작성해주세요."""),
            ("human", """다음 마케팅 문구를 바탕으로 이미지 생성 프롬프트를 작성해주세요:

마케팅 문구: {marketing_copy}

요구사항:
- 현대적이고 전문적인 광고 이미지
- 마케팅 메시지를 보완하는 깔끔한 레이아웃
- 디지털 광고에 적합 (소셜 미디어, 디스플레이 광고)
- 브랜드 친화적이고 시각적으로 매력적
- 마케팅 메시지를 향상시키는 색상과 이미지 사용
- 카피의 메시지를 지원하는 시각적 요소에 집중

영어로 작성하고, 구체적이고 명확하게 표현해주세요.""")
        ])
        
        # 프롬프트 최적화
        prompt_chain = image_prompt_template | llm | StrOutputParser()
        optimized_prompt = prompt_chain.invoke({
            "marketing_copy": req.prompt
        })
        
        # Gemini API를 사용하여 이미지 생성
        # Gemini는 현재 이미지 생성 기능이 제한적이므로 텍스트 기반 이미지 생성
        try:
            # Gemini 2.5 Pro를 사용한 이미지 생성 (텍스트 기반)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 이미지 생성 프롬프트 구성
            image_generation_prompt = f"""
            Create a detailed description of an advertisement image based on this marketing copy: "{req.prompt}"
            
            The image should be:
            - Modern and professional
            - Suitable for digital advertising
            - Brand-friendly and visually appealing
            - Complementary to the marketing message
            
            Please describe the image in detail, including:
            - Visual elements and composition
            - Color scheme and mood
            - Key objects and their placement
            - Overall atmosphere and style
            
            Return only the image description, no additional text.
            """
            
            # Gemini로 이미지 설명 생성
            response = model.generate_content(image_generation_prompt)
            image_description = response.text
            
            # 실제 이미지 생성은 Gemini에서 지원하지 않으므로 설명을 반환
            # 실제 프로덕션에서는 다른 이미지 생성 서비스 사용 고려
            image_urls = [f"Generated Image Description: {image_description}"]
            
        except Exception as e:
            print(f"Gemini image generation failed: {e}")
            # Fallback: 기본 이미지 설명
            image_urls = [f"Marketing Image for: {req.prompt}"]
        
        return ImageGenerationResponse(images=image_urls)
        
    except Exception as e:
        print(f"Image generation failed: {e}")
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

# -----------------------------
# LangChain 에이전트 엔드포인트
# -----------------------------
class AgentRequest(BaseModel):
    query: str
    marketing_a: Optional[str] = None
    marketing_b: Optional[str] = None
    category: Optional[str] = None
    target_info: Optional[str] = None

class AgentResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

@app.post("/api/agent-query", response_model=AgentResponse)
def agent_query(req: AgentRequest):
    """LangChain 에이전트를 사용한 마케팅 분석 쿼리"""
    try:
        if not marketing_agent:
            return AgentResponse(
                response="",
                success=False,
                error="마케팅 분석 에이전트가 초기화되지 않았습니다."
            )
        
        # 에이전트 실행
        result = marketing_agent.invoke({
            "input": req.query,
            "chat_history": []
        })
        
        return AgentResponse(
            response=result.get("output", "분석 결과를 생성할 수 없습니다."),
            success=True
        )
        
    except Exception as e:
        print(f"Agent query failed: {e}")
        return AgentResponse(
            response="",
            success=False,
            error=f"에이전트 쿼리 실패: {str(e)}"
        )

@app.get("/api/agent-status")
def agent_status():
    """에이전트 상태 확인"""
    return {
        "agent_initialized": marketing_agent is not None,
        "llm_available": llm is not None,
        "embeddings_available": embeddings is not None,
        "tools": ["marketing_analysis"] if marketing_agent else []
    }

def _generate_local_c_analysis(req: "PredictRequest", ai_text: str, ctr_c: float, ctr_a: float, ctr_b: float) -> PredictResponse:
    """Gemini API 실패 시 로컬에서 C안 분석 생성"""
    try:
        # 타겟 정보 구성
        age_groups = ", ".join(req.age_groups or [])
        genders = ", ".join(req.genders or [])
        interests = req.interests or ""
        category = req.category or "일반"
        
        # 승자 결정
        winner = "A" if ctr_a >= ctr_b else "B"
        winner_ctr = max(ctr_a, ctr_b)
        
        # 로컬 분석 텍스트 생성
        analysis_c = f"""AI가 생성한 마케팅 문구 '{ai_text}'에 대한 상세 분석입니다.

이 문구는 {winner}안의 핵심 강점을 반영하여 {ctr_c:.1%}의 CTR을 예측합니다. 

**타겟 분석**: {age_groups} {genders} {interests}를 대상으로 한 {category} 카테고리 마케팅에 최적화되어 있습니다.

**전략적 장점**: 
- {winner}안의 성공 요인을 통합하여 더 높은 효과 기대
- 타겟 오디언스의 특성을 고려한 맞춤형 메시지 구성
- 감정적 호소력과 명확한 가치 제안의 균형

**CTR 예측 근거**: 기존 {winner}안({winner_ctr:.1%}) 대비 {ctr_c/winner_ctr:.1%}배 향상된 성과를 기대할 수 있습니다."""

        return PredictResponse(
            ctr_a=0.0,
            ctr_b=0.0,
            ctr_c=ctr_c,
            analysis_a="",
            analysis_b="",
            analysis_c=analysis_c,
            ai_suggestion=""
        )
        
    except Exception as e:
        print(f"로컬 C안 분석 생성 실패: {e}")
        return None

def _generate_local_c_analysis_text(req: "PredictRequest", ai_text: str, ctr_c: float, ctr_a: float, ctr_b: float) -> str:
    """간단한 로컬 C안 분석 텍스트 생성"""
    try:
        winner = "A" if ctr_a >= ctr_b else "B"
        winner_ctr = max(ctr_a, ctr_b)
        
        return f"""AI가 생성한 마케팅 문구 '{ai_text}'에 대한 분석입니다. 

이 문구는 {winner}안의 장점을 결합하여 {ctr_c:.1%}의 CTR을 예측합니다. 

타겟 오디언스({', '.join(req.age_groups or [])} {', '.join(req.genders or [])} {req.interests or ''})와의 높은 연관성과 구체적인 제안으로 효과적인 마케팅 성과를 기대할 수 있습니다.

{winner}안({winner_ctr:.1%}) 대비 {ctr_c/winner_ctr:.1%}배 향상된 성과를 기대할 수 있어요."""
        
    except Exception as e:
        print(f"간단한 로컬 C안 분석 생성 실패: {e}")
        return f"AI가 생성한 마케팅 문구 '{ai_text}'에 대한 분석입니다. 이 문구는 A안과 B안의 장점을 결합하여 {ctr_c:.1%}의 CTR을 예측합니다."
