import os
import re
import json
import time
import random
from typing import List, Dict, Any, Tuple, Optional

from .config import PERSONAS, CALIBRATION
from .models import PredictRequest

# -----------------------------
# JSON 추출 유틸
# -----------------------------
_JSON_BLOCK = re.compile(r"\{[\s\S]*\}")

def _extract_json(text: str) -> dict:
    """모델 응답에서 JSON 블록만 안전하게 추출/파싱."""
    if not text:
        raise ValueError("빈 응답")
    s = text.strip()

    # 코드펜스 제거
    if s.startswith("```"):
        # ```json ... ``` 혹은 ``` ... ```
        s = s.strip("`").strip()
        if s[:4].lower() == "json":
            s = s[4:].strip()

    # 가장 그럴듯한 JSON 블록
    m = _JSON_BLOCK.search(s)
    if m:
        return json.loads(m.group(0))

    # 전체가 JSON일 수도 있음
    return json.loads(s)

# -----------------------------
# 페르소나 샘플링
# -----------------------------
def sample_personas(req: PredictRequest, topN: int = 5) -> List[Dict[str, Any]]:
    filtered = []
    for p in PERSONAS:
        score = 0
        if req.age_groups and p["age_group"] in (req.age_groups or []):
            score += 1
        if req.genders and p["gender"] in (req.genders or []):
            score += 1
        if req.interests and any(k in (req.interests or "") for k in p["keywords"]):
            score += 1
        if req.category and any(k in (req.category or "") for k in p.get("categories", "").split(", ")):
            score += 1
        filtered.append((score, p))

    filtered.sort(key=lambda x: x[0], reverse=True)
    pool = [p for s, p in filtered[:max(topN*2, topN)]] or PERSONAS
    return random.sample(pool, k=min(topN, len(pool)))

# -----------------------------
# Gemini 호출 (재시도 + 모델 롤오버)
# -----------------------------
def _call_gemini_with_retry(prompt: str, max_retries: int = 3, timeout_s: float = 25.0) -> Optional[dict]:
    """
    - 우선순위 모델: 환경변수 GEMINI_MODEL > 기본 리스트
    - 500/429 등의 오류에 대해 지수 백오프 재시도
    - 응답을 JSON으로 파싱해서 dict 반환
    - 모든 시도 실패 시 None 반환
    """
    import google.genai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")

    # 모델 우선순위
    priority = []
    if os.getenv("GEMINI_MODEL"):
        priority.append(os.getenv("GEMINI_MODEL").strip())
    # 기본 롤오버 순서
    for m in ["gemini-2.5-pro", "gemini-1.5-pro", "gemini-1.5-flash"]:
        if m not in priority:
            priority.append(m)

    client = genai.Client(api_key=api_key)

    last_err = None
    for model in priority:
        backoff = 0.8
        for attempt in range(1, max_retries + 1):
            try:
                print(f"[Gemini] ▶ 호출 시작 model={model} attempt={attempt}")
                t0 = time.time()
                # google-genai는 요청 시간이 길 수 있으니 함수 레벨 타임아웃 가드
                resp = client.models.generate_content(
                    model=model,
                    contents=[prompt],
                    # 일부 환경에서 파라미터 키워드가 바뀔 수 있으므로 최소 옵션만 사용
                )
                elapsed = int((time.time() - t0) * 1000)
                print(f"[Gemini] ◀ 응답 수신 model={model} latency_ms={elapsed}")

                # 텍스트 추출
                text_out = getattr(resp, "text", None)
                if not text_out:
                    parts = []
                    for cand in getattr(resp, "candidates", []) or []:
                        content = getattr(cand, "content", None)
                        for part in getattr(content, "parts", []) or []:
                            if getattr(part, "text", None):
                                parts.append(part.text)
                    text_out = "\n".join(parts).strip()

                data = _extract_json(text_out)
                return data

            except Exception as e:
                last_err = e
                print(f"[Gemini] ❌ 실패 model={model} attempt={attempt} err={e}")
                if attempt < max_retries:
                    time.sleep(backoff + random.uniform(0, 0.2))
                    backoff *= 2.0
                else:
                    # 다음 모델로 롤오버
                    break

    # 전부 실패
    print(f"[Gemini] ❌ 모든 모델/재시도 실패: {last_err}")
    return None

# -----------------------------
# Gemini 기반 점수 계산 (강화판)
# -----------------------------
def llm_persona_scores(req: PredictRequest, personas: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str]:
    """
    - Gemini를 반드시 시도
    - 500/내부 오류 등은 재시도 및 모델 롤오버로 최대한 극복
    - 성공 시 페르소나별 a_score/b_score를 사용
    - 실패 시 예외 throw → 호출측에서 fast fallback
    """
    persona_lines = [
        f"- {p.get('name','N/A')} ({p['age_group']} {p['gender']}): {p['interests']}"
        for p in personas
    ]
    prompt = f"""
당신은 마케팅 전문가입니다. 두 개의 마케팅 문구 A안, B안과 여러 페르소나 정보를 보고,
각 페르소나가 어느 쪽에 더 반응할지 0~1 점수로 평가하세요.

마케팅 문구:
A안: {req.marketing_a}
B안: {req.marketing_b}

페르소나:
{chr(10).join(persona_lines)}

반드시 아래 JSON "만" 출력하세요. 다른 설명은 절대 금지.
형식:
{{
  "personas": [
    {{"a_score": 0.0, "b_score": 0.0}},
    ...
  ]
}}
""".strip()

    data = _call_gemini_with_retry(prompt, max_retries=3)
    if data is None:
        # 호출측에서 fast fallback 하도록 예외
        raise RuntimeError("Gemini 호출 실패")

    plist = data.get("personas", [])
    if not isinstance(plist, list) or not plist:
        raise ValueError("Gemini 응답 포맷 오류: personas 누락")

    # 길이 보정
    if len(plist) < len(personas):
        while len(plist) < len(personas):
            plist.append({"a_score": 0.5, "b_score": 0.5})

    rows: List[Dict[str, Any]] = []
    winner_keywords: List[str] = []
    for i, pscore in enumerate(plist[:len(personas)]):
        persona = personas[i]
        try:
            a_score = float(pscore.get("a_score", 0.5))
            b_score = float(pscore.get("b_score", 0.5))
        except Exception:
            a_score, b_score = 0.5, 0.5
        rows.append({
            "persona": persona,
            "a_score": max(0.0, min(1.0, a_score)),
            "b_score": max(0.0, min(1.0, b_score)),
            "winner": "A" if a_score > b_score else "B",
        })
        winner_keywords.extend(persona.get("keywords", []))

    dedup = list(dict.fromkeys(winner_keywords))
    return rows, ", ".join(dedup[:5])

# -----------------------------
# 빠른 점수 계산 (fallback)
# -----------------------------
def fast_persona_scores(req: PredictRequest, personas: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str]:
    rows = []
    kw_pool = []
    for persona in personas:
        a_score = _calculate_matching_score(persona, req.marketing_a)
        b_score = _calculate_matching_score(persona, req.marketing_b)
        rows.append({
            "persona": persona,
            "a_score": a_score,
            "b_score": b_score,
            "winner": "A" if a_score > b_score else "B",
        })
        kw_pool.extend(persona.get("keywords", []))
    return rows, ", ".join(list(dict.fromkeys(kw_pool))[:5])

# -----------------------------
# 내부 매칭 점수 (fallback용)
# -----------------------------
def _calculate_matching_score(persona: Dict[str, Any], marketing_text: str) -> float:
    text_lower = (marketing_text or "").lower()
    score = 0.0
    for keyword in persona.get("keywords", []):
        if keyword.lower() in text_lower:
            score += 0.1
    score += random.uniform(-0.05, 0.05)
    return float(max(0.0, min(1.0, 0.3 + score)))

# -----------------------------
# CTR 계산
# -----------------------------
def weighted_ctr_from_scores(rows: List[Dict[str, Any]]) -> Tuple[float, float, str, str]:
    if not rows:
        return 0.45, 0.55, "기본 분석", "기본 분석"
    total_a = sum(r["a_score"] for r in rows)
    total_b = sum(r["b_score"] for r in rows)
    if total_a + total_b > 0:
        ctr_a = total_a / (total_a + total_b)
        ctr_b = total_b / (total_a + total_b)
    else:
        ctr_a, ctr_b = 0.45, 0.55
    reasons_a = "AI 분석: 타겟 키워드 정합성 높음"
    reasons_b = "AI 분석: 메시지 명확성/관심사 적합"
    return float(ctr_a), float(ctr_b), reasons_a, reasons_b

# -----------------------------
# 간단 KNN 팔로우(시뮬레이션)
# -----------------------------
def _knn_follow(category: str, ages: List[str], genders: List[str], interests: str,
                A: str, B: str, k: int = 5, tau_hard: float = 0.9) -> Dict[str, Any]:
    if random.random() < 0.15:
        return {"mode": "hard", "follow_class": random.choice(["A", "B"])}
    return {"mode": "none"}

# -----------------------------
# 제3문구 생성
# -----------------------------
def generate_third_copy(req: PredictRequest, winner_keywords: str, winner_class: str) -> str:
    if not winner_keywords:
        winner_keywords = "트렌디, 혁신"
    category_templates = {
        "뷰티":   f"'{winner_keywords}'의 핵심 가치를 담아 더욱 매력적인 {req.category} 경험을 선사해요",
        "패션":   f"'{winner_keywords}'의 트렌드를 반영한 독특한 {req.category} 스타일을 제안해요",
        "식품":   f"'{winner_keywords}'의 맛과 건강을 모두 만족시키는 {req.category}를 경험해보세요",
        "전자제품": f"'{winner_keywords}'의 혁신 기술로 더 스마트한 {req.category} 라이프를 시작하세요",
        "홈리빙": f"'{winner_keywords}'의 편리함과 아름다움을 담은 {req.category}로 공간을 완성하세요",
    }
    return category_templates.get(req.category or "기타", f"'{winner_keywords}'의 장점을 결합한 {req.category} 솔루션을 제공해요")

# -----------------------------
# CTR 캘리브레이션
# -----------------------------
def calibrate_ctr(ctr: float, category: str, shrink: float = 0.35) -> float:
    e = CALIBRATION.get(category or "기타", CALIBRATION["기타"])
    calibrated = e["min"] + (e["max"] - e["min"]) * float(max(0.0, min(1.0, ctr))) * (1 - shrink)
    return float(max(e["min"], min(e["max"], calibrated)))
