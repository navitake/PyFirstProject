from datetime import datetime


def create(client, title="ジムに行く", category="STR", **kw):
    r = client.post("/api/tasks", json={"title": title, "category": category, **kw})
    assert r.status_code == 201, r.text
    return r.json()


def complete(client, task_id):
    r = client.post(f"/api/tasks/{task_id}/complete")
    assert r.status_code == 200, r.text
    return r.json()


def today_titles(client):
    return [t["title"] for t in client.get("/api/today").json()["tasks"]]


def test_complete_shows_gain_and_daily_cap(client):
    ids = [create(client, f"運動{i}", due_date="2026-10-26")["id"] for i in range(4)]
    gains = [complete(client, i)["gain"] for i in ids]
    assert [g["amount"] for g in gains] == [5, 3, 2, 0]
    assert gains[3]["capped"] is True
    stats = client.get("/api/stats").json()
    assert stats["stats"]["STR"] == 10
    assert stats["remaining_today"]["STR"] == 0


def test_uncomplete_reverts_stats_and_cannot_be_farmed(client):
    task = create(client)
    complete(client, task["id"])
    r = client.post(f"/api/tasks/{task['id']}/uncomplete").json()
    assert r["stats"]["stats"]["STR"] == 0
    for _ in range(5):  # 完了と取り消しを繰り返しても増えない
        complete(client, task["id"])
        client.post(f"/api/tasks/{task['id']}/uncomplete")
    assert complete(client, task["id"])["stats"]["stats"]["STR"] == 5


def test_deleting_completed_task_removes_its_gain(client):
    task = create(client)
    complete(client, task["id"])
    assert client.delete(f"/api/tasks/{task['id']}").status_code == 204
    assert client.get("/api/stats").json()["stats"]["STR"] == 0


def test_today_view_contents(client, clock):
    create(client, "期限なし")
    create(client, "今日まで", due_date="2026-10-26")
    create(client, "明日まで", due_date="2026-10-27")
    create(client, "昨日まで", due_date="2026-10-25")
    today = client.get("/api/today").json()["tasks"]
    titles = {t["title"]: t for t in today}
    assert set(titles) == {"今日まで", "昨日まで"}
    assert titles["昨日まで"]["overdue"] is True
    assert titles["今日まで"]["overdue"] is False


def test_completed_today_stays_visible_until_midnight(client, clock):
    task = create(client, "今日まで", due_date="2026-10-26")
    complete(client, task["id"])
    assert today_titles(client) == ["今日まで"]
    clock.set(datetime(2026, 10, 27, 0, 1))
    assert today_titles(client) == []


def test_all_tasks_sorted_by_due_date_with_undated_last(client):
    create(client, "期限なし")
    create(client, "来週", due_date="2026-11-02")
    create(client, "明日", due_date="2026-10-27")
    titles = [t["title"] for t in client.get("/api/tasks").json()]
    assert titles == ["明日", "来週", "期限なし"]


def test_week_resets_on_monday(client, clock):
    clock.set(datetime(2026, 11, 1, 23, 0))  # 日曜
    complete(client, create(client)["id"])
    assert client.get("/api/stats").json()["stats"]["STR"] == 5
    clock.set(datetime(2026, 11, 2, 0, 0))  # 月曜 0:00
    stats = client.get("/api/stats").json()
    assert stats["stats"]["STR"] == 0
    assert stats["week_start"] == "2026-11-02"


def test_day_boundary_uses_local_midnight(client, clock):
    # 日本時間 23:59 と 0:00 は別の日として数える（UTC では同じ日）
    clock.set(datetime(2026, 10, 27, 23, 59))
    for i in range(3):
        complete(client, create(client, f"a{i}")["id"])
    clock.set(datetime(2026, 10, 28, 0, 0))
    assert complete(client, create(client, "b")["id"])["gain"]["amount"] == 5


def test_recurring_creates_today_instance_only_on_matching_days(client, clock):
    r = client.post(
        "/api/recurring",
        json={"title": "ランニング", "category": "STR", "weekdays": [0, 2]},  # 月・水
    )
    assert r.status_code == 201
    assert today_titles(client) == ["ランニング"]  # 月曜
    assert today_titles(client) == ["ランニング"]  # 2回開いても増えない
    clock.set(datetime(2026, 10, 27, 9, 0))  # 火曜
    assert today_titles(client) == []
    clock.set(datetime(2026, 10, 28, 9, 0))  # 水曜
    assert today_titles(client) == ["ランニング"]


def test_missed_recurring_does_not_pile_up(client, clock):
    client.post("/api/recurring", json={"title": "読書", "category": "INT", "weekdays": list(range(7))})
    today_titles(client)  # 月曜の分を作るだけで完了しない
    clock.set(datetime(2026, 10, 27, 9, 0))
    assert today_titles(client) == ["読書"]  # 火曜の分だけ。月曜の分は持ち越さない
    assert [t["title"] for t in client.get("/api/tasks").json()] == ["読書"]


def test_stopping_recurring_removes_todays_open_instance(client):
    rule = client.post(
        "/api/recurring", json={"title": "瞑想", "category": "MND", "weekdays": [0]}
    ).json()
    assert today_titles(client) == ["瞑想"]
    client.patch(f"/api/recurring/{rule['id']}", json={"active": False})
    assert today_titles(client) == []


def test_deleting_recurring_keeps_completed_history(client):
    rule = client.post(
        "/api/recurring", json={"title": "料理", "category": "VIT", "weekdays": [0]}
    ).json()
    task_id = client.get("/api/today").json()["tasks"][0]["id"]
    complete(client, task_id)
    assert client.delete(f"/api/recurring/{rule['id']}").status_code == 204
    assert client.get("/api/stats").json()["stats"]["VIT"] == 5


def test_parent_task_is_not_counted(client):
    parent = create(client, "プレゼン資料を作る", "DEX")
    # 分解はLLM導入後に画面から行う。ここではデータとして親子を作って数え方だけ確かめる
    from app.db import get_db
    from app.main import app
    from app.models import Task

    db = next(app.dependency_overrides[get_db]())
    db.add(Task(title="構成を考える", category="DEX", parent_id=parent["id"], created_at=datetime(2026, 10, 26)))
    db.commit()
    assert complete(client, parent["id"])["gain"] is None
    assert client.get("/api/stats").json()["stats"]["DEX"] == 0


def test_validation(client):
    assert client.post("/api/tasks", json={"title": "", "category": "STR"}).status_code == 422
    assert client.post("/api/tasks", json={"title": "x", "category": "LUK"}).status_code == 422
    assert (
        client.post("/api/recurring", json={"title": "x", "category": "STR", "weekdays": [7]}).status_code
        == 422
    )
    task = create(client)
    assert client.patch(f"/api/tasks/{task['id']}", json={"title": None}).status_code == 422
    r = client.patch(f"/api/tasks/{task['id']}", json={"due_date": "2026-10-30"})
    assert r.json()["due_date"] == "2026-10-30"
    r = client.patch(f"/api/tasks/{task['id']}", json={"due_date": None})
    assert r.json()["due_date"] is None


def test_analyze_reports_unavailable_without_model(client):
    r = client.post("/api/analyze", json={"text": "部屋を片付ける"})
    assert r.json() == {"available": False, "category": None, "subtasks": []}
