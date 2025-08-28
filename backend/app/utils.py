import json
import os
import tempfile
import shutil
from typing import Any, Dict, List, Optional

from .config import RESULTS_PATH

# -------------------------------------------------
# 공통 텍스트 유틸 (llm_utils 등에서 사용)
# -------------------------------------------------
def _cleanup_text(s: Optional[str]) -> str:
    if not s:
        return ""
    return " ".join(str(s).split())

# -------------------------------------------------
# JSONL 입출력
# -------------------------------------------------
def append_jsonl(path: str, obj: Dict[str, Any]) -> None:
    """JSONL 파일에 한 줄 추가 (경로 생성 포함)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    """JSONL 파일을 리스트로 로드. 손상된 라인은 건너뜀."""
    out: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                # 손상된 라인은 무시
                continue
    return out

# -------------------------------------------------
# user_final_text 업데이트 (핵심)
# -------------------------------------------------
def update_user_choice_inplace(log_id: str, user_final_text: str) -> bool:
    """
    RESULTS_PATH(JSONL)에서 주어진 log_id 레코드를 찾아
    user_final_text를 사용자가 고른 문구로 업데이트한다.

    보완:
    - log_id 비교 시 str/공백 안전화
    - user_final_text가 "A"|"B"|"C"로 온 경우, 해당 레코드의
      marketing_a / marketing_b / ai_generated_text 실제 문구로 치환
    - 임시 파일로 원자적 교체
    """
    if not log_id:
        return False
    if not isinstance(user_final_text, str) or not user_final_text.strip():
        return False
    if not os.path.exists(RESULTS_PATH):
        return False

    key = str(log_id).strip()
    updated = False
    dirpath = os.path.dirname(RESULTS_PATH) or "."
    os.makedirs(dirpath, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(prefix="results_", suffix=".jsonl", dir=dirpath, text=True)
    os.close(fd)

    try:
        with open(RESULTS_PATH, "r", encoding="utf-8") as rf, open(tmp_path, "w", encoding="utf-8") as wf:
            for raw in rf:
                line = raw.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    # 손상 라인은 그대로 유지
                    wf.write(raw)
                    continue

                rec_log_id = str(rec.get("log_id", "")).strip()
                if (not updated) and rec_log_id == key:
                    uft = user_final_text.strip()
                    if uft in ("A", "B", "C"):
                        A = (rec.get("marketing_a") or "").strip()
                        B = (rec.get("marketing_b") or "").strip()
                        C = (rec.get("ai_generated_text") or "").strip()
                        rec["user_final_text"] = A if uft == "A" else (B if uft == "B" else C)
                    else:
                        rec["user_final_text"] = uft
                    updated = True
                    wf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                else:
                    wf.write(json.dumps(rec, ensure_ascii=False) + "\n")

        shutil.move(tmp_path, RESULTS_PATH)
    except Exception:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return False

    return updated

# -------------------------------------------------
# rebuild-index용 간단 피처/클래스 유틸
# -------------------------------------------------
def _feature_sentence(category: str,
                      ages: List[str],
                      genders: List[str],
                      interests: str,
                      A: str,
                      B: str,
                      C: str) -> str:
    """인덱스 구축용 간단 텍스트 피처."""
    cat = _cleanup_text(category)
    ag = _cleanup_text(" ".join(ages or []))
    gd = _cleanup_text(" ".join(genders or []))
    it = _cleanup_text(interests)
    a = _cleanup_text(A)
    b = _cleanup_text(B)
    c = _cleanup_text(C)
    return f"[cat]{cat} [ages]{ag} [genders]{gd} [interests]{it} [A]{a} [B]{b} [C]{c}"

def _to_class(r: Dict[str, Any]) -> str:
    """
    결과 레코드에서 최종 선택 클래스를 유추(A/B/C/USER/NONE).
    """
    final = (r.get("user_final_text") or "").strip()
    if not final:
        return "NONE"

    A = (r.get("marketing_a") or "").strip()
    B = (r.get("marketing_b") or "").strip()
    C = (r.get("ai_generated_text") or "").strip()

    if final == A:
        return "A"
    if final == B:
        return "B"
    if final == C:
        return "C"
    return "USER"
