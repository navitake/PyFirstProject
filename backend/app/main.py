from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  テーブル定義を Base に登録する
from .api import router
from .db import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # マイグレーションの仕組みは本番運用を始めるときに入れる。それまでは起動時にテーブルを作る
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="週末ダンジョン タスク管理", lifespan=lifespan)
app.include_router(router)
