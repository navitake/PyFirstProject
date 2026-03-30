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
│   └── SPEC.md     # ゲーム仕様書（設計の源泉）
├── main.py         # 既存スクリプト（OCR関連）
├── ocrClass.py
└── hit_api.py
```

> バックエンド・フロントエンドのディレクトリ構成は実装開始時に決定する。

---

## 開発ルール

- 仕様変更は必ず `docs/SPEC.md` に反映してからコードに落とす
- ★マークは仮置き値。バランス確定後に更新する
- Claude APIはタスクカテゴリ自動判別にのみ使用する
