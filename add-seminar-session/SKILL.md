---
name: add-seminar-session
description: Use this skill to add a new seminar session to the lab-seminars repository. Trigger when the user wants to create a new session from a PDF, paper, or textbook chapter, invokes /add-seminar-session, mentions adding a 勉強会セッション or 輪講, or wants to generate まとめ記事 and スライド from a source document.
argument-hint: <slug> <pdf-path> [display-title] [YYYY-MM-DD]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# add-seminar-session

PDFや論文からセミナーセッションを新規追加します。まとめ記事・Marpスライド・Mermaid図を生成し、サイトのナビゲーションも自動更新します。

## 引数

`$ARGUMENTS` を次の形式でパースしてください：

```
<slug> <pdf-path> [display-title] [YYYY-MM-DD]
```

- `slug` (必須): URLセーフな識別子（例: `dl-ch6-2`, `bert`, `attention-is-all-you-need`）
- `pdf-path` (必須): PDFへのパス。`pdfs/` からの相対パスでも絶対パスでも可
- `display-title` (任意): ナビゲーション・一覧に表示するタイトル。省略時はPDF内容から推測
- `date` (任意): YYYY-MM-DD 形式。**省略時は `date +%Y-%m-%d` コマンドで今日の日付を自動取得する**

変数を定義する：
- `SESSION_ID = <date>-<slug>`
- `SESSION_DIR = docs/sessions/<SESSION_ID>`

## Step 1: PDFを読み込む

`Read` ツールでPDFを読み込み、以下を把握する：
- 章・節の構造（セクション番号とタイトル）
- 主要概念、定義、数式
- 著者・出典情報

`display-title` が省略されていた場合、ここで内容からタイトルを決定する。

## Step 2: ディレクトリ作成

```bash
mkdir -p docs/sessions/<SESSION_ID>/diagrams
```

## Step 3: index.md を生成

`docs/sessions/<SESSION_ID>/index.md` を作成する。

**目標**: その内容を読んでいない人でも理解できる、自己完結した解説記事。

**テンプレート**: まず `.claude/skills/add-seminar-session/assets/index_template.md` を Read し、構造を把握してから生成する。各 `<!-- ... -->` プレースホルダーをPDFから読み取った実際の内容で置き換える。

**品質ガイドライン**:
- 数式はインライン `$...$` またはブロック `$$...$$` で記述し、変数の意味を添える
- Mermaid図を最低1つ含める（概念の関係・フロー・階層を図示）
- 重要な洞察は `!!! note` / `!!! warning` / `!!! success` admonitionで強調する
- 比較・対照があるときはテーブルを使う

## Step 4: slides.md を生成

`docs/sessions/<SESSION_ID>/slides.md` を作成する。

Marp形式のスライド（全体10〜15枚程度）。各節を1〜3枚にまとめる。

**テンプレート**: `.claude/skills/add-seminar-session/assets/slides_template.md` を Read し、frontmatter・構成を確認してから生成する。各 `<!-- ... -->` プレースホルダーを実際の内容で置き換える。

## Step 5: diagrams/architecture.mmd を生成

`docs/sessions/<SESSION_ID>/diagrams/architecture.mmd` を作成する。

内容に合ったMermaid図を1つ。`index.md` 内のインライン図とは異なる視点・粒度で描く（全体構成図、手法比較、データフロー、歴史的変遷など）。

## Step 6: mkdocs.yml を更新

`mkdocs.yml` の `nav:` → `セッション:` 配下に1行追加する。

正確なインデント・フォーマットは `.claude/skills/add-seminar-session/references/session_format.md` を参照。

## Step 7: docs/index.md を更新

`docs/index.md` のセッション一覧テーブルの末尾に1行追加する。

テーブル行の形式は `.claude/skills/add-seminar-session/references/session_format.md` を参照。

## 完了メッセージ

全ステップ完了後、以下を出力する：

```
✅ セッション追加完了：<SESSION_ID>

生成：
  docs/sessions/<SESSION_ID>/index.md
  docs/sessions/<SESSION_ID>/slides.md
  docs/sessions/<SESSION_ID>/diagrams/architecture.mmd

更新：
  mkdocs.yml（nav に追加）
  docs/index.md（テーブルに追加）

確認：
  uv run mkdocs serve
```
