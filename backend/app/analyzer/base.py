"""タスク解析（分類・分解）の窓口。

使うモデルは比較して決める（SPEC「タスク解析に使うLLM」）ので、アプリ本体はこの窓口だけを使う。
API のモデルや自前の小型モデルは、この Protocol を満たすクラスとして追加する。
"""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class SubtaskSuggestion:
    title: str
    category: str


@dataclass(frozen=True)
class AnalysisResult:
    category: str
    subtasks: list[SubtaskSuggestion] = field(default_factory=list)  # 分解しない場合は空


class TaskAnalyzer(Protocol):
    name: str

    def analyze(self, text: str) -> AnalysisResult: ...
