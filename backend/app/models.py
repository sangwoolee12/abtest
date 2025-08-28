from pydantic import BaseModel
from typing import List, Optional
import time

# -----------------------------
# 요청/응답 모델
# -----------------------------

class PredictRequest(BaseModel):
    age_groups: Optional[List[str]] = None
    genders: Optional[List[str]] = None
    interests: Optional[str] = None
    category: Optional[str] = None
    marketing_a: str
    marketing_b: str

class PredictResponse(BaseModel):
    ctr_a: float
    ctr_b: float
    ctr_c: float
    analysis_a: str
    analysis_b: str
    analysis_c: str
    ai_suggestion: str
    ai_top_ctr_choice: Optional[str] = None
    log_id: Optional[str] = None

class ImageGenerationRequest(BaseModel):
    prompt: str
    n: int = 1
    size: str = "1024x1024"

class ImageGenerationResponse(BaseModel):
    images: List[str]

class UserChoiceIn(BaseModel):
    log_id: str
    user_final_text: str  # 사용자가 고른 실제 텍스트(A/B/제3 무엇이든 문자열)

# -----------------------------
# 저장용 모델
# -----------------------------

class ABTestStoredResult(BaseModel):
    log_id: str
    timestamp: float
    age_groups: List[str]
    genders: List[str]
    interests: str
    category: str
    marketing_a: str
    marketing_b: str
    pred_ctr_a: float
    pred_ctr_b: float
    pred_ctr_c: float
    ai_generated_text: str
    ai_top_ctr_choice: str
    user_final_text: Optional[str] = None

# -----------------------------
# 페르소나 모델
# -----------------------------

class Persona(BaseModel):
    age_group: str
    gender: str
    interests: str
    description: str
    keywords: List[str]
