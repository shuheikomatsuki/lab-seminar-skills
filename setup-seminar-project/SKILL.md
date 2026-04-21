---
name: setup-seminar-project
description: Use this skill to initialize a new MkDocs-based seminar documentation project from scratch. Trigger when the user invokes /setup-seminar-project, wants to create a new 勉強会サイト, or needs to set up the prerequisite project structure before using session-addition skills.
argument-hint: <project-name> [description] [output-dir] [--skills-target .claude/skills|.agents/skills|both|none]
allowed-tools: [Read, Write, Bash, Glob]
---

# setup-seminar-project

MkDocs + Material テーマを使った勉強会まとめサイトのプロジェクトを初期化します。
完了後すぐにセッション追加スキルを使える状態にします。

画像生成APIキーや外部画像生成SDKは不要です。画像を使う場合も、スキルは `image_prompts.yml` と画像埋め込み導線だけを作り、実際の生成は Gemini / Google AI Studio / nanobanana などのチャット画面で手動実行します。

## 引数

`$ARGUMENTS` を次の形式でパースしてください：

```
<project-name> [description] [output-dir] [--skills-target .claude/skills|.agents/skills|both|none]
```

- `project-name` (必須): サイトタイトル（例: `研究室勉強会`）
- `description` (任意): 勉強会の説明文。省略時は空文字扱い
- `output-dir` (任意): 出力先ディレクトリパス。省略時はカレントディレクトリ (`.`)
- `--skills-target` (任意): `lab-seminar-skills` を導入する場所。
  - `.claude/skills`: Claude Code 用
  - `.agents/skills`: Codex 用
  - `both`: `.claude/skills` と `.agents/skills` の両方
  - `none`: スキル導入をスキップ
  - 省略時: Claude Code で実行中なら `.claude/skills`、Codex で実行中なら `.agents/skills`、判定できない場合は `.claude/skills`

変数を定義する：
- `PROJECT_DIR` = `<output-dir>`（省略時は `.`）
- `SITE_NAME` = `<project-name>`
- `SITE_DESC` = `<description>`（省略時は空文字）
- `PROJECT_SLUG` = `SITE_NAME` をASCIIスラッグ形式に変換したもの（例: `研究室勉強会` → `lab-seminars`、`My Lab` → `my-lab`）
- `SKILL_SOURCE_DIR` = この `SKILL.md` が置かれている `setup-seminar-project` ディレクトリ
- `SKILLS_TARGETS` = `--skills-target` から決定した導入先の配列

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
mkdir -p "$PROJECT_DIR/pdfs"
```

## Step 3: pyproject.toml を生成する

`$SKILL_SOURCE_DIR/assets/pyproject_template.toml` を Read し、
`{{PROJECT_SLUG}}` を `PROJECT_SLUG` の値で置換して `$PROJECT_DIR/pyproject.toml` に Write する。

## Step 4: mkdocs.yml を生成する

`$SKILL_SOURCE_DIR/assets/mkdocs_template.yml` を Read し、
- `{{SITE_NAME}}` を `SITE_NAME` の値で置換
- `{{SITE_DESC}}` を `SITE_DESC` の値で置換

して `$PROJECT_DIR/mkdocs.yml` に Write する。

## Step 5: docs/index.md を生成する

`$SKILL_SOURCE_DIR/assets/index_template.md` を Read し、
- `{{SITE_NAME}}` を `SITE_NAME` の値で置換
- `{{SITE_DESC}}` を `SITE_DESC` の値で置換

して `$PROJECT_DIR/docs/index.md` に Write する。

## Step 6: extra.css と .gitignore を生成する

- `$SKILL_SOURCE_DIR/assets/extra_css_template.css` を Read して、`$PROJECT_DIR/docs/stylesheets/extra.css` に Write する（置換なし）
- `$SKILL_SOURCE_DIR/assets/gitignore_template.txt` を Read して、`$PROJECT_DIR/.gitignore` に Write する（置換なし）

## Step 7: lab-seminar-skills を導入する

`SKILLS_TARGETS` が `none` の場合はこのステップをスキップする。

それ以外の場合は、`lab-seminar-skills` リポジトリを指定された skills ディレクトリへサブモジュール登録する。
各ターゲットについて親ディレクトリだけを作成し、skills ディレクトリ自体は上書きしない。

```bash
cd "$PROJECT_DIR"
test -d .git || git init
mkdir -p "$(dirname "<SKILLS_TARGET>")"
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills "<SKILLS_TARGET>"
```

`<SKILLS_TARGET>` が既に存在する場合は上書きせず、以下を出力してスキップする：

```
⚠️  <SKILLS_TARGET> が既に存在するため、git submodule の登録をスキップしました。
手動で以下を実行してスキルを導入してください:
  git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills <SKILLS_TARGET>
または（git を使わない場合）:
  git clone https://github.com/shuheikomatsuki/lab-seminar-skills <SKILLS_TARGET>
```

コマンドが失敗した場合も同じ案内を出してスキップする。

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
  pdfs/
  <SKILLS_TARGETS>

次のステップ:
  1. cd <PROJECT_DIR>
  2. uv run mkdocs serve   → ローカルプレビュー (http://127.0.0.1:8000)
  3. 公開する場合: /setup-github-pages-deploy
  4. 論文紹介: /add-paper-session <slug> pdfs/your-paper.pdf [タイトル] [YYYY-MM-DD]
     教科書:   /add-textbook-session <slug> pdfs/your-chapter.pdf [タイトル] [YYYY-MM-DD]
```

`uv` が見つからなかった場合の追記：

```
注意: uv が見つかりませんでした。以下のコマンドでインストール後、uv sync を実行してください:
  curl -LsSf https://astral.sh/uv/install.sh | sh
  cd <PROJECT_DIR> && uv sync
```
