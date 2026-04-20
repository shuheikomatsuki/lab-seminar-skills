---
name: add-paper-session
description: Use this skill to add a new paper introduction session to the lab-seminars repository. Trigger when the user wants to create a new session from a research paper PDF, invokes /add-paper-session, mentions adding a 論文紹介 or 論文セッション, or wants to generate まとめ記事 from a research paper.
argument-hint: "[slug] <pdf-path> [display-title] [YYYY-MM-DD]"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# add-paper-session

論文PDFから論文紹介セッションを新規追加します。解説記事・Mermaid図を生成し、サイトのナビゲーションも自動更新します。

---

## 引数

`$ARGUMENTS` を次の形式でパースしてください：

```
[slug] <pdf-path> [display-title] [YYYY-MM-DD]
```

- `slug` (任意): URLセーフな識別子（例: `attention-is-all-you-need`, `bert-2018`）
  - **省略判定**: 第1引数が `.pdf` で終わるか `/` を含む場合はパスとみなし、slug 省略と判断する
  - **省略時の導出**: PDFファイル名から生成する（拡張子除去・小文字化・非英数字を `-` に置換）
- `pdf-path` (必須): PDFへのパス。`pdfs/` からの相対パスでも絶対パスでも可
- `display-title` (任意): ナビゲーション・一覧に表示するタイトル。省略時はPDF内容から推測
- `date` (任意): YYYY-MM-DD 形式。優先順位: **CLI引数 → seminar_config.yml の `next_seminar_date` → 今日の日付**

変数を定義する：
- `SESSION_ID = <date>-<slug>`
- `SESSION_DIR = docs/sessions/<SESSION_ID>`
- `SKILL_SOURCE_DIR` = この `SKILL.md` が置かれている `add-paper-session` ディレクトリ

---

## Step 0: 設定ファイルの読み込み

`seminar_config.yml` が存在する場合、`Read` ツールで読み込み以下の変数に格納する：
- `config_date`: `next_seminar_date` の値
- `config_presenter`: `default_presenter` の値

ファイルが存在しない場合はどちらも未設定とする。

`date` 引数が省略されていた場合、`config_date` が設定されていればそれを使用し、未設定なら `date +%Y-%m-%d` で今日の日付を取得する。

---

## Step 1: PDFを読み込む

`Read` ツールで論文PDFを読み込み、以下を把握する：
- Abstract / 概要
- 背景・研究課題（先行研究の何が問題だったか）
- 提案手法（Method）の概要とアーキテクチャ
- 実験設定・使用データセット・評価指標
- 主要な定量結果・定性結果
- 考察・限界
- 結論・貢献
- 著者・出典情報（会議名・年・arXiv IDなど）

`display-title` が省略されていた場合、ここで論文タイトルからタイトルを決定する。

---

## Step 2: ディレクトリ作成

```bash
mkdir -p docs/sessions/<SESSION_ID>/diagrams
mkdir -p docs/sessions/<SESSION_ID>/images
```

---

## Step 3: index.md（論文紹介記事）を生成

`docs/sessions/<SESSION_ID>/index.md` を作成する。

**目標**: 論文を読んでいない人でも手法・実験・貢献を理解できる、自己完結した解説記事。

**テンプレート**: まず `$SKILL_SOURCE_DIR/assets/index_template.md` を Read し、構造を把握してから生成する。各 `<!-- ... -->` プレースホルダーをPDFから読み取った実際の内容で置き換える。

**メタ情報の改行**: 冒頭の `**出典:**` 行と `**担当:**` 行は、それぞれ末尾に半角スペース2個を付け、Markdownプレビューで `出典`、`担当`、`日付` が別行に表示されるようにする。`**日付:**` 行は最後のメタ情報行なので、末尾には不要な半角スペースを付けない。

**発表者の挿入**: `config_presenter` が設定されている場合、`（担当者名）` プレースホルダーを `config_presenter` の値で置き換える。未設定の場合は `（担当者名）` のままにする。

**品質ガイドライン**:
- Abstract を単に翻訳するのではなく、「なぜこの研究が必要か」を先行研究との対比で説明する
- 提案手法の核心となる数式・アーキテクチャ図をMermaidで示す
- 初学者がつまずきやすい箇所に、必要に応じて `<!-- image-slot: <image-id> -->` を最大3件まで挿入する
- 画像スロットは、直感説明・数式の意味・提案手法の全体像・誤解しやすい比較の直後に置く
- 生成画像は教育用の補助図に限定し、論文の厳密な数値結果・原図・実験表の再現には使わない
- 実験結果は定量評価テーブルと「何がどのくらい改善されたか」の解釈を両方記載する
- 限界・今後の課題も必ず記載する（批判的な視点を持つ）
- 発表者の所感・議論点を末尾に記載する

---

## Step 4: image_prompts.yml を生成

`docs/sessions/<SESSION_ID>/image_prompts.yml` を作成する。

記事中に挿入した各 `image-slot` について、手動画像生成用のプロンプトを記載する。画像生成APIは使わない。プロンプトは、ユーザーが Gemini / Google AI Studio / nanobanana のチャット画面に貼り付けて使えるようにする。

**スキーマ**:

```yaml
images:
  - id: <image-id>
    article: index.md
    filename: images/<image-id>.png
    alt: "<画像の代替テキスト>"
    insert_after_heading: "<スロットを置いた見出し>"
    purpose: "<この画像で理解しやすくしたいポイント>"
    prompt: |
      <画像生成用プロンプト>
    notes: "<生成時の注意。文字崩れ・ラベル量・事実性など>"
```

**プロンプト作成ルール**:
- 白背景または淡色背景の教材用図解を基本にする
- 論文の主張を超える構造・数値・結果を描かない
- 文字は最小限にし、文字崩れが起きる場合はラベルなしで生成して本文側で説明するよう `notes` に書く
- 1つの画像は1つの理解ポイントだけを扱う
- Mermaid で十分な構造図は画像化しない

画像スロットを挿入しなかった場合も、次の空ファイルを作成する：

```yaml
images: []
```

---

## Step 5: diagrams/architecture.mmd を生成

`docs/sessions/<SESSION_ID>/diagrams/architecture.mmd` を作成する。

提案手法のアーキテクチャ・システム構成・データフロー・先行研究との比較などをMermaid図で示す。

---

## Step 6: mkdocs.yml を更新

`mkdocs.yml` の `nav:` → `セッション:` 配下に1行追加する（フラットエントリ）。

```yaml
    - <date> <display-title>: sessions/<SESSION_ID>/index.md
```

インデントはスペース4つ。

---

## Step 7: docs/index.md を更新

`docs/index.md` のセッション一覧テーブルの末尾に1行追加する。

```markdown
| <date> | [<display-title>](sessions/<SESSION_ID>/index.md) |
```

---

## Step 8: ビルド確認

```bash
uv run mkdocs build --strict
```

- **成功した場合**: 完了メッセージに `✅ ビルド確認済み` を追加する
- **失敗した場合**: エラー出力を表示し、原因箇所を特定して修正してから再実行する

---

## 完了メッセージ

```
✅ 論文紹介セッション追加完了：<SESSION_ID>

生成：
  docs/sessions/<SESSION_ID>/index.md（論文紹介記事）
  docs/sessions/<SESSION_ID>/diagrams/architecture.mmd
  docs/sessions/<SESSION_ID>/images/（生成画像の保存先）
  docs/sessions/<SESSION_ID>/image_prompts.yml（手動画像生成用プロンプト）

更新：
  mkdocs.yml（nav に追加）
  docs/index.md（テーブルに追加）

確認：
  uv run mkdocs build --strict  ✅
  uv run mkdocs serve

画像生成（任意）：
  1. image_prompts.yml の prompt を Gemini / Google AI Studio / nanobanana に貼り付ける
  2. 生成画像を filename のパスに保存する
  3. /insert-generated-images <SESSION_ID> で本文へ埋め込む
```
