import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# -----------------------------
# API 설정
# -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
EMBED_MODEL = "models/embedding-001"

# -----------------------------
# 파일 경로
# -----------------------------
RESULTS_PATH = "data/abtest_results.jsonl"

# -----------------------------
# 페르소나 데이터 (TargetScreen과 일치)
# -----------------------------
PERSONAS = [
    {
        "id": "p1",
        "name": "뷰티/화장품",
        "age_group": "20대",
        "gender": "여성",
        "interests": "생활, 노하우, 쇼핑",
        "categories": "뷰티, 화장품, 스킨케어",
        "description": "뷰티와 화장품에 관심이 많고 트렌드를 추구하는 20대 여성",
        "keywords": ["뷰티", "화장품", "스킨케어", "메이크업", "트렌드", "쇼핑", "생활"]
    },
    {
        "id": "p2",
        "name": "게임",
        "age_group": "20대",
        "gender": "남성",
        "interests": "취미, 여가, 여행",
        "categories": "게임, 전자제품, 엔터테인먼트",
        "description": "게임과 전자제품에 관심이 많고 새로운 기술을 추구하는 20대 남성",
        "keywords": ["게임", "전자제품", "엔터테인먼트", "기술", "취미", "여가", "여행"]
    },
    {
        "id": "p3",
        "name": "패션/잡화",
        "age_group": "30대",
        "gender": "여성",
        "interests": "생활, 노하우, 쇼핑",
        "categories": "패션, 액세서리, 라이프스타일",
        "description": "패션과 라이프스타일에 관심이 많고 실용적인 소비를 선호하는 30대 여성",
        "keywords": ["패션", "액세서리", "라이프스타일", "생활", "노하우", "쇼핑", "스타일"]
    },
    {
        "id": "p4",
        "name": "부동산/재테크",
        "age_group": "30대",
        "gender": "남성",
        "interests": "지식, 동향",
        "categories": "부동산, 투자, 금융",
        "description": "부동산과 투자에 관심이 많고 경제적 안정을 추구하는 30대 남성",
        "keywords": ["부동산", "투자", "금융", "지식", "동향", "경제", "안정"]
    },
    {
        "id": "p5",
        "name": "여행/숙박/항공",
        "age_group": "40대",
        "gender": "여성",
        "interests": "취미, 여가, 여행",
        "categories": "여행, 숙박, 항공",
        "description": "여행과 여가를 중시하고 새로운 경험을 추구하는 40대 여성",
        "keywords": ["여행", "숙박", "항공", "취미", "여가", "경험", "휴식"]
    },
    {
        "id": "p6",
        "name": "스포츠/레저",
        "age_group": "40대",
        "gender": "남성",
        "interests": "취미, 여가, 여행",
        "categories": "스포츠, 아웃도어, 레저",
        "description": "스포츠와 아웃도어 활동을 즐기고 건강한 라이프스타일을 추구하는 40대 남성",
        "keywords": ["스포츠", "아웃도어", "레저", "건강", "취미", "여가", "활동"]
    },
    {
        "id": "p7",
        "name": "식음료/요리",
        "age_group": "50대",
        "gender": "여성",
        "interests": "생활, 노하우, 쇼핑",
        "categories": "식음료, 요리",
        "description": "요리와 식음료에 관심이 많고 가족을 위한 맛있는 음식을 만드는 50대 여성",
        "keywords": ["식음료", "요리", "생활", "노하우", "가족", "맛", "건강"]
    },
    {
        "id": "p8",
        "name": "정치/사회",
        "age_group": "50대",
        "gender": "남성",
        "interests": "지식, 동향",
        "categories": "정치, 사회이슈, 뉴스",
        "description": "정치와 사회이슈에 관심이 많고 사회적 동향을 파악하는 50대 남성",
        "keywords": ["정치", "사회이슈", "뉴스", "지식", "동향", "사회", "정보"]
    }
]

# -----------------------------
# 카테고리별 CTR 캘리브레이션 (새로운 personas와 일치)
# -----------------------------
CALIBRATION = {
    "뷰티": {"min": 0.02, "max": 0.08, "shrink": 0.35},
    "화장품": {"min": 0.025, "max": 0.09, "shrink": 0.35},
    "스킨케어": {"min": 0.02, "max": 0.08, "shrink": 0.35},
    "게임": {"min": 0.02, "max": 0.06, "shrink": 0.35},
    "전자제품": {"min": 0.01, "max": 0.04, "shrink": 0.35},
    "엔터테인먼트": {"min": 0.015, "max": 0.05, "shrink": 0.35},
    "패션": {"min": 0.015, "max": 0.06, "shrink": 0.35},
    "액세서리": {"min": 0.02, "max": 0.07, "shrink": 0.35},
    "라이프스타일": {"min": 0.015, "max": 0.05, "shrink": 0.35},
    "부동산": {"min": 0.003, "max": 0.015, "shrink": 0.35},
    "투자": {"min": 0.008, "max": 0.025, "shrink": 0.35},
    "금융": {"min": 0.008, "max": 0.025, "shrink": 0.35},
    "여행": {"min": 0.015, "max": 0.05, "shrink": 0.35},
    "숙박": {"min": 0.015, "max": 0.05, "shrink": 0.35},
    "항공": {"min": 0.01, "max": 0.04, "shrink": 0.35},
    "스포츠": {"min": 0.015, "max": 0.05, "shrink": 0.35},
    "아웃도어": {"min": 0.015, "max": 0.05, "shrink": 0.35},
    "레저": {"min": 0.015, "max": 0.05, "shrink": 0.35},
    "식음료": {"min": 0.025, "max": 0.09, "shrink": 0.35},
    "요리": {"min": 0.02, "max": 0.07, "shrink": 0.35},
    "정치": {"min": 0.005, "max": 0.02, "shrink": 0.35},
    "사회이슈": {"min": 0.008, "max": 0.025, "shrink": 0.35},
    "뉴스": {"min": 0.008, "max": 0.025, "shrink": 0.35},
    "기타": {"min": 0.015, "max": 0.06, "shrink": 0.35}
}
