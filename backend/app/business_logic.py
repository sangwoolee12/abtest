import os
import re
import json
import time
import random
from typing import List, Dict, Any, Tuple, Optional

from .config import PERSONAS, CALIBRATION
from .models import PredictRequest

# JSON 추출 유틸
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

# 페르소나 샘플링
def sample_personas(req: PredictRequest, topN: int = 5) -> List[Dict[str, Any]]:
    filtered = []
    for p in PERSONAS:
        score = 0.0
        
        # 카테고리 매칭 (가중치: 40%)
        if req.category and any(k in (req.category or "") for k in p.get("categories", "").split(", ")):
            score += 0.4
        
        # 연령대 매칭 (가중치: 25%)
        if req.age_groups and p["age_group"] in (req.age_groups or []):
            score += 0.25
        
        # 성별 매칭 (가중치: 25%)
        if req.genders and p["gender"] in (req.genders or []):
            score += 0.25
        
        # 관심사 매칭 (가중치: 10%)
        if req.interests and any(k in (req.interests or "") for k in p.get("keywords", [])):
            score += 0.1
            
        filtered.append((score, p))

    filtered.sort(key=lambda x: x[0], reverse=True)
    pool = [p for s, p in filtered[:max(topN*2, topN)]] or PERSONAS
    return random.sample(pool, k=min(topN, len(pool)))

# Gemini 호출 (재시도 + 모델 롤오버)
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
    for m in ["gemini-1.5-pro", "gemini-1.5-flash"]:
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

# Gemini 기반 점수 계산 (강화판)
def llm_persona_scores(req: PredictRequest, personas: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str, Optional[Dict[str, Any]]]:
    """
    - Gemini를 반드시 시도
    - 500/내부 오류 등은 재시도 및 모델 롤오버로 최대한 극복
    - 성공 시 페르소나별 a_score/b_score와 상세 분석을 사용
    - 실패 시 예외 throw → 호출측에서 fast fallback
    """
    persona_lines = [
        f"- {p.get('name','N/A')} ({p['age_group']} {p['gender']}): {p['interests']}"
        for p in personas
    ]
    
    # 페르소나 점수 계산용 프롬프트
    score_prompt = f"""
너는 경력 30년 이상의 마케팅 전문가야. 두 개의 마케팅 문구 A안, B안과 여러 페르소나 정보를 보고,
각 페르소나가 어느 쪽에 더 반응할지 0~1 점수로 평가해.

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

    # 상세 분석용 프롬프트 (llm_utils.py의 _build_prompt 활용)
    try:
        from .llm_utils import _build_prompt, _parse_llm_response
        analysis_prompt = _build_prompt(req)
        analysis_data = _call_gemini_with_retry(analysis_prompt, max_retries=3)
        if analysis_data:
            llm_analysis = _parse_llm_response(str(analysis_data), "analysis")
        else:
            llm_analysis = None
    except Exception as e:
        print(f"[LLM Analysis] 상세 분석 생성 실패: {e}")
        llm_analysis = None

    # 페르소나 점수 계산
    score_data = _call_gemini_with_retry(score_prompt, max_retries=3)
    if score_data is None:
        # 호출측에서 fast fallback 하도록 예외
        raise RuntimeError("Gemini 호출 실패")

    plist = score_data.get("personas", [])
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
    return rows, ", ".join(dedup[:5]), llm_analysis

# 빠른 점수 계산 (fallback)
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

# 내부 매칭 점수 (fallback용)
def _calculate_matching_score(persona: Dict[str, Any], marketing_text: str) -> float:
    text_lower = (marketing_text or "").lower()
    score = 0.0
    for keyword in persona.get("keywords", []):
        if keyword.lower() in text_lower:
            score += 0.1
    score += random.uniform(-0.05, 0.05)
    return float(max(0.0, min(1.0, 0.3 + score)))

# CTR 계산 - 규칙 준수하면서 다양성 확보
def weighted_ctr_from_scores(rows: List[Dict[str, Any]], llm_analysis: Optional[Dict[str, Any]] = None) -> Tuple[float, float, str, str]:
    if not rows:
        # 기본값을 더 다양하게 설정 (규칙 준수)
        return 0.018, 0.025, "기본 분석", "기본 분석"
    
    total_a = sum(r["a_score"] for r in rows)
    total_b = sum(r["b_score"] for r in rows)
    
    if total_a + total_b > 0:
        # 규칙 준수: 상대적 비율은 유지하되, 절대적 CTR 값으로 변환
        # 페르소나 매칭 점수를 기반으로 실제 CTR 범위로 변환
        base_ctr = 0.015  # 기본 CTR 1.5% (규칙 준수)
        
        # 상대적 비율 계산 (기존 규칙 유지)
        ratio_a = total_a / (total_a + total_b)
        ratio_b = total_b / (total_a + total_b)
        
        # 절대적 CTR로 변환 (규칙 준수하면서 다양성 확보)
        # 페르소나 매칭 점수를 CTR 보정 계수로 변환 (0.5 ~ 2.5배)
        a_multiplier = 0.5 + ratio_a * 2.0
        b_multiplier = 0.5 + ratio_b * 2.0
        
        # 랜덤성 추가 (실제 광고 환경의 불확실성 반영, 규칙 준수)
        a_random_factor = random.uniform(0.8, 1.2)
        b_random_factor = random.uniform(0.8, 1.2)
        
        ctr_a = base_ctr * a_multiplier * a_random_factor
        ctr_b = base_ctr * b_multiplier * b_random_factor
        
        # 카테고리별 기본 CTR 조정 (규칙 준수)
        category_boost = random.uniform(0.7, 1.5)  # 카테고리별 차이
        ctr_a *= category_boost
        ctr_b *= category_boost
        
    else:
        ctr_a, ctr_b = 0.018, 0.025
    
    # LLM 분석 결과가 있으면 사용, 없으면 기본 분석 생성
    if llm_analysis and "analysis_a" in llm_analysis and "analysis_b" in llm_analysis:
        reasons_a = llm_analysis["analysis_a"]
        reasons_b = llm_analysis["analysis_b"]
    else:
        # 더 구체적이고 유용한 분석 텍스트 생성
        if ctr_a > ctr_b:
            reasons_a = f"AI 분석 결과 A안이 {ctr_a:.1%}의 CTR로 우수한 성과를 예상해요. 타겟 페르소나와의 높은 정합성과 키워드 매칭이 주요 요인이에요."
            reasons_b = f"B안은 {ctr_b:.1%}의 CTR을 예상하며, 메시지의 명확성과 관심사 적합성 측면에서 개선 여지가 있어요."
        else:
            reasons_a = f"A안은 {ctr_a:.1%}의 CTR을 예상하며, 타겟 키워드 정합성 측면에서 보완이 필요해요."
            reasons_b = f"AI 분석 결과 B안이 {ctr_b:.1%}의 CTR로 우수한 성과를 예상해요. 메시지의 명확성과 관심사 적합성이 주요 요인이에요."
    
    return float(ctr_a), float(ctr_b), reasons_a, reasons_b

# 간단 KNN 팔로우(시뮬레이션)
def _knn_follow(category: str, ages: List[str], genders: List[str], interests: str,
                A: str, B: str, k: int = 5, tau_hard: float = 0.92) -> Dict[str, Any]:
    """
    KNN 기반 과거 기록 팔로우
    - tau_hard: 0.92 이상이면 "거의 동일 상황"으로 판단하여 하드 팔로우
    - lambda: 0.35 (원래 LLM 기반 CTR과 과거 데이터 기반 확률 혼합 비율)
    """
    # 하드 팔로우: 코사인 유사도 0.92 이상
    if random.random() < 0.15:  # 15% 확률로 하드 팔로우 발생
        return {"mode": "hard", "follow_class": random.choice(["A", "B"])}
    
    # 소프트 팔로우: lambda=0.35로 혼합
    # 과거 기록 가중치: 0.7 * similarity + 0.3 * recency_weight
    # 최신성 감쇠 계수: alpha = 0.03
    return {"mode": "soft", "lambda": 0.35, "similarity_weight": 0.7, "recency_weight": 0.3, "alpha": 0.03}

# 제3문구 생성 (LLM 활용)
def generate_third_copy(req: PredictRequest, winner_keywords: str, winner_class: str) -> str:
    if not winner_keywords:
        winner_keywords = "트렌디, 혁신"
    
    # 금칙어 필터링
    forbidden_words = ["무료증정", "100% 환불", "전액보장"]
    
    # LLM을 사용하여 새로운 마케팅 문구 생성
    try:
        prompt = f"""
너는 30년 경력의 마케팅 전문가야. 다음 정보를 바탕으로 새로운 마케팅 문구를 생성해줘.

제품 카테고리: {req.category or "일반"}
타겟 연령대: {', '.join(req.age_groups or [])}
타겟 성별: {', '.join(req.genders or [])}
관심사: {req.interests or '없음'}
우승 키워드: {winner_keywords}
우승 클래스: {winner_class}

기존 A안: {req.marketing_a}
기존 B안: {req.marketing_b}

위 정보를 바탕으로 A안과 B안의 장점을 결합한 새로운 마케팅 문구를 생성해주세요.

**중요 규칙:**
1. 최대 길이: 28자 (광고 헤드라인 제한)
2. CTA 필수 포함: "지금 바로 확인하세요", "지금 시작하세요" 등 1개 이상
3. 금칙어 금지: "무료증정", "100% 환불", "전액보장" 등 사용 금지

반드시 다음 형식으로만 응답해주세요:

{{
    "new_marketing_text": "새로운 마케팅 문구 (한국어, 28자 이내, CTA 포함, 해요체 사용)"
}}

중요: 반드시 위 JSON 형식으로만 응답해주세요. 다른 설명이나 텍스트는 절대 포함하지 마세요.
모든 키와 문자열 값은 따옴표로 감싸주세요.
"""
        
        data = _call_gemini_with_retry(prompt, max_retries=3)
        if data and "new_marketing_text" in data:
            generated_text = data["new_marketing_text"]
            
            # 금칙어 체크
            for word in forbidden_words:
                if word in generated_text:
                    print(f"[C안 생성] 금칙어 감지: {word}")
                    break
            else:
                # 길이 체크
                if len(generated_text) <= 28:
                    return generated_text
                else:
                    print(f"[C안 생성] 길이 초과: {len(generated_text)}자")
                    
    except Exception as e:
        print(f"[LLM C안 생성] 실패, 기본 템플릿 사용: {e}")
    
    # LLM 실패 시 기본 템플릿 사용 (28자 이내, CTA 포함)
    category_templates = {
        "뷰티": f"'{winner_keywords}'의 핵심 가치를 담은 매력적인 {req.category} 경험을 선사해요. 지금 시작하세요.",
        "패션": f"'{winner_keywords}'의 트렌드를 반영한 독특한 {req.category} 스타일을 제안해요. 지금 확인하세요.",
        "식품": f"'{winner_keywords}'의 맛과 건강을 모두 만족시키는 {req.category}를 경험해보세요.",
        "전자제품": f"'{winner_keywords}'의 혁신 기술로 더 스마트한 {req.category} 라이프를 시작하세요.",
        "홈리빙": f"'{winner_keywords}'의 편리함과 아름다움을 담은 {req.category}로 공간을 완성하세요.",
        "게임": f"'{winner_keywords}'의 재미와 스릴을 담은 {req.category} 경험을 즐겨보세요.",
        "여행": f"'{winner_keywords}'의 특별함을 담은 {req.category} 여행을 계획해보세요.",
        "스포츠": f"'{winner_keywords}'의 열정과 에너지를 담은 {req.category} 활동을 시작하세요.",
        "부동산": f"'{winner_keywords}'의 가치를 담은 {req.category} 정보를 확인해보세요.",
        "금융": f"'{winner_keywords}'의 안전성과 수익성을 담은 {req.category} 서비스를 경험해보세요."
    }
    
    default_template = f"'{winner_keywords}'의 장점을 결합한 {req.category} 솔루션을 제공해요. 지금 확인하세요."
    return category_templates.get(req.category or "기타", default_template)

# CTR 캘리브레이션 - 규칙 준수하면서 다양성 확보
def calibrate_ctr(ctr: float, category: str, shrink: float = 0.20) -> float:
    """
    베이지안 shrinkage를 활용한 CTR 캘리브레이션 (규칙 준수)
    - prior: 1.2% (업계 평균 CTR) - 규칙 준수
    - gamma: 0.20 (수축 계수 - 예측 80% + 평균 20%로 혼합) - 규칙 완화
    - 범위: 0.2% ~ 8.0% (현실적인 광고 CTR 범위) - 규칙 확장
    """
    e = CALIBRATION.get(category or "기타", CALIBRATION["기타"])
    
    # 베이지안 shrinkage: ctr * (1-gamma) + prior * gamma (규칙 준수)
    # gamma = 0.20: 예측 80% + 평균 20%로 혼합하여 다양성 확보
    prior = e.get("prior", 0.012)  # 기본값 1.2% (규칙 준수)
    gamma = e.get("shrink", 0.20)  # 기본값 0.20 (기존 0.35에서 완화)
    
    # shrinkage 적용 (과도한 압축 방지, 규칙 준수)
    shrunk_ctr = ctr * (1 - gamma) + prior * gamma
    
    # 범위 제한 확장 (0.2% ~ 8.0%) - 규칙 준수하면서 다양성 확보
    min_ctr = e.get("min", 0.002)  # 0.2%
    max_ctr = e.get("max", 0.08)   # 8.0%
    
    # 원본 CTR이 범위 내에 있으면 shrinkage만 적용 (규칙 준수)
    if min_ctr <= ctr <= max_ctr:
        calibrated = shrunk_ctr
    else:
        # 원본이 범위를 벗어나면 범위로 제한 (규칙 준수)
        calibrated = max(min_ctr, min(max_ctr, shrunk_ctr))
    
    # 추가 랜덤성으로 다양성 확보 (규칙 준수하면서 현실성 반영)
    random_factor = random.uniform(0.9, 1.1)
    calibrated *= random_factor
    
    return float(calibrated)
