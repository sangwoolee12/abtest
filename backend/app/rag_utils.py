import json
import os
from typing import List, Dict, Any, Optional
from .models import PredictRequest
from .business_logic import _call_gemini_with_retry

class RAGSystem:
    """RAG(Retrieval-Augmented Generation) 시스템"""
    
    def __init__(self, results_path: str = "data/abtest_results.jsonl"):
        self.results_path = results_path
        self._cache = None
        self._cache_timestamp = 0
    
    def _load_results(self) -> List[Dict[str, Any]]:
        """결과 로그 로드 (캐싱 포함)"""
        try:
            if not os.path.exists(self.results_path):
                return []
            
            # 파일 수정 시간 확인
            current_timestamp = os.path.getmtime(self.results_path)
            if self._cache and current_timestamp <= self._cache_timestamp:
                return self._cache
            
            with open(self.results_path, 'r', encoding='utf-8') as f:
                results = []
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            results.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                
                self._cache = results
                self._cache_timestamp = current_timestamp
                return results
        except Exception as e:
            print(f"[RAG] 결과 로드 실패: {e}")
            return []
    
    def _find_relevant_examples(self, req: PredictRequest, top_k: int = 5) -> List[Dict[str, Any]]:
        """요청과 관련된 예시 찾기"""
        results = self._load_results()
        if not results:
            return []
        
        # 사용자 선택이 있는 결과만 필터링
        user_choices = [r for r in results if r.get("user_final_text")]
        if not user_choices:
            return []
        
        # 카테고리, 연령대, 성별 기반 유사도 계산
        relevant_examples = []
        for example in user_choices:
            score = 0
            
            # 카테고리 매칭
            if example.get("category") == req.category:
                score += 3
            
            # 연령대 매칭
            if req.age_groups and example.get("age_groups"):
                for age in req.age_groups:
                    if age in example["age_groups"]:
                        score += 2
                        break
            
            # 성별 매칭
            if req.genders and example.get("genders"):
                for gender in req.genders:
                    if gender in example["genders"]:
                        score += 2
                        break
            
            # 관심사 키워드 매칭
            if req.interests and example.get("interests"):
                req_interests = req.interests.lower().split(', ')
                example_interests = example["interests"].lower().split(', ')
                for interest in req_interests:
                    if any(interest in ex_interest for ex_interest in example_interests):
                        score += 1
            
            if score > 0:
                relevant_examples.append({
                    "example": example,
                    "score": score
                })
        
        # 점수 순으로 정렬하고 top_k 반환
        relevant_examples.sort(key=lambda x: x["score"], reverse=True)
        return [ex["example"] for ex in relevant_examples[:top_k]]
    
    def generate_rag_enhanced_analysis(self, req: PredictRequest, 
                                     base_analysis: str,
                                     relevant_examples: Optional[List[Dict[str, Any]]] = None) -> str:
        """RAG를 활용한 향상된 분석 생성"""
        if not relevant_examples:
            relevant_examples = self._find_relevant_examples(req)
        
        if not relevant_examples:
            return base_analysis
        
        # 관련 예시 정보 구성
        examples_text = []
        for i, example in enumerate(relevant_examples, 1):
            example_text = f"""
예시 {i}:
- 카테고리: {example.get('category', 'N/A')}
- 타겟: {', '.join(example.get('age_groups', []))} {', '.join(example.get('genders', []))}
- A안: {example.get('marketing_a', 'N/A')}
- B안: {example.get('marketing_b', 'N/A')}
- C안: {example.get('ai_generated_text', 'N/A')}
- 사용자 선택: {example.get('user_final_text', 'N/A')}
- 예측 CTR: A({example.get('pred_ctr_a', 0):.1%}), B({example.get('pred_ctr_b', 0):.1%}), C({example.get('pred_ctr_c', 0):.1%})
"""
            examples_text.append(example_text)
        
        # RAG 프롬프트 생성
        prompt = f"""
너는 30년 경력의 A/B 테스트 마케팅 전문가야. 다음 정보를 바탕으로 향상된 분석을 제공해줘.

현재 분석 대상:
- 카테고리: {req.category or '일반'}
- 타겟: {', '.join(req.age_groups or [])} {', '.join(req.genders or [])}
- 관심사: {req.interests or '없음'}
- A안: {req.marketing_a}
- B안: {req.marketing_b}

기존 분석:
{base_analysis}

과거 유사 사례 (사용자 실제 선택 결과):
{chr(10).join(examples_text)}

위 과거 사례를 참고하여 기존 분석을 더욱 정확하고 실용적으로 개선해주세요.
과거 사용자들의 실제 선택 패턴과 성과를 반영하여 분석의 신뢰도를 높여주세요.

반드시 다음 형식으로만 응답해주세요:
{{
    "enhanced_analysis": "향상된 분석 내용 (한국어, 400자 이상, 해요체 사용)"
}}

중요: 반드시 위 JSON 형식으로만 응답해주세요. 다른 설명이나 텍스트는 절대 포함하지 마세요.
모든 키와 문자열 값은 따옴표로 감싸주세요.
"""
        
        try:
            data = _call_gemini_with_retry(prompt, max_retries=3)
            if data and "enhanced_analysis" in data:
                return data["enhanced_analysis"]
        except Exception as e:
            print(f"[RAG] 향상된 분석 생성 실패: {e}")
        
        return base_analysis
    
    def get_insights_from_logs(self, category: Optional[str] = None) -> Dict[str, Any]:
        """로그 데이터에서 인사이트 추출"""
        results = self._load_results()
        if not results:
            return {}
        
        # 사용자 선택이 있는 결과만 필터링
        user_choices = [r for r in results if r.get("user_final_text")]
        if not user_choices:
            return {}
        
        # 카테고리별 필터링
        if category:
            user_choices = [r for r in user_choices if r.get("category") == category]
        
        if not user_choices:
            return {}
        
        # 통계 계산
        total_choices = len(user_choices)
        choice_counts = {"A": 0, "B": 0, "C": 0}
        category_performance = {}
        
        for choice in user_choices:
            # 어떤 옵션을 선택했는지 판단
            user_text = choice["user_final_text"]
            if user_text == choice.get("marketing_a"):
                choice_counts["A"] += 1
            elif user_text == choice.get("marketing_b"):
                choice_counts["B"] += 1
            elif user_text == choice.get("ai_generated_text"):
                choice_counts["C"] += 1
            
            # 카테고리별 성과
            cat = choice.get("category", "기타")
            if cat not in category_performance:
                category_performance[cat] = {"total": 0, "success_rate": 0}
            category_performance[cat]["total"] += 1
        
        # 성공률 계산 (예측 CTR과 실제 선택의 일치도)
        success_count = 0
        for choice in user_choices:
            pred_winner = "A" if choice.get("pred_ctr_a", 0) >= choice.get("pred_ctr_b", 0) else "B"
            if choice.get("pred_ctr_c", 0) > max(choice.get("pred_ctr_a", 0), choice.get("pred_ctr_b", 0)):
                pred_winner = "C"
            
            actual_winner = "A" if choice["user_final_text"] == choice.get("marketing_a") else "B"
            if choice["user_final_text"] == choice.get("ai_generated_text"):
                actual_winner = "C"
            
            if pred_winner == actual_winner:
                success_count += 1
        
        return {
            "total_choices": total_choices,
            "choice_distribution": choice_counts,
            "prediction_accuracy": success_count / total_choices if total_choices > 0 else 0,
            "category_performance": category_performance,
            "recent_trends": user_choices[-10:] if len(user_choices) > 10 else user_choices
        }

# 전역 RAG 시스템 인스턴스
rag_system = RAGSystem()
