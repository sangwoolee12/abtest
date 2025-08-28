import random
import numpy as np
import json
from typing import List, Dict, Any, Tuple
from .config import PERSONAS, CALIBRATION
from .models import PredictRequest
from .llm_utils import _clean_llm_response

# -----------------------------
# 페르소나 샘플링
# -----------------------------

def sample_personas(req: PredictRequest, topN: int = 5) -> List[Dict[str, Any]]:
    """요청에 맞는 페르소나 샘플링"""
    if not req.age_groups and not req.genders and not req.interests:
        # 모든 조건이 없으면 랜덤 샘플링
        return random.sample(PERSONAS, min(topN, len(PERSONAS)))
    
    # 조건에 맞는 페르소나 필터링
    filtered = []
    for persona in PERSONAS:
        score = 0
        
        # 연령대 매칭
        if req.age_groups and persona["age_group"] in req.age_groups:
            score += 2
        
        # 성별 매칭
        if req.genders and persona["gender"] in req.genders:
            score += 2
        
        # 관심사 매칭 (키워드 기반)
        if req.interests:
            interests_lower = req.interests.lower()
            for keyword in persona["keywords"]:
                if keyword.lower() in interests_lower:
                    score += 1
        
        if score > 0:
            filtered.append((persona, score))
    
    # 점수순 정렬 후 상위 N개 선택
    filtered.sort(key=lambda x: x[1], reverse=True)
    selected = [p[0] for p in filtered[:topN]]
    
    # 부족하면 랜덤으로 보충
    if len(selected) < topN:
        remaining = [p for p in PERSONAS if p not in selected]
        selected.extend(random.sample(remaining, min(topN - len(selected), len(remaining))))
    
    return selected

# -----------------------------
# LLM 페르소나 점수
# -----------------------------

def llm_persona_scores(req: PredictRequest, personas: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str]:
    """LLM을 사용하여 페르소나별 점수 계산 (최적화)"""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise Exception("Gemini API key not configured")
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2, google_api_key=api_key)
        
        rows = []
        winner_keywords = []
        
        # 배치 처리로 속도 향상
        batch_prompt = f"""
당신은 마케팅 전문가입니다. 다음 페르소나들과 마케팅 문구 A안, B안의 매칭도를 분석해주세요.

마케팅 문구:
A안: {req.marketing_a}
B안: {req.marketing_b}

페르소나 정보:
{chr(10).join([f"- {p['name']} ({p['age_group']} {p['gender']}): {p['interests']}" for p in personas])}

각 페르소나별로 다음 형식으로 응답해주세요:
{{
    "personas": [
        {{"name": "페르소나명", "a_score": 0.0-1.0, "b_score": 0.0-1.0}},
        ...
    ]
}}

JSON 형식으로만 응답해주세요.
"""
        
        try:
            response = llm.invoke(batch_prompt)
            data = json.loads(_clean_llm_response(response.content))
            
            for i, p_data in enumerate(data.get("personas", [])):
                persona = personas[i] if i < len(personas) else personas[0]
                a_score = float(p_data.get("a_score", 0.5))
                b_score = float(p_data.get("b_score", 0.5))
                
                rows.append({
                    "persona": persona,
                    "a_score": a_score,
                    "b_score": b_score,
                    "winner": "A" if a_score > b_score else "B"
                })
                
                if a_score > b_score:
                    winner_keywords.extend(persona["keywords"])
                else:
                    winner_keywords.extend(persona["keywords"])
                    
        except Exception as e:
            print(f"배치 분석 실패, 개별 분석 시도: {e}")
            # 개별 분석으로 fallback
            for persona in personas:
                a_score = _calculate_matching_score(persona, req.marketing_a)
                b_score = _calculate_matching_score(persona, req.marketing_b)
                
                rows.append({
                    "persona": persona,
                    "a_score": a_score,
                    "b_score": b_score,
                    "winner": "A" if a_score > b_score else "B"
                })
        
        winner_keywords = list(set(winner_keywords))
        return rows, ", ".join(winner_keywords[:5])
        
    except Exception as e:
        print(f"LLM 분석 실패, 시뮬레이션 사용: {e}")
        # 빠른 시뮬레이션
        rows = []
        for persona in personas:
            a_score = _calculate_matching_score(persona, req.marketing_a)
            b_score = _calculate_matching_score(persona, req.marketing_b)
            rows.append({
                "persona": persona,
                "a_score": a_score,
                "b_score": b_score,
                "winner": "A" if a_score > b_score else "B"
            })
        
        winner_keywords = [kw for p in personas for kw in p["keywords"]]
        return rows, ", ".join(list(set(winner_keywords))[:5])

def _calculate_matching_score(persona: Dict[str, Any], marketing_text: str) -> float:
    """페르소나와 마케팅 문구의 매칭도 계산"""
    text_lower = marketing_text.lower()
    score = 0.0
    
    # 키워드 매칭
    for keyword in persona["keywords"]:
        if keyword.lower() in text_lower:
            score += 0.1
    
    # 연령대 매칭 (마케팅 문구에 연령대가 언급된 경우)
    age_keywords = {
        "10대": ["10대", "청소년", "학생", "학교"],
        "20대": ["20대", "청년", "대학생", "직장인"],
        "30대": ["30대", "성인", "직장인", "가족"],
        "40대": ["40대", "중년", "가족", "경험"],
        "50대+": ["50대", "60대", "70대", "노년", "경험"]
    }
    
    age_group = persona["age_group"]
    if age_group in age_keywords:
        for keyword in age_keywords[age_group]:
            if keyword in text_lower:
                score += 0.05
    
    # 기본 점수 + 랜덤 요소
    base_score = 0.3 + score
    random_factor = random.uniform(-0.1, 0.1)
    
    return max(0.0, min(1.0, base_score + random_factor))

# -----------------------------
# CTR 계산
# -----------------------------

def weighted_ctr_from_scores(rows: List[Dict[str, Any]]) -> Tuple[float, float, str, str]:
    """페르소나 점수로부터 가중 CTR 계산"""
    if not rows:
        return 0.45, 0.55, "기본 분석", "기본 분석"
    
    total_a = sum(row["a_score"] for row in rows)
    total_b = sum(row["b_score"] for row in rows)
    
    # 정규화
    if total_a + total_b > 0:
        ctr_a = total_a / (total_a + total_b)
        ctr_b = total_b / (total_a + total_b)
    else:
        ctr_a, ctr_b = 0.45, 0.55
    
    # 분석 문구 생성
    reasons_a = f"페르소나 분석 결과 A안이 {ctr_a:.1%}의 CTR을 보입니다."
    reasons_b = f"페르소나 분석 결과 B안이 {ctr_b:.1%}의 CTR을 보입니다."
    
    return ctr_a, ctr_b, reasons_a, reasons_b

# -----------------------------
# KNN 팔로우
# -----------------------------

def _knn_follow(category: str, ages: List[str], genders: List[str], interests: str, A: str, B: str, k: int = 5, tau_hard: float = 0.9) -> Dict[str, Any]:
    """과거 유사 상황 팔로우 (빠른 처리)"""
    # 간단한 시뮬레이션으로 속도 향상
    if random.random() < 0.2:  # 20% 확률로 하드 팔로우만
        return {
            "mode": "hard",
            "follow_class": random.choice(["A", "B"])
        }
    return {"mode": "none"}  # 대부분의 경우 팔로우 없음

# -----------------------------
# 제3문구 생성
# -----------------------------

def generate_third_copy(req: PredictRequest, winner_keywords: str, winner_class: str) -> str:
    """승자 요인을 반영한 제3문구 생성"""
    if not winner_keywords:
        winner_keywords = "트렌디, 혁신"
    
    # 카테고리별 기본 문구
    category_templates = {
        "뷰티": f"'{winner_keywords}'의 핵심 가치를 담아 더욱 매력적인 {req.category} 경험을 선사해요",
        "패션": f"'{winner_keywords}'의 트렌드를 반영한 독특한 {req.category} 스타일을 제안해요",
        "식품": f"'{winner_keywords}'의 맛과 건강을 모두 만족시키는 {req.category}를 경험해보세요",
        "전자제품": f"'{winner_keywords}'의 혁신 기술로 더 스마트한 {req.category} 라이프를 시작하세요",
        "홈리빙": f"'{winner_keywords}'의 편리함과 아름다움을 담은 {req.category}로 공간을 완성하세요"
    }
    
    template = category_templates.get(req.category, f"'{winner_keywords}'의 장점을 결합한 {req.category} 솔루션을 제공해요")
    
    return template

# -----------------------------
# CTR 캘리브레이션
# -----------------------------

def calibrate_ctr(ctr: float, category: str, shrink: float = 0.35) -> float:
    """카테고리별 CTR 캘리브레이션"""
    if category not in CALIBRATION:
        category = "기타"
    
    e = CALIBRATION[category]
    calibrated = e["min"] + (e["max"] - e["min"]) * ctr * (1 - shrink)
    
    return float(max(e["min"], min(e["max"], calibrated)))
