from ..config import TASK_ANALYZER
from .base import TaskAnalyzer


def get_analyzer() -> TaskAnalyzer | None:
    """設定されたタスク解析を返す。未設定（"none"）なら None で、画面ではカテゴリを手で選ぶ。"""
    if TASK_ANALYZER == "none":
        return None
    raise ValueError(f"未対応の TASK_ANALYZER です: {TASK_ANALYZER}")
