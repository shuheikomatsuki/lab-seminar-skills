---
name: add-textbook-session
description: Use this skill to add a new textbook session to the lab-seminars repository. Trigger when the user wants to create a new session from a textbook PDF, invokes /add-textbook-session, mentions adding a 勉強会セッション or 輪講, or wants to generate まとめ記事 from a textbook chapter.
argument-hint: "[slug] <pdf-path> [display-title] [YYYY-MM-DD]  |  <session-id> <pdf-path> --sub <subsection-slug> [subsection-title] [presenter]"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# add-textbook-session

教科書のPDFからセミナーセッションを追加します。**2つのモード**があります。

**Mode 1 — 新規セッション作成:**
サブセクション全体の概要ページ・Mermaid図を生成し、サイトのナビゲーションに追加します。

**Mode 2 — サブサブセクション深掘り記事追加:**
既存セッションに、1人の担当者が担当するサブサブセクションの詳細記事を追加します。

---

## 引数とモード検出

`$ARGUMENTS` に `--sub` が含まれる場合は **Mode 2**、含まれない場合は **Mode 1** として処理する。

### Mode 1 の引数

```
[slug] <pdf-path> [display-title] [YYYY-MM-DD]
```

- `slug` (任意): URLセーフな識別子（例: `dl-ch6-3`）
  - **省略判定**: 第1引数が `.pdf` で終わるか `/` を含む場合はパスとみなし、slug 省略と判断する
  - **省略時の導出**: PDFファイル名から生成する（拡張子除去・小文字化・非英数字を `-` に置換）
- `pdf-path` (必須): PDFへのパス。`pdfs/` からの相対パスでも絶対パスでも可
- `display-title` (任意): ナビゲーション・一覧に表示するタイトル。省略時はPDF内容から推測
- `date` (任意): YYYY-MM-DD 形式。優先順位: **CLI引数 → seminar_config.yml の `next_seminar_date` → 今日の日付**

変数を定義する：
- `SESSION_ID = <date>-<slug>`
- `SESSION_DIR = docs/sessions/<SESSION_ID>`

### Mode 2 の引数

```
<session-id> <pdf-path> --sub <subsection-slug> [subsection-title] [presenter]
```

- `session-id` (必須): 既存セッションのID（例: `2026-05-10-dl-ch6-3`）
- `pdf-path` (必須): PDFへのパス
- `--sub` (フラグ): Mode 2 であることを示す
- `subsection-slug` (必須): `--sub` の直後。URLセーフな識別子（例: `6-3-1`）
- `subsection-title` (任意): `--sub <slug>` の後に続く文字列。省略時はPDF内容から推測
- `presenter` (任意): さらに後に続く文字列。省略時は `config_presenter` または `（担当者名）`

変数を定義する：
- `SESSION_DIR = docs/sessions/<session-id>`
- `SUB_FILE = docs/sessions/<session-id>/<subsection-slug>.md`

---

## Step 0: 設定ファイルの読み込み

`seminar_config.yml` が存在する場合、`Read` ツールで読み込み以下の変数に格納する：
- `config_date`: `next_seminar_date` の値
- `config_presenter`: `default_presenter` の値

ファイルが存在しない場合はどちらも未設定とする。

Mode 1 で `date` 引数が省略されていた場合、`config_date` が設定されていればそれを使用し、未設定なら `date +%Y-%m-%d` で今日の日付を取得する。

---

## Mode 1: 新規セッション作成

### Step 1: PDFを読み込む

`Read` ツールでPDFを読み込み、以下を把握する：
- 章・節の構造（**サブサブセクションの番号とタイトル一覧**を必ず把握する）
- 各サブサブセクションの主要概念
- 著者・出典情報

`display-title` が省略されていた場合、ここで内容からタイトルを決定する。

### Step 2: ディレクトリ作成

```bash
mkdir -p docs/sessions/<SESSION_ID>/diagrams
```

### Step 3: index.md（概要ページ）を生成

`docs/sessions/<SESSION_ID>/index.md` を作成する。

**目標**: 節全体の位置づけと構成を把握できる薄い概要ページ。詳細はサブサブセクション記事（Mode 2 で生成）に委ねる。

**テンプレート**: まず `.claude/skills/add-textbook-session/assets/overview_template.md` を Read し、構造を把握してから生成する。各 `<!-- ... -->` プレースホルダーをPDFから読み取った実際の内容で置き換える。

**発表者の挿入**: `config_presenter` が設定されている場合、`（担当者名）` プレースホルダーを `config_presenter` の値で置き換える。未設定の場合は `（担当者名）` のままにする。

**品質ガイドライン**:
- サブサブセクション一覧テーブルには、担当者欄を `（担当者名）`、記事リンク欄を `準備中` として全サブサブセクションを列挙する
- 全体の流れをMermaid図で示す（各サブサブセクションのキーコンセプト間の関係）
- まとめテーブルには各サブサブセクションの1行要点を記載する

### Step 4: diagrams/architecture.mmd を生成

`docs/sessions/<SESSION_ID>/diagrams/architecture.mmd` を作成する。

節全体の概念構造・フロー・歴史的変遷などをMermaid図で示す。`index.md` 内のインライン図とは異なる視点・粒度で描く。

### Step 5: mkdocs.yml を更新（Mode 1）

`mkdocs.yml` の `nav:` → `セッション:` 配下に**ネスト構造のグループ**として追加する。

```yaml
    - <date> <display-title>:
      - 概要: sessions/<SESSION_ID>/index.md
```

正確なインデント・フォーマットは `.claude/skills/add-textbook-session/references/session_format.md` を参照。

### Step 6: docs/index.md を更新

`docs/index.md` のセッション一覧テーブルの末尾に1行追加する。

テーブル行の形式は `.claude/skills/add-textbook-session/references/session_format.md` を参照。

### Step 7: ビルド確認

```bash
uv run mkdocs build --strict
```

- **成功した場合**: 完了メッセージに `✅ ビルド確認済み` を追加する
- **失敗した場合**: エラー出力を表示し、原因箇所を特定して修正してから再実行する

### Mode 1 完了メッセージ

```
✅ セッション追加完了：<SESSION_ID>

生成：
  docs/sessions/<SESSION_ID>/index.md（概要ページ）
  docs/sessions/<SESSION_ID>/diagrams/architecture.mmd

更新：
  mkdocs.yml（nav にネストグループとして追加）
  docs/index.md（テーブルに追加）

次のステップ：
  担当者が決まったら以下のコマンドでサブセクション記事を追加してください：
  /add-textbook-session <SESSION_ID> <pdf-path> --sub <subsection-slug> [サブセクションタイトル] [担当者名]

確認：
  uv run mkdocs build --strict  ✅
  uv run mkdocs serve
```

---

## Mode 2: サブサブセクション深掘り記事追加

### Step 1: PDFと既存ページを読み込む

以下の2つを `Read` ツールで読み込む：

1. **PDF**: 指定されたサブサブセクションの内容に集中して読み込む。隣接するサブサブセクションのタイトルも把握し、前後の接続に備える
2. **既存の概要ページ** `docs/sessions/<session-id>/index.md`: サブサブセクション一覧テーブルの現状を把握する

`subsection-title` が省略されていた場合、PDFからタイトルを決定する。

発表者の決定（優先順位）: CLI引数 `presenter` → `config_presenter` → `（担当者名）`

### Step 2: 深掘り記事を生成

`docs/sessions/<session-id>/<subsection-slug>.md` を作成する。

**目標**: そのサブサブセクションを担当者が発表する際に参照できる、深く掘り下げた自己完結した解説記事。

**テンプレート**: まず `.claude/skills/add-textbook-session/assets/index_template.md` を Read し、構造を把握してから生成する。

**品質ガイドライン**:
- 数式はステップバイステップで導出し、各ステップに直感的な説明を添える
- Mermaid図を最低1つ含める（概念の視覚化）
- 前後のサブサブセクションとの接続を `!!! abstract` admonition で明示する
- 重要な洞察は `!!! note` / `!!! warning` / `!!! success` で強調する
- 担当者が議論・発表できる疑問点・考察を末尾に記載する

### Step 3: mkdocs.yml を更新（Mode 2）

既存セッショングループの末尾にサブページを追加する。

```yaml
    - <date> <display-title>:
      - 概要: sessions/<session-id>/index.md
      - <subsection-title>: sessions/<session-id>/<subsection-slug>.md  ← ここに追加
```

正確なインデント・Editパターンは `.claude/skills/add-textbook-session/references/session_format.md` を参照。

### Step 4: 概要ページの一覧テーブルを更新

`docs/sessions/<session-id>/index.md` のサブサブセクション一覧テーブルを更新する。

- 該当行が `準備中` の場合: リンクを `[詳細](<subsection-slug>.md)` に書き換える
- 該当行が存在しない場合: テーブル末尾に新規行を追加する

発表者名も判明していれば同時に更新する。

### Step 5: ビルド確認

```bash
uv run mkdocs build --strict
```

### Mode 2 完了メッセージ

```
✅ サブセクション記事追加完了：<session-id>/<subsection-slug>

生成：
  docs/sessions/<session-id>/<subsection-slug>.md（深掘り記事）

更新：
  mkdocs.yml（既存グループにサブページを追加）
  docs/sessions/<session-id>/index.md（一覧テーブルを更新）

確認：
  uv run mkdocs build --strict  ✅
  uv run mkdocs serve
```
