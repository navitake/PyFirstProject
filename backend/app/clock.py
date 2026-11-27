from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from .config import TIMEZONE


class Clock:
    """現在時刻と、ユーザーのタイムゾーンでの日付を扱う。テストでは固定の時刻に差し替える。"""

    def __init__(self, tz: str = TIMEZONE):
        self.tz = ZoneInfo(tz)

    def now_utc(self) -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def local_date(self, utc_naive: datetime) -> date:
        return utc_naive.replace(tzinfo=UTC).astimezone(self.tz).date()

    def today(self) -> date:
        return self.local_date(self.now_utc())

    def week_start(self) -> date:
        """今週の月曜日"""
        today = self.today()
        return today - timedelta(days=today.weekday())

    def local_midnight_utc(self, d: date) -> datetime:
        """その日の 0:00（ユーザーのタイムゾーン）を UTC で返す"""
        local = datetime(d.year, d.month, d.day, tzinfo=self.tz)
        return local.astimezone(UTC).replace(tzinfo=None)


def get_clock() -> Clock:
    return Clock()
