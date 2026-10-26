# タスク解析（分類・分解）のモデル候補

調査日: 2026-10-26。料金は各社の公式ページで確認した**標準の単価**（100万トークンあたり、米ドル）。
料金は変わるので、決めるときにもう一度確認する。

---

## 結論

- **一人で使う段階では、どれを選んでも料金はほぼ問題にならない**（月300件の登録で、高くても約 $0.2）。決め手は「日本語での分解の質」「速さ」「JSON の形式を守れるか」「将来の乗り換えやすさ」になる
- 比較テストにかける候補は次の**6つ**を推奨する

| # | モデル | 提供元 | 選んだ理由 |
|---|---|---|---|
| 1 | Claude Haiku 5.5 | Anthropic | 分類などの大量・低遅延の処理向けとされる現行の小型モデル。JSON の形式を強制できる。学習に使われない。提供終了は早くても2027年10月以降 |
| 2 | gpt-6-luna | OpenAI | OpenAI の最新の小型モデル。同じ系列の一つ前（5.6 luna）は日本語の評価が高い |
| 3 | gpt-5-nano | OpenAI | 調べた中で最安（ただし一つ前の世代） |
| 4 | Gemini 3.1 Flash-Lite | Google | Google の現行で最安の小型モデル |
| 5 | gpt-oss-20b（Groq） | OpenAI のモデルを Groq で実行 | 最速クラス（毎秒約1000トークン）。**中身が公開されたモデルなので、将来そのまま自前のサーバに移せる** |
| 6 | Qwen3.5-4B（自前で実行） | Alibaba | 自前で動かせる小型モデルの中で、日本語の評価が最も高い。お金がかからず、タスクの内容が外に出ない |

---

## 料金の比較

1回の登録で **入力 約800トークン・出力 約200トークン** と仮定した概算（カテゴリの説明と例を含めた指示文＋分解案のJSON）。

| モデル | 入力 | 出力 | 1回あたり | 自分1人（月300件） | 利用者1000人（月30万件） |
|---|---|---|---|---|---|
| gpt-5-nano | $0.05 | $0.40 | $0.00012 | $0.04 | $36 |
| gpt-oss-20b（Groq） | $0.075 | $0.30 | $0.00012 | $0.04 | $36 |
| gpt-4.1-nano | $0.10 | $0.40 | $0.00016 | $0.05 | $48 |
| Gemini 2.5 Flash-Lite | $0.10 | $0.40 | $0.00016 | $0.05 | $48 |
| **Claude Haiku 5.5** | $0.10 | $0.50 | $0.00018 | $0.05 | $54 |
| **gpt-6-luna** | $0.10 | $0.50 | $0.00018 | $0.05 | $54 |
| gpt-oss-120b（Groq） | $0.15 | $0.60 | $0.00024 | $0.07 | $72 |
| gpt-5.4-nano | $0.20 | $1.25 | $0.00041 | $0.12 | $123 |
| **Gemini 3.1 Flash-Lite** | $0.25 | $1.50 | $0.00050 | $0.15 | $150 |
| Gemini 3.5 Flash-Lite | $0.30 | $2.50 | $0.00074 | $0.22 | $222 |
| Qwen3.5-4B（自前で実行） | — | — | 0（電気代・サーバ代のみ） | 0 | サーバ代（固定費） |

**注意点**

- **考えてから答えるタイプのモデルは、表より高くなる**。考えた分も出力として課金されるため。gpt-5-nano はこのタイプ。Haiku 5.5 は考える機能を切れる（推論の強さ effort を high 以下にした場合）。実際の金額は比較テストで測る
- 同じ指示文を毎回送るので、各社の**キャッシュ割引**（繰り返し送る入力が最大9割引）が使える。表は割引なしの値
- Gemini 2.5 Flash-Lite と gpt-4.1-nano は安いが一つ前の世代で、提供終了が早い可能性があるので候補からは外した

---

## 料金以外の比較

| 観点 | Claude Haiku 5.5 | gpt-6-luna / gpt-5-nano | Gemini 3.1 Flash-Lite | gpt-oss-20b（Groq） | Qwen3.5-4B（自前） |
|---|---|---|---|---|---|
| JSON の形式を強制できるか | ○（構造化出力） | ○（構造化出力） | ○（構造化出力） | ○（strict モード） | △（実行ソフト次第。Ollama などは形式の指定に対応） |
| 日本語の評価 | 日本語の評価表には未掲載 | 一つ前の 5.6 luna が日本語の評価表で上位 | 未掲載 | 未掲載 | 10B以下の小型モデルで1位 |
| 速さ | 速い | 速い（nano は考える分だけ遅くなりうる） | 速い | **最速クラス** | PCの性能次第（GPUなしだと数秒） |
| 送った内容が学習に使われるか | 使われない（初期設定） | 使われない（初期設定） | **有料枠は使われない／無料枠は使われる** | 使われない（規約で禁止） | 外に出ない |
| 将来の乗り換えやすさ | — | — | — | **同じモデルを自前で動かせる** | もともと自前 |
| 弱み | Anthropic にしかない | OpenAI にしかない | 無料枠は学習に使われるので有料枠が前提 | Groq の無料枠・提供モデルはよく変わる | PCを起動していないとスマホから使えない |

**日本語の評価**について: 参考にしたのは日本語の課題で総合的に測る評価表（Nejumi Leaderboard 4、2026年10月22日時点）。API の小型モデルはほとんど載っていないため、**最終的には自分たちのタスク文で試すしかない**。

**自前で動かす場合**: 自分のPCで Ollama などを使えば無料で動かせるが、PCが起動していないとスマホから使えない。いつでも使えるようにするには常時起動のサーバが必要になり、使った量に関係なく毎月固定費がかかる。利用者が少ないうちは API のほうが安い。日本語向けに追加学習した NVIDIA Nemotron Nano 9B v2 Japanese も候補になる（同じ評価表で小型2位）。

---

## 比較テストの進め方（案）

1. **テスト用のタスク集を作る**（約50件）。実際に登録しそうな文で、次を混ぜる
   - 1回で終わる小さいタスク（分解しないのが正解）: 「歯医者の予約をする」
   - 工程が複数ある大きいタスク（分解するのが正解）: 「引っ越しの準備をする」
   - カテゴリが迷いやすいタスク: 「部屋を片付ける」「散歩しながら英語のポッドキャストを聞く」
2. **正解を付ける**（カテゴリ、分解するかどうか）。家事の扱いを先に決めておく必要がある
3. **各モデルで同じ指示文を使って実行し、次を測る**
   - カテゴリの正解率
   - 分解するかどうかの判定の正解率
   - 分解案の質（人が3段階で評価）
   - JSON の形式が崩れた回数
   - 応答時間（中央値）
   - 実際にかかった料金
4. 結果を表にして決める

テストを動かすには、試すモデルごとに各社の **APIキー** が必要（Anthropic・OpenAI・Google・Groq）。自前のモデルは Ollama を入れたPCで動かす。

---

## 端末の中で動かすモデル（PC・スマホそれぞれで実行）

LLMをサーバではなく、使っている端末の中で動かす方法。料金がかからず、タスクの内容が端末の外に出ない。
確認画面でユーザーが確定した結果だけをサーバに送るので、**サーバから見ればどこで解析したかは関係ない**（今の作りと両立する）。

| 端末 | 使えるもの | 形式の強制 | 日本語 | 条件・状態（2026-10 時点） |
|---|---|---|---|---|
| iPhone（ネイティブアプリ） | Apple の Foundation Models（端末内の約3Bモデル） | ○（guided generation） | ○（提供開始時から対応） | iOS 26 以降、Apple Intelligence 対応機種。入力と出力の合計が約4Kトークンまで（タスク解析には十分） |
| Android（ネイティブアプリ） | ML Kit GenAI Prompt API（Gemini Nano） | 要確認 | 端末と入っているモデル次第 | **アルファ版**。対応機種が限られる（Pixel 9・10、一部の Xiaomi・Galaxy など） |
| PC（ブラウザ） | Chrome の内蔵AI（Gemini Nano） | ○（JSON スキーマ指定） | 要確認 | 4GB超のビデオメモリ、または16GBメモリ＋4コア以上、空き容量約22GB。**一般のWebサイトから使えるかは公式情報で確認できず** |
| PC・スマホ（ブラウザ） | WebLLM など（WebGPU で Qwen などを実行） | ○ | モデル次第 | iPhone の Safari も iOS 26 から WebGPU が標準で有効。ただしモデルの初回ダウンロードが数GBで、スマホではメモリ不足で止まる恐れがある（実測情報なし） |

**まとめ**

- 端末の中で動かす方法は、**ネイティブアプリで本領を発揮する**。iPhone は条件を満たせば無料・高速・日本語対応で使える
- **Webアプリの段階では使える端末が限られる**（PCのChromeは見込みあり、スマホのブラウザは重い）
- 端末によって使えるモデルが違うので、どの端末でも同じ質になるとは限らない。比較テストでは端末内のモデルも一緒に測る
- 使えない端末（古い機種など）のために、**サーバ側の解析（API または自前のモデル）か手入力に切り替える**仕組みが要る

---

## 出典

- [Claude のモデルと料金](https://platform.claude.com/docs/en/models/overview)（Haiku 5.5: 入力 $0.10 / 出力 $0.50）／[API のデータ保持](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)／[学習への利用について](https://privacy.anthropic.com/en/articles/7996868-i-want-to-opt-out-of-my-prompts-and-results-being-used-for-training-models)
- [OpenAI API の料金](https://developers.openai.com/api/docs/pricing)／[OpenAI のデータの扱い](https://developers.openai.com/api/docs/guides/your-data)
- [Gemini API の料金（無料枠と有料枠のデータの扱いを含む）](https://ai.google.dev/gemini-api/docs/pricing)
- [Groq のモデル一覧と料金](https://console.groq.com/docs/models)／[Groq の構造化出力](https://console.groq.com/docs/structured-outputs)／[Groq のデータの扱い](https://console.groq.com/docs/your-data)／[Groq の利用規約](https://console.groq.com/docs/legal/services-agreement)
- [日本語LLMランキング 2026（Nejumi Leaderboard 4 の分析、9月1日版を10月22日時点で更新）](https://journal.qualiteg.com/llm-ranking-2026/)
- 端末内モデル: [Apple の Foundation Models 発表（対応言語に日本語）](https://www.apple.com/newsroom/2025/09/apples-foundation-models-framework-unlocks-new-intelligent-app-experiences/)／[Apple Intelligence の日本語対応（iOS 18.4）](https://www.apple.com/newsroom/2025/03/apple-intelligence-features-expand-to-new-languages-and-regions-today/)／[Apple Intelligence の入手方法と対応言語](https://support.apple.com/en-us/121115)／[Apple の技術レポート（guided generation）](https://arxiv.org/pdf/2507.13575)／[Foundation Models の解説（4Kトークンの制限など）](https://www.atelier-socle.com/en/articles/foundation-models-api-guide)／[ML Kit GenAI の概要](https://developers.google.com/ml-kit/genai)／[ML Kit GenAI Prompt API のアルファ版発表](https://android-developers.googleblog.com/2025/10/ml-kit-genai-prompt-api-alpha-release.html)／[Chrome の Prompt API](https://developer.chrome.com/docs/ai/prompt-api)／[Chrome の内蔵AIの解説（動作条件）](https://noqta.tn/en/tutorials/chrome-built-in-ai-prompt-api-gemini-nano-2026)／[iOS 26 の WebGPU](https://appdevelopermagazine.com/webgpu-in-ios-26/)
