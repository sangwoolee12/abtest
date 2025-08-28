import json
from typing import Dict, Any
from .models import PredictRequest
from .utils import _cleanup_text

# LLM 프롬프트 생성
def _build_prompt(req: PredictRequest) -> str:
    """A안, B안 분석을 위한 프롬프트 생성"""
    prompt = f"""
너는 30년 경력의 A/B 테스트 마케팅 전문가야. 다음 마케팅 문구 A안과 B안을 분석해줘.

제품 카테고리: {req.category}
타겟 연령대: {', '.join(req.age_groups or [])}
타겟 성별: {', '.join(req.genders or [])}
관심사: {req.interests or '없음'}

마케팅 문구:
A안: {req.marketing_a}
B안: {req.marketing_b}

다음 형식으로 분석해줘:
{{
    "ctr_a": 0.0-1.0 사이의 값,
    "ctr_b": 0.0-1.0 사이의 값,
    "analysis_a": "A안에 대한 상세 분석 (한국어, 300자 이상, 해요체 사용)",
    "analysis_b": "B안에 대한 상세 분석 (한국어, 300자 이상, 해요체 사용)",
    "ai_suggestion": "AI 제안사항 (한국어, 300자 이상, 해요체 사용)"
}}

JSON 형식으로만 응답해줘.
"""
    return prompt

def _build_c_analysis_prompt(req: PredictRequest, third_copy: str) -> str:
    """C안 분석을 위한 프롬프트 생성"""
    prompt = f"""
너는 30년 경력의 A/B 테스트 마케팅 전문가야. 다음 마케팅 문구 A안과 B안을 분석해줘.

제품 카테고리: {req.category}
타겟 연령대: {', '.join(req.age_groups or [])}
타겟 성별: {', '.join(req.genders or [])}
관심사: {req.interests or '없음'}

AI 생성 마케팅 문구: {third_copy}

다음 형식으로 분석해주세요:
{{
    "analysis_c": "C안에 대한 상세 분석 (한국어, 300자 이상, 해요체 사용)"
}}

중요: 반드시 위 JSON 형식으로만 응답해주세요. 다른 설명이나 텍스트는 절대 포함하지 마세요.
모든 키와 문자열 값은 따옴표로 감싸주세요.
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
