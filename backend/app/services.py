from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from .clock import Clock
from .game import Completion, WeekResult, compute_week
from .models import RecurringTask, Task
from .schemas import RecurringOut, StatsOut, TaskOut


def weekdays_to_mask(weekdays: list[int]) -> int:
    mask = 0
    for d in weekdays:
        mask |= 1 << d
    return mask


def mask_to_weekdays(mask: int) -> list[int]:
    return [d for d in range(7) if mask & (1 << d)]


def recurring_out(r: RecurringTask) -> RecurringOut:
    return RecurringOut(
        id=r.id,
        title=r.title,
        category=r.category,
        weekdays=mask_to_weekdays(r.weekday_mask),
        active=r.active,
    )


def task_out(task: Task, today: date) -> TaskOut:
    out = TaskOut.model_validate(task)
    out.overdue = task.completed_at is None and task.due_date is not None and task.due_date < today
    return out


def ensure_recurring_instances(db: Session, clock: Clock) -> None:
    """今日が該当日の繰り返しタスクについて、今日の分のタスクがなければ作る。

    やらなかった日の分は作らない（SPEC「繰り返しタスク」: 溜まらない）。
    """
    today = clock.today()
    bit = 1 << today.weekday()
    rules = db.scalars(select(RecurringTask).where(RecurringTask.active.is_(True))).all()
    existing = set(
        db.scalars(
            select(Task.recurring_id).where(
                Task.recurring_id.is_not(None), Task.due_date == today
            )
        ).all()
    )
    created = False
    for r in rules:
        if r.weekday_mask & bit and r.id not in existing:
            db.add(
                Task(
                    title=r.title,
                    category=r.category,
                    due_date=today,
                    recurring_id=r.id,
                    created_at=clock.now_utc(),
                )
            )
            created = True
    if created:
        db.commit()


def compute_stats(db: Session, clock: Clock) -> tuple[WeekResult, StatsOut]:
    week_start = clock.week_start()
    parent_ids = set(
        db.scalars(select(Task.parent_id).where(Task.parent_id.is_not(None)).distinct()).all()
    )
    rows = db.scalars(
        select(Task).where(
            Task.completed_at.is_not(None),
            Task.completed_at >= clock.local_midnight_utc(week_start),
        )
    ).all()
    completions = [
        Completion(t.id, t.category, t.completed_at, clock.local_date(t.completed_at))
        for t in rows
        if t.id not in parent_ids  # 分解元の親タスクは加算しない
    ]
    result = compute_week(completions)
    today = clock.today()
    return result, StatsOut(
        today=today,
        week_start=week_start,
        stats=result.stats,
        remaining_today=result.remaining_today(today),
    )
