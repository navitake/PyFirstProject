# 週末ダンジョン

タスクをこなすとキャラクターが育ち、週末にダンジョンへ出発するタスク管理アプリ。
仕様は [`docs/SPEC.md`](docs/SPEC.md)、進み具合は [`docs/PROGRESS.md`](docs/PROGRESS.md) を参照。

## 動かし方

サーバ（FastAPI）と画面（Next.js）を、それぞれ別のターミナルで起動する。
必要なもの: Python 3.11 以上、Node.js 20 以上。

### 1. サーバ

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate          # Mac / Linux は source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

データは `backend/data/app.db`（SQLite）に保存される。

### 2. 画面

```powershell
cd frontend
npm install
npm run dev
```

ブラウザで http://localhost:3000 を開く。

### スマホから使う

PC と同じ Wi-Fi につないだスマホから使うには、画面を `npm run dev -- -H 0.0.0.0` で起動し、
スマホのブラウザで `http://<PCのIPアドレス>:3000` を開く。

## テスト

```powershell
cd backend
pytest
```

## 設定（環境変数）

| 名前 | 既定値 | 内容 |
|---|---|---|
| `DATABASE_URL` | `sqlite:///backend/data/app.db` | データベース。本番は PostgreSQL を指定する |
| `APP_TIMEZONE` | `Asia/Tokyo` | 1日の区切りに使うタイムゾーン |
| `TASK_ANALYZER` | `none` | タスク解析（分類・分解）に使うLLM。モデルが決まるまでは `none` |
| `BACKEND_URL` | `http://127.0.0.1:8000` | 画面側が中継するサーバの場所 |

## フォルダ

| フォルダ | 内容 |
|---|---|
| `backend/` | サーバ（FastAPI）。タスク・繰り返し・ステータス計算 |
| `frontend/` | 画面（Next.js）。今日 / すべて / 繰り返し |
| `prototype/` | ゲーム部分の検証用プロトタイプ（単一HTML） |
| `docs/` | 仕様書と進捗ログ |
