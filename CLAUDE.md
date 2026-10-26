# CLAUDE.md

Claude Codeがこのリポジトリを理解するためのガイド。ゲーム仕様の詳細は `docs/SPEC.md` を参照。

---

## プロジェクト

**Todoリスト風ローグライクRPG** — タスク管理をゲーム化したWebアプリ＋モバイルアプリ。
タスクをこなすとキャラクターのステータス・コマンドが強化され、週末にダンジョンへ強制出発する。

---

## 技術スタック

| レイヤー | 技術 |
|---|---|
| バックエンドAPI | Python / FastAPI |
| フロントエンド（Web） | React / Next.js |
| モバイルアプリ | React Native または Flutter |
| データベース | PostgreSQL |
| タスク解析（分類・分解） | サーバ側から呼ぶLLM（初期は Claude API の Haiku 5.5） |
| 認証 | Firebase Auth または Auth.js |

---

## リポジトリ構成

```
/
├── CLAUDE.md       # このファイル
├── README.md       # 動かし方
├── backend/        # サーバ（FastAPI）
│   ├── app/
│   │   ├── api.py       # エンドポイント
│   │   ├── game.py      # ステータス計算（完了記録から毎回計算する）
│   │   ├── services.py  # 繰り返しタスクの生成など
│   │   ├── models.py    # テーブル定義（SQLAlchemy）
│   │   ├── clock.py     # 現在時刻と日付の区切り（テストで差し替える）
│   │   └── analyzer/    # タスク解析（LLM）の窓口。モデルごとの実装をここに足す
│   └── tests/
├── frontend/       # 画面（Next.js）。/api/* はサーバへ中継する
│   ├── app/             # 今日 / すべて（tasks）/ 繰り返し（habits）
│   └── components/
├── docs/
│   ├── SPEC.md     # ゲーム仕様書（設計の源泉）
│   └── PROGRESS.md # 進捗・決定ログ・次にやること
├── prototype/
│   └── weekend-dungeon.html  # 遊べる検証用プロトタイプ（単一HTML）
├── main.py         # 既存スクリプト（OCR関連）
├── ocrClass.py
└── hit_api.py
```

---

## 開発ルール

- セッション開始時は `docs/PROGRESS.md` で現在地を確認する
- 仕様変更は必ず `docs/SPEC.md` に反映してからコードに落とす
- 決定したことは `docs/PROGRESS.md` の決定ログと「現在地」を更新する
- プロトタイプは SPEC 準拠。SPEC 未確定の値はプロトタイプ内で「仮」と明示する
- ★マークは仮置き値。バランス確定後に更新する
- サーバを変更したら `cd backend && pytest`、画面を変更したら `cd frontend && npm run build` が通ることを確かめる
- ローカルの DB は SQLite、本番は PostgreSQL（`DATABASE_URL` で切り替え）。SQLite でしか動かない書き方は避ける
- LLMはタスクの分類・分解にのみ使用する。呼び出しはサーバ側から行い、APIキーを端末に置かない
- LLMの呼び出し部分は差し替え可能にする（API と自前の小型モデルを切り替えられるように）
