import json
from typing import Dict, Any
from .models import PredictRequest
from .utils import _cleanup_text

# LLM 프롬프트 생성
def _build_prompt(req: PredictRequest) -> str:
    """A안, B안 분석을 위한 프롬프트 생성 - 더 자연스럽고 전문적으로 개선"""
    prompt = f"""
너는 30년 경력의 A/B 테스트 마케팅 전문가야. 두 개의 마케팅 문구를 비교 분석해줘.

제품 카테고리: {req.category}
타겟 연령대: {', '.join(req.age_groups or [])}
타겟 성별: {', '.join(req.genders or [])}
관심사: {req.interests or '없음'}

마케팅 문구:
A안: {req.marketing_a}
B안: {req.marketing_b}

**분석 요구사항:**
1. 각 문구의 강점과 약점을 객관적으로 분석
2. 타겟 고객층에 미칠 영향 예측
3. A/B 테스트 관점에서의 성과 전망
4. 실제 마케팅 현장에서의 활용 가능성

다음 형식으로 분석해줘:
{{
    "ctr_a": 0.0-1.0 사이의 값,
    "ctr_b": 0.0-1.0 사이의 값,
    "analysis_a": "A안에 대한 상세 분석 (한국어, 300자 이상, 자연스러운 해요체 사용, 전문적이되 친근한 톤)",
    "analysis_b": "B안에 대한 상세 분석 (한국어, 300자 이상, 자연스러운 해요체 사용, 전문적이되 친근한 톤)",
    "ai_suggestion": "A/B 테스트 결과를 바탕으로 한 마케팅 전략 제안 (한국어, 300자 이상, 실무에 바로 적용 가능한 수준)"
}}

**중요:**
- 반드시 위 JSON 형식으로만 응답
- 분석은 전문적이되 자연스럽게
- 과장이나 허위 표현 금지
- 실제 마케팅 현장에서 사용할 수 있는 수준의 분석
"""
    return prompt

def _build_c_analysis_prompt(req: PredictRequest, third_copy: str) -> str:
    """C안 분석을 위한 프롬프트 생성 - A/B안과 동일한 기준으로 통일"""
    prompt = f"""
너는 30년 경력의 A/B 테스트 마케팅 전문가야. AI가 생성한 새로운 마케팅 문구(C안)를 분석해줘.

제품 카테고리: {req.category}
타겟 연령대: {', '.join(req.age_groups or [])}
타겟 성별: {', '.join(req.genders or [])}
관심사: {req.interests or '없음'}

기존 마케팅 문구:
A안: {req.marketing_a}
B안: {req.marketing_b}

AI 생성 마케팅 문구 (C안): {third_copy}

**분석 요구사항:**
1. C안의 강점과 약점을 객관적으로 분석
2. A안, B안과의 차별점과 시너지 효과 평가
3. 타겟 고객층에 미칠 영향 예측
4. 실제 마케팅 성과에 대한 현실적인 전망

다음 형식으로 분석해주세요:
{{
    "analysis_c": "C안에 대한 상세 분석 (한국어, 300자 이상, 자연스러운 해요체 사용, 전문적이되 친근한 톤)"
}}

**중요:**
- 반드시 위 JSON 형식으로만 응답
- 분석은 전문적이되 자연스럽게
- 과장이나 허위 표현 금지
- 실제 마케팅 현장에서 사용할 수 있는 수준의 분석
"""
    return prompt

# LLM 응답 처리
def _clean_llm_response(result: str) -> str:
    """LLM 응답에서 마크다운 형식 제거 및 Python 딕셔너리를 JSON으로 변환"""
    cleaned_result = result.strip()
    
    # 마크다운 코드 블록 제거
    if cleaned_result.startswith('```json'):
        cleaned_result = cleaned_result[7:]  # ```json 제거
    elif cleaned_result.startswith('```'):
        cleaned_result = cleaned_result[3:]  # ``` 제거
    if cleaned_result.endswith('```'):
        cleaned_result = cleaned_result[:-3]  # ``` 제거
    
    cleaned_result = cleaned_result.strip()
    
    # Python 딕셔너리를 JSON으로 변환
    try:
        # ast.literal_eval로 안전하게 Python 딕셔너리 파싱
        import ast
        parsed_dict = ast.literal_eval(cleaned_result)
        import json
        return json.dumps(parsed_dict, ensure_ascii=False)
    except:
        # 변환 실패 시 원본 반환
        return cleaned_result

def _parse_llm_response(result: str, response_type: str = "analysis") -> Dict[str, Any]:
    """LLM 응답 파싱"""
    try:
        cleaned_result = _clean_llm_response(result)
        print(f"[DEBUG] 정리된 응답: {cleaned_result[:300]}...")
        
        # JSON 파싱 시도
        try:
            data = json.loads(cleaned_result)
        except json.JSONDecodeError as json_err:
            print(f"[DEBUG] JSON 파싱 실패: {json_err}")
            # Python 딕셔너리로 직접 파싱 시도
            try:
                import ast
                data = ast.literal_eval(cleaned_result)
                print(f"[DEBUG] Python 딕셔너리 파싱 성공")
            except Exception as ast_err:
                print(f"[DEBUG] Python 딕셔너리 파싱도 실패: {ast_err}")
                raise Exception(f"응답 형식 파싱 실패: {json_err}, {ast_err}")
        
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
        print(f"원본 응답: {result[:300]}...")
        print(f"정리된 응답: {cleaned_result[:300]}...")
        raise Exception(f"LLM 응답 파싱 실패: {e}")

# 로컬 분석 생성 함수들은 제거됨 - 이제 무조건 LLM 사용
