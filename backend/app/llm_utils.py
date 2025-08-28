import json
from typing import Dict, Any
from .models import PredictRequest
from .utils import _cleanup_text

# -----------------------------
# LLM 프롬프트 생성
# -----------------------------

def _build_prompt(req: PredictRequest) -> str:
    """A안, B안 분석을 위한 프롬프트 생성"""
    prompt = f"""
당신은 A/B 테스트 마케팅 전문가입니다. 다음 마케팅 문구 A안과 B안을 분석해주세요.

제품 카테고리: {req.category}
타겟 연령대: {', '.join(req.age_groups or [])}
타겟 성별: {', '.join(req.genders or [])}
관심사: {req.interests or '없음'}

마케팅 문구:
A안: {req.marketing_a}
B안: {req.marketing_b}

다음 형식으로 분석해주세요:
{{
    "ctr_a": 0.0-1.0 사이의 값,
    "ctr_b": 0.0-1.0 사이의 값,
    "analysis_a": "A안에 대한 상세 분석 (한국어, 300자 이상)",
    "analysis_b": "B안에 대한 상세 분석 (한국어, 300자 이상)",
    "ai_suggestion": "AI 제안사항 (한국어, 300자 이상)"
}}

JSON 형식으로만 응답해주세요.
"""
    return prompt

def _build_c_analysis_prompt(req: PredictRequest, third_copy: str) -> str:
    """C안 분석을 위한 프롬프트 생성"""
    prompt = f"""
당신은 마케팅 전문가입니다. AI가 생성한 마케팅 문구를 분석해주세요.

제품 카테고리: {req.category}
타겟 연령대: {', '.join(req.age_groups or [])}
타겟 성별: {', '.join(req.genders or [])}
관심사: {req.interests or '없음'}

AI 생성 마케팅 문구: {third_copy}

다음 형식으로 분석해주세요:
{{
    "analysis_c": "C안에 대한 상세 분석 (한국어, 300자 내외, 해요체 사용)"
}}

JSON 형식으로만 응답해주세요.
"""
    return prompt

# -----------------------------
# LLM 응답 처리
# -----------------------------

def _clean_llm_response(result: str) -> str:
    """LLM 응답에서 마크다운 형식 제거"""
    cleaned_result = result.strip()
    if cleaned_result.startswith('```json'):
        cleaned_result = cleaned_result[7:]  # ```json 제거
    if cleaned_result.endswith('```'):
        cleaned_result = cleaned_result[:-3]  # ``` 제거
    return cleaned_result.strip()

def _parse_llm_response(result: str, response_type: str = "analysis") -> Dict[str, Any]:
    """LLM 응답 파싱"""
    try:
        cleaned_result = _clean_llm_response(result)
        data = json.loads(cleaned_result)
        
        if response_type == "analysis":
            return {
                "ctr_a": float(data["ctr_a"]),
                "ctr_b": float(data["ctr_b"]),
                "analysis_a": _cleanup_text(str(data["analysis_a"])),
                "analysis_b": _cleanup_text(str(data["analysis_b"])),
                "ai_suggestion": _cleanup_text(str(data["ai_suggestion"]))
            }
        elif response_type == "c_analysis":
            return {
                "analysis_c": _cleanup_text(str(data["analysis_c"]))
            }
        else:
            raise ValueError(f"Unknown response type: {response_type}")
            
    except Exception as e:
        print(f"LLM 응답 파싱 실패: {e}")
        print(f"응답 내용: {result[:200]}...")
        print(f"정리된 응답: {cleaned_result[:200]}...")
        raise Exception(f"LLM 응답 파싱 실패: {e}")

# -----------------------------
# 로컬 분석 생성
# -----------------------------

def _generate_local_c_analysis(req: PredictRequest, third_copy: str, ctr_c: float, ctr_a: float, ctr_b: float):
    """로컬에서 C안 분석 생성 (LLM 실패 시)"""
    try:
        # 간단한 로컬 분석 생성
        if ctr_c > max(ctr_a, ctr_b):
            analysis = f"AI가 생성한 마케팅 문구는 기존 A안과 B안의 장점을 결합하여 {ctr_c:.1%}의 높은 CTR을 예상합니다. 타겟 고객층의 니즈에 더욱 부합하는 메시지를 전달해요."
        else:
            analysis = f"AI가 생성한 마케팅 문구는 {ctr_c:.1%}의 CTR을 예상합니다. 기존 문구들과 비교하여 경쟁력 있는 접근을 시도해요."
        
        return type('C_Analysis', (), {'analysis_c': analysis})()
        
    except Exception as e:
        print(f"로컬 C안 분석 생성 실패: {e}")
        # 기본값 반환
        return type('C_Analysis', (), {'analysis_c': f"AI가 생성한 마케팅 문구: {third_copy}"})()

def _generate_local_c_analysis_text(req: PredictRequest, third_copy: str, ctr_c: float, ctr_a: float, ctr_b: float) -> str:
    """로컬에서 C안 분석 텍스트 생성 (LLM 실패 시)"""
    try:
        if ctr_c > max(ctr_a, ctr_b):
            return f"AI가 생성한 마케팅 문구는 기존 A안과 B안의 장점을 결합하여 {ctr_c:.1%}의 높은 CTR을 예상합니다. 타겟 고객층의 니즈에 더욱 부합하는 메시지를 전달해요."
        else:
            return f"AI가 생성한 마케팅 문구는 {ctr_c:.1%}의 CTR을 예상합니다. 기존 문구들과 비교하여 경쟁력 있는 접근을 시도해요."
    except Exception as e:
        print(f"로컬 C안 분석 텍스트 생성 실패: {e}")
        return f"AI가 생성한 마케팅 문구: {third_copy}"
