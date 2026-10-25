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
| AI分類 | Claude API（タスクカテゴリ自動判別） |
| 認証 | Firebase Auth または Auth.js |

---

## リポジトリ構成

```
/
├── CLAUDE.md       # このファイル
├── docs/
│   ├── SPEC.md     # ゲーム仕様書（設計の源泉）
│   └── PROGRESS.md # 進捗・決定ログ・次にやること
├── prototype/
│   └── weekend-dungeon.html  # 遊べる検証用プロトタイプ（単一HTML）
├── main.py         # 既存スクリプト（OCR関連）
├── ocrClass.py
└── hit_api.py
```

> バックエンド・フロントエンドのディレクトリ構成は実装開始時に決定する。

---

## 開発ルール

- セッション開始時は `docs/PROGRESS.md` で現在地を確認する
- 仕様変更は必ず `docs/SPEC.md` に反映してからコードに落とす
- 決定したことは `docs/PROGRESS.md` の決定ログと「現在地」を更新する
- プロトタイプは SPEC 準拠。SPEC 未確定の値はプロトタイプ内で「仮」と明示する
- ★マークは仮置き値。バランス確定後に更新する
- Claude APIはタスクカテゴリ自動判別にのみ使用する
