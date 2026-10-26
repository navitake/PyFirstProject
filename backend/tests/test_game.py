from datetime import date, datetime, timedelta

from app.game import Completion, base_gain, compute_week

MON = date(2026, 10, 26)


def completions(category: str, per_day: list[int]) -> list[Completion]:
    """per_day[i] 件を i 日目に完了したことにする"""
    out = []
    task_id = 0
    for day, n in enumerate(per_day):
        d = MON + timedelta(days=day)
        for i in range(n):
            task_id += 1
            out.append(Completion(task_id, category, datetime(d.year, d.month, d.day, 1, i), d))
    return out


def test_base_gain_table():
    assert [base_gain(v) for v in (0, 19, 20, 39, 40, 54, 55, 67, 68, 79, 80)] == [
        5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0,
    ]


def test_daily_multiplier_matches_spec():
    # SPEC: 0〜19 の帯は 1件目+5 / 2件目+3 / 3件目+2、4件目以降は加算なし
    result = compute_week(completions("STR", [4]))
    assert [result.gains[i].amount for i in (1, 2, 3, 4)] == [5, 3, 2, 0]
    assert result.gains[4].capped
    assert result.stats["STR"] == 10


def test_growth_per_day_at_three_tasks():
    # SPEC「主要しきい値への到達目安」: 1日3件ずつ続けたときの各日の終わりの値
    expected = [10, 20, 28, 36, 43, 49, 55]
    for days, value in enumerate(expected, start=1):
        assert compute_week(completions("STR", [3] * days)).stats["STR"] == value


def test_growth_per_day_at_one_task():
    expected = [5, 10, 15, 20, 24, 28, 32]
    for days, value in enumerate(expected, start=1):
        assert compute_week(completions("STR", [1] * days)).stats["STR"] == value


def test_daily_limit_is_per_category():
    week = completions("STR", [3]) + [
        Completion(100, "INT", datetime(2026, 10, 26, 2, 0), MON),
    ]
    result = compute_week(week)
    assert result.stats == {"STR": 10, "INT": 5, "VIT": 0, "DEX": 0, "MND": 0}
    assert result.remaining_today(MON) == {"STR": 0, "INT": 2, "VIT": 3, "DEX": 3, "MND": 3}


def test_stat_caps_at_80():
    # 1週間では 80 に届かないので、日数を増やして上限で止まることだけ確かめる
    result = compute_week(completions("MND", [3] * 30))
    assert result.stats["MND"] == 80
