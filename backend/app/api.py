from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .analyzer import get_analyzer
from .clock import Clock, get_clock
from .db import get_db
from .models import RecurringTask, Task
from .schemas import (
    AnalyzeIn,
    AnalyzeOut,
    CompleteOut,
    GainOut,
    RecurringCreate,
    RecurringOut,
    RecurringUpdate,
    StatsOut,
    SubtaskOut,
    TaskCreate,
    TaskOut,
    TaskUpdate,
    TodayOut,
)
from .services import (
    compute_stats,
    ensure_recurring_instances,
    recurring_out,
    task_out,
    weekdays_to_mask,
)

router = APIRouter(prefix="/api")


def get_task(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(404, "タスクが見つかりません")
    return task


@router.get("/today", response_model=TodayOut)
def today_view(db: Session = Depends(get_db), clock: Clock = Depends(get_clock)):
    ensure_recurring_instances(db, clock)
    today = clock.today()
    tasks = db.scalars(
        select(Task).where(
            or_(
                # 期限が今日以前の未完了タスク（繰り返しタスクは今日の分だけ）
                (Task.completed_at.is_(None))
                & (Task.due_date <= today)
                & (or_(Task.recurring_id.is_(None), Task.due_date == today)),
                # 今日完了したタスク
                Task.completed_at >= clock.local_midnight_utc(today),
            )
        )
    ).all()
    tasks = sorted(
        tasks,
        key=lambda t: (t.completed_at is not None, t.completed_at or t.created_at, t.id),
    )
    _, stats = compute_stats(db, clock)
    return TodayOut(stats=stats, tasks=[task_out(t, today) for t in tasks])


@router.get("/tasks", response_model=list[TaskOut])
def list_open_tasks(db: Session = Depends(get_db), clock: Clock = Depends(get_clock)):
    """未完了のタスク全部。期限が近い順、期限なしは最後。過去の繰り返し分は含めない。"""
    today = clock.today()
    tasks = db.scalars(
        select(Task).where(
            Task.completed_at.is_(None),
            or_(Task.recurring_id.is_(None), Task.due_date == today),
        )
    ).all()
    tasks = sorted(tasks, key=lambda t: (t.due_date is None, t.due_date or today, t.id))
    return [task_out(t, today) for t in tasks]


@router.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db), clock: Clock = Depends(get_clock)):
    task = Task(**body.model_dump(), created_at=clock.now_utc())
    db.add(task)
    db.commit()
    return task_out(task, clock.today())


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    body: TaskUpdate,
    db: Session = Depends(get_db),
    clock: Clock = Depends(get_clock),
):
    task = get_task(db, task_id)
    for key in body.model_fields_set:
        value = getattr(body, key)
        if value is None and key != "due_date":
            raise HTTPException(422, f"{key} は空にできません")
        setattr(task, key, value)
    db.commit()
    return task_out(task, clock.today())


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db.delete(get_task(db, task_id))
    db.commit()
    return Response(status_code=204)


@router.post("/tasks/{task_id}/complete", response_model=CompleteOut)
def complete_task(task_id: int, db: Session = Depends(get_db), clock: Clock = Depends(get_clock)):
    task = get_task(db, task_id)
    if task.completed_at is None:
        task.completed_at = clock.now_utc()
        db.commit()
    result, stats = compute_stats(db, clock)
    gain = result.gains.get(task.id)
    return CompleteOut(
        task=task_out(task, clock.today()),
        gain=GainOut(stat=task.category, amount=gain.amount, capped=gain.capped) if gain else None,
        stats=stats,
    )


@router.post("/tasks/{task_id}/uncomplete", response_model=CompleteOut)
def uncomplete_task(task_id: int, db: Session = Depends(get_db), clock: Clock = Depends(get_clock)):
    task = get_task(db, task_id)
    task.completed_at = None
    db.commit()
    _, stats = compute_stats(db, clock)
    return CompleteOut(task=task_out(task, clock.today()), gain=None, stats=stats)


@router.get("/stats", response_model=StatsOut)
def week_stats(db: Session = Depends(get_db), clock: Clock = Depends(get_clock)):
    return compute_stats(db, clock)[1]


@router.get("/recurring", response_model=list[RecurringOut])
def list_recurring(db: Session = Depends(get_db)):
    return [recurring_out(r) for r in db.scalars(select(RecurringTask).order_by(RecurringTask.id))]


@router.post("/recurring", response_model=RecurringOut, status_code=201)
def create_recurring(
    body: RecurringCreate, db: Session = Depends(get_db), clock: Clock = Depends(get_clock)
):
    rule = RecurringTask(
        title=body.title,
        category=body.category,
        weekday_mask=weekdays_to_mask(body.weekdays),
        active=True,
        created_at=clock.now_utc(),
    )
    db.add(rule)
    db.commit()
    return recurring_out(rule)


@router.patch("/recurring/{rule_id}", response_model=RecurringOut)
def update_recurring(
    rule_id: int,
    body: RecurringUpdate,
    db: Session = Depends(get_db),
    clock: Clock = Depends(get_clock),
):
    rule = db.get(RecurringTask, rule_id)
    if rule is None:
        raise HTTPException(404, "繰り返しタスクが見つかりません")
    for key in body.model_fields_set:
        value = getattr(body, key)
        if value is None:
            raise HTTPException(422, f"{key} は空にできません")
        if key == "weekdays":
            rule.weekday_mask = weekdays_to_mask(value)
        else:
            setattr(rule, key, value)
    # 今日の分がまだ未完了なら、変更後の内容に合わせる（止めた・曜日から外した場合は消す）
    today_task = db.scalars(
        select(Task).where(
            Task.recurring_id == rule.id,
            Task.due_date == clock.today(),
            Task.completed_at.is_(None),
        )
    ).first()
    if today_task is not None:
        if not rule.active or not rule.weekday_mask & (1 << clock.today().weekday()):
            db.delete(today_task)
        else:
            today_task.title = rule.title
            today_task.category = rule.category
    db.commit()
    return recurring_out(rule)


@router.delete("/recurring/{rule_id}", status_code=204)
def delete_recurring(rule_id: int, db: Session = Depends(get_db)):
    rule = db.get(RecurringTask, rule_id)
    if rule is None:
        raise HTTPException(404, "繰り返しタスクが見つかりません")
    # 未完了の分は消し、完了済みの分はステータスの記録として残す
    for t in db.scalars(
        select(Task).where(Task.recurring_id == rule.id, Task.completed_at.is_(None))
    ):
        db.delete(t)
    db.delete(rule)
    db.commit()
    return Response(status_code=204)


@router.post("/analyze", response_model=AnalyzeOut)
def analyze(body: AnalyzeIn):
    analyzer = get_analyzer()
    if analyzer is None:
        return AnalyzeOut(available=False)
    result = analyzer.analyze(body.text)
    return AnalyzeOut(
        available=True,
        category=result.category,
        subtasks=[SubtaskOut(title=s.title, category=s.category) for s in result.subtasks],
    )
