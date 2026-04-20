---
name: setup-seminar-project
description: Use this skill to initialize a new MkDocs-based seminar documentation project from scratch. Trigger when the user invokes /setup-seminar-project, wants to create a new 勉強会サイト, or needs to set up the prerequisite project structure before using session-addition skills.
argument-hint: <project-name> [description] [output-dir]
allowed-tools: [Read, Write, Bash, Glob]
---

# setup-seminar-project

MkDocs + Material テーマを使った勉強会まとめサイトのプロジェクトを初期化します。
完了後すぐにセッション追加スキルを使える状態にします。

## 引数

`$ARGUMENTS` を次の形式でパースしてください：

```
<project-name> [description] [output-dir]
```

- `project-name` (必須): サイトタイトル（例: `研究室勉強会`）
- `description` (任意): 勉強会の説明文。省略時は空文字扱い
- `output-dir` (任意): 出力先ディレクトリパス。省略時はカレントディレクトリ (`.`)

変数を定義する：
- `PROJECT_DIR` = `<output-dir>`（省略時は `.`）
- `SITE_NAME` = `<project-name>`
- `SITE_DESC` = `<description>`（省略時は空文字）
- `PROJECT_SLUG` = `SITE_NAME` をASCIIスラッグ形式に変換したもの（例: `研究室勉強会` → `lab-seminars`、`My Lab` → `my-lab`）

## Step 1: 既存プロジェクトのチェック

`Glob` で `$PROJECT_DIR/mkdocs.yml` の存在を確認する。

ファイルが存在した場合は以下を出力して**中断**する：

```
⚠️  $PROJECT_DIR/mkdocs.yml が既に存在します。
上書きする場合は既存ファイルを削除してから再実行してください。
```

## Step 2: ディレクトリを作成する

```bash
mkdir -p "$PROJECT_DIR/docs/sessions"
mkdir -p "$PROJECT_DIR/docs/stylesheets"
mkdir -p "$PROJECT_DIR/.claude/skills"
```

## Step 3: pyproject.toml を生成する

`.claude/skills/setup-seminar-project/assets/pyproject_template.toml` を Read し、
`{{PROJECT_SLUG}}` を `PROJECT_SLUG` の値で置換して `$PROJECT_DIR/pyproject.toml` に Write する。

## Step 4: mkdocs.yml を生成する

`.claude/skills/setup-seminar-project/assets/mkdocs_template.yml` を Read し、
- `{{SITE_NAME}}` を `SITE_NAME` の値で置換
- `{{SITE_DESC}}` を `SITE_DESC` の値で置換

して `$PROJECT_DIR/mkdocs.yml` に Write する。

## Step 5: docs/index.md を生成する

`.claude/skills/setup-seminar-project/assets/index_template.md` を Read し、
- `{{SITE_NAME}}` を `SITE_NAME` の値で置換
- `{{SITE_DESC}}` を `SITE_DESC` の値で置換

して `$PROJECT_DIR/docs/index.md` に Write する。

## Step 6: extra.css と .gitignore を生成する

- `.claude/skills/setup-seminar-project/assets/extra_css_template.css` を Read して、`$PROJECT_DIR/docs/stylesheets/extra.css` に Write する（置換なし）
- `.claude/skills/setup-seminar-project/assets/gitignore_template.txt` を Read して、`$PROJECT_DIR/.gitignore` に Write する（置換なし）

## Step 7: lab-seminar-skills をサブモジュールとして登録する

以下を実行して `lab-seminar-skills` リポジトリを `.claude/skills/` としてサブモジュール登録する：

```bash
cd "$PROJECT_DIR"
git init
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .claude/skills
```

コマンドが失敗した場合は以下を出力してスキップする：

```
⚠️  git submodule の登録をスキップしました。
手動で以下を実行してスキルを導入してください:
  git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .claude/skills
または（git を使わない場合）:
  git clone https://github.com/shuheikomatsuki/lab-seminar-skills .claude/skills
```

## Step 8: uv sync を実行する

```bash
command -v uv >/dev/null 2>&1 && cd "$PROJECT_DIR" && uv sync
```

`uv` が存在しない場合は完了メッセージ内で案内する（中断はしない）。

## 完了メッセージ

全ステップ完了後、以下を出力する（`uv` が見つからなかった場合は注意書きを追加）：

```
✅ プロジェクト初期化完了: <PROJECT_DIR>/

生成ファイル:
  pyproject.toml
  mkdocs.yml
  docs/index.md
  docs/stylesheets/extra.css
  .gitignore
  .claude/skills/

次のステップ:
  1. cd <PROJECT_DIR>
  2. uv run mkdocs serve   → ローカルプレビュー (http://127.0.0.1:8000)
  3. 論文紹介: /add-paper-session <slug> pdfs/your-paper.pdf [タイトル] [YYYY-MM-DD]
     教科書:   /add-textbook-session <slug> pdfs/your-chapter.pdf [タイトル] [YYYY-MM-DD]
```

`uv` が見つからなかった場合の追記：

```
注意: uv が見つかりませんでした。以下のコマンドでインストール後、uv sync を実行してください:
  curl -LsSf https://astral.sh/uv/install.sh | sh
  cd <PROJECT_DIR> && uv sync
```
