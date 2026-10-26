"""ステータス計算（SPEC「ステータス成長システム」「完了とステータス」）。

今週のステータスは保存せず、今週の完了記録から毎回計算する。
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime

STATS = ("STR", "INT", "VIT", "DEX", "MND")
STAT_MAX = 80
DAILY_LIMIT = 3
DAY_MULT = (1.0, 0.67, 0.33)


def base_gain(value: int) -> int:
    if value >= 80:
        return 0
    if value >= 68:
        return 1
    if value >= 55:
        return 2
    if value >= 40:
        return 3
    if value >= 20:
        return 4
    return 5


def round_half_up(x: float) -> int:
    # Python の round は偶数丸めなので、SPEC の「四捨五入」に合わせて自前で丸める
    return int(x + 0.5)


@dataclass(frozen=True)
class Completion:
    task_id: int
    category: str
    completed_at: datetime
    local_date: date


@dataclass(frozen=True)
class Gain:
    amount: int
    capped: bool  # その日そのカテゴリで上限（3件）を超えていたため加算なし


@dataclass
class WeekResult:
    stats: dict[str, int] = field(default_factory=lambda: dict.fromkeys(STATS, 0))
    gains: dict[int, Gain] = field(default_factory=dict)
    counts_by_day: dict[tuple[date, str], int] = field(default_factory=lambda: defaultdict(int))

    def remaining_today(self, today: date) -> dict[str, int]:
        return {s: max(0, DAILY_LIMIT - self.counts_by_day[(today, s)]) for s in STATS}


def compute_week(completions: list[Completion]) -> WeekResult:
    """今週の完了記録を完了した順に並べ、成長テーブルと日次乗数を当てはめる。"""
    result = WeekResult()
    for c in sorted(completions, key=lambda c: (c.completed_at, c.task_id)):
        n = result.counts_by_day[(c.local_date, c.category)]
        result.counts_by_day[(c.local_date, c.category)] = n + 1
        if n >= DAILY_LIMIT:
            result.gains[c.task_id] = Gain(0, capped=True)
            continue
        current = result.stats[c.category]
        amount = min(round_half_up(base_gain(current) * DAY_MULT[n]), STAT_MAX - current)
        result.stats[c.category] = current + amount
        result.gains[c.task_id] = Gain(amount, capped=False)
    return result
