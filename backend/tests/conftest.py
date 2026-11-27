from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.clock import Clock, get_clock
from app.db import Base, get_db, make_engine
from app.main import app

JST = ZoneInfo("Asia/Tokyo")


class FixedClock(Clock):
    """テスト用に時刻を固定・進められる時計"""

    def __init__(self, local: datetime):
        super().__init__("Asia/Tokyo")
        self.set(local)

    def set(self, local: datetime) -> None:
        self._now = local.replace(tzinfo=JST).astimezone(UTC).replace(tzinfo=None)

    def now_utc(self) -> datetime:
        return self._now


@pytest.fixture
def clock():
    # 2026-10-26 は月曜日
    return FixedClock(datetime(2026, 10, 26, 9, 0))


@pytest.fixture
def client(clock):
    engine = make_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_clock] = lambda: clock
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
