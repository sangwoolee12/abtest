import json
import time
import os
from typing import List, Dict, Any
from .config import RESULTS_PATH

# -----------------------------
# JSONL 파일 처리
# -----------------------------

def append_jsonl(filepath: str, data: Dict[str, Any]) -> None:
    """JSONL 파일에 데이터 추가"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

def _load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """JSONL 파일 로드"""
    if not os.path.exists(filepath):
        return []
    
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data

def update_user_choice_inplace(log_id: str, user_final_text: str) -> bool:
    """사용자 최종 선택을 인플레이스로 업데이트"""
    try:
        data = _load_jsonl(RESULTS_PATH)
        updated = False
        
        for i, row in enumerate(data):
            if row.get("log_id") == log_id:
                data[i]["user_final_text"] = user_final_text
                updated = True
                break
        
        if updated:
            # 파일에 다시 쓰기
            with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
                for row in data:
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')
            return True
        
        return False
    except Exception as e:
        print(f"사용자 선택 업데이트 실패: {e}")
        return False

# -----------------------------
# 텍스트 처리
# -----------------------------

def _cleanup_text(text: str) -> str:
    """텍스트 정리"""
    if not text:
        return ""
    # 따옴표 제거
    text = text.strip().strip('"').strip("'")
    # 줄바꿈 정리
    text = text.replace('\n', ' ').replace('\r', ' ')
    # 연속 공백 제거
    text = ' '.join(text.split())
    return text

def _feature_sentence(category: str, age_groups: List[str], genders: List[str], interests: str, marketing_a: str, marketing_b: str) -> str:
    """특징 문장 생성"""
    parts = []
    if category:
        parts.append(f"카테고리: {category}")
    if age_groups:
        parts.append(f"연령대: {', '.join(age_groups)}")
    if genders:
        parts.append(f"성별: {', '.join(genders)}")
    if interests:
        parts.append(f"관심사: {interests}")
    parts.append(f"마케팅A: {marketing_a}")
    parts.append(f"마케팅B: {marketing_b}")
    return " | ".join(parts)

# -----------------------------
# 클래스 분류
# -----------------------------

def _to_class(row: Dict[str, Any]) -> str:
    """최종 선택을 클래스로 변환"""
    final_text = row.get("user_final_text", "")
    if not final_text:
        return "N/A"
    
    marketing_a = row.get("marketing_a", "")
    marketing_b = row.get("marketing_b", "")
    
    if final_text == marketing_a:
        return "A"
    elif final_text == marketing_b:
        return "B"
    else:
        return "C"  # AI 생성 또는 기타
