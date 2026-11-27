from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Category = Literal["STR", "INT", "VIT", "DEX", "MND"]
Weekday = Annotated[int, Field(ge=0, le=6)]  # 0=月曜 … 6=日曜


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: Category
    due_date: date | None = None


class TaskUpdate(BaseModel):
    # 送られた項目だけを更新する。due_date に null を送ると期限を外す
    title: str | None = Field(default=None, min_length=1, max_length=200)
    category: Category | None = None
    due_date: date | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    category: Category
    due_date: date | None
    parent_id: int | None
    recurring_id: int | None
    created_at: datetime
    completed_at: datetime | None
    overdue: bool = False


class RecurringCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: Category
    weekdays: list[Weekday] = Field(min_length=1)


class RecurringUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    category: Category | None = None
    weekdays: list[Weekday] | None = Field(default=None, min_length=1)
    active: bool | None = None


class RecurringOut(BaseModel):
    id: int
    title: str
    category: Category
    weekdays: list[int]
    active: bool


class StatsOut(BaseModel):
    today: date
    week_start: date
    stats: dict[str, int]
    remaining_today: dict[str, int]


class TodayOut(BaseModel):
    stats: StatsOut
    tasks: list[TaskOut]


class GainOut(BaseModel):
    stat: Category
    amount: int
    capped: bool


class CompleteOut(BaseModel):
    task: TaskOut
    gain: GainOut | None  # 親タスク（分解元）を完了したときは加算なしで None
    stats: StatsOut


class AnalyzeIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class SubtaskOut(BaseModel):
    title: str
    category: Category


class AnalyzeOut(BaseModel):
    available: bool  # タスク解析のモデルが設定されているか
    category: Category | None = None
    subtasks: list[SubtaskOut] = []
