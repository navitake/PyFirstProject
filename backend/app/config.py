import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

# 既定はローカルの SQLite。本番は DATABASE_URL で PostgreSQL を指定する
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'data' / 'app.db'}")

# 1日の区切りに使うタイムゾーン（SPEC「日付の区切り」）
TIMEZONE = os.environ.get("APP_TIMEZONE", "Asia/Tokyo")

# タスク解析に使うLLM。モデルが決まるまでは "none"（手動でカテゴリを選ぶ）
TASK_ANALYZER = os.environ.get("TASK_ANALYZER", "none")
