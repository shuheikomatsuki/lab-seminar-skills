# lab-seminar-skills

Claude Code / Codex 向けのスキル集です。MkDocs ベースの勉強会まとめサイトを自動構築・更新するスキルを提供します。

## スキル一覧

| スキル | 説明 |
|--------|------|
| `setup-seminar-project` | MkDocs + Material テーマの勉強会サイトを新規初期化する |
| `add-paper-session` | 論文 PDF から論文紹介記事・Mermaid 図を生成し、セッションとして追加する |
| `add-textbook-session` | 教科書 PDF から概要ページやサブセクション深掘り記事を生成し、セッションとして追加する |
| `extract-pdf-pages` | 登録済み PDF または PDF パスからページ範囲・セクション範囲を抽出する |
| `remove-session` | セッション全体を公開対象から外し、archive へ退避または完全削除する |
| `remove-session-page` | セッション内の特定 Markdown ページを公開対象から外し、archive へ退避または完全削除する |

## 導入方法

このリポジトリは、勉強会サイト本体ではなく **Claude Code / Codex に読み込ませるスキル集**です。
以下のコマンドは、これから記事を生成・更新したい **勉強会サイトのプロジェクトルート**で実行してください。

例:

```bash
mkdir my-lab-seminars
cd my-lab-seminars
git init
```

そのうえで、使う実行環境に合わせて次の場所へ導入します。

- Claude Code: プロジェクトルート直下の `.claude/skills`
- Codex: プロジェクトルート直下の `.agents/skills`

> **注意:** サブモジュール方式では `.claude/skills/` または `.agents/skills/` ディレクトリ全体がこのリポジトリに置き換わります。
> 独自スキルをそのディレクトリに置いている場合は、先にこのリポジトリへ移動してください。
> 独自スキルを別管理したい場合は、後述の **cp 方式** を使ってください。

### サブモジュール方式（推奨）

スキルの更新を `git submodule update --remote` で追跡できます。

#### Claude Code

```bash
mkdir -p .claude
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .claude/skills
```

#### Codex

```bash
mkdir -p .agents
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .agents/skills
```

#### 両方使う場合

```bash
mkdir -p .claude .agents
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .claude/skills
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .agents/skills
```

#### サブモジュールの更新

```bash
git submodule update --remote .claude/skills
git submodule update --remote .agents/skills
```

### cp 方式（独自スキルと共存させたい場合）

既存の `.claude/skills/` に独自スキルがある場合や、サブモジュールを使いたくない場合はこちら。
スキルファイルを手動でコピーするため、更新は再度 `cp` を実行してください。

#### Claude Code

```bash
git clone https://github.com/shuheikomatsuki/lab-seminar-skills /tmp/lab-seminar-skills
mkdir -p .claude/skills
cp -r /tmp/lab-seminar-skills/setup-seminar-project .claude/skills/
cp -r /tmp/lab-seminar-skills/add-paper-session .claude/skills/
cp -r /tmp/lab-seminar-skills/add-textbook-session .claude/skills/
cp -r /tmp/lab-seminar-skills/extract-pdf-pages .claude/skills/
cp -r /tmp/lab-seminar-skills/remove-session .claude/skills/
cp -r /tmp/lab-seminar-skills/remove-session-page .claude/skills/
```

#### Codex

```bash
git clone https://github.com/shuheikomatsuki/lab-seminar-skills /tmp/lab-seminar-skills
mkdir -p .agents/skills
cp -r /tmp/lab-seminar-skills/setup-seminar-project .agents/skills/
cp -r /tmp/lab-seminar-skills/add-paper-session .agents/skills/
cp -r /tmp/lab-seminar-skills/add-textbook-session .agents/skills/
cp -r /tmp/lab-seminar-skills/extract-pdf-pages .agents/skills/
cp -r /tmp/lab-seminar-skills/remove-session .agents/skills/
cp -r /tmp/lab-seminar-skills/remove-session-page .agents/skills/
```

#### 更新（Claude Code）

```bash
git -C /tmp/lab-seminar-skills pull
cp -r /tmp/lab-seminar-skills/setup-seminar-project .claude/skills/
cp -r /tmp/lab-seminar-skills/add-paper-session .claude/skills/
cp -r /tmp/lab-seminar-skills/add-textbook-session .claude/skills/
cp -r /tmp/lab-seminar-skills/extract-pdf-pages .claude/skills/
cp -r /tmp/lab-seminar-skills/remove-session .claude/skills/
cp -r /tmp/lab-seminar-skills/remove-session-page .claude/skills/
```

#### 更新（Codex）

```bash
git -C /tmp/lab-seminar-skills pull
cp -r /tmp/lab-seminar-skills/setup-seminar-project .agents/skills/
cp -r /tmp/lab-seminar-skills/add-paper-session .agents/skills/
cp -r /tmp/lab-seminar-skills/add-textbook-session .agents/skills/
cp -r /tmp/lab-seminar-skills/extract-pdf-pages .agents/skills/
cp -r /tmp/lab-seminar-skills/remove-session .agents/skills/
cp -r /tmp/lab-seminar-skills/remove-session-page .agents/skills/
```

## 使い方

### 0 から新しい勉強会サイトを作る流れ

1. 空のプロジェクトディレクトリを作成し、その直下へ移動します。
2. 上記のサブモジュール方式または cp 方式で、このスキル集を `.claude/skills` または `.agents/skills` に導入します。
3. `/setup-seminar-project` を実行して MkDocs プロジェクトを初期化します。
4. `uv run mkdocs serve` でローカルプレビューします。
5. PDF を `pdfs/` に置くか、`seminar_config.yml` の `pdf_sources` に登録して、各セッション追加スキルを実行します。

Codex で新規作成する例:

```bash
mkdir my-lab-seminars
cd my-lab-seminars
git init
mkdir -p .agents
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .agents/skills
```

その後 Codex に以下を依頼します。

```text
/setup-seminar-project 研究室勉強会 "深層学習輪講"
```

### 新規プロジェクトのセットアップ

```
/setup-seminar-project <project-name> [description] [output-dir] [--skills-target .claude/skills|.agents/skills|both|none]
```

例:

```
/setup-seminar-project 研究室勉強会 "深層学習輪講"
/setup-seminar-project 研究室勉強会 "深層学習輪講" . --skills-target .agents/skills
```

`setup-seminar-project` は `pyproject.toml`、`mkdocs.yml`、`docs/index.md`、`docs/stylesheets/extra.css`、`.gitignore`、`pdfs/` を作成し、可能であれば `lab-seminar-skills` を指定先の skills ディレクトリへサブモジュール登録します。
すでに skills ディレクトリが存在している場合は上書きせず、手動導入手順を表示して続行します。

### 論文紹介セッションの追加

```
/add-paper-session [slug] <pdf-path> [display-title] [YYYY-MM-DD]
```

`slug` は省略可能です。省略時は PDF ファイル名から自動生成されます。
`date` は `seminar_config.yml` の `next_seminar_date` があればそちらを使います。

例:

```
# slug あり
/add-paper-session attention-is-all-you-need pdfs/attention.pdf "Attention Is All You Need"

# slug 省略（PDFファイル名から自動生成）
/add-paper-session pdfs/attention.pdf "Attention Is All You Need"
```

### 教科書セッション概要の追加

```
/add-textbook-session [slug] <pdf-path> [display-title] [YYYY-MM-DD]
```

節全体の概要ページを作成し、サブサブセクション一覧と Mermaid 図を生成します。

例:

```
/add-textbook-session dl-ch6-3 pdfs/deeplearning-ch6-3.pdf "DL Ch6.3 ベイズ線形回帰"
```

### 教科書サブセクション記事の追加

```
/add-textbook-session <session-id> <pdf-path> --sub <subsection-slug> [subsection-title] [presenter]
```

既存の教科書セッションに、担当者別の深掘り記事を追加します。

例:

```
/add-textbook-session 2026-04-25-dl-ch6-3 pdfs/deeplearning-ch6-3.pdf --sub 6-3-1 "6.3.1 パラメータ分布" 山田太郎
```

### PDFページ抽出

```
/extract-pdf-pages <pdf-key-or-path> <pages-or-section> [output-filename] [--output-dir <dir>]
```

教科書全体の PDF から、指定ページまたはセクション番号に対応する範囲を抽出します。抽出した PDF は `/add-textbook-session` の入力に使えます。

例:

```
/extract-pdf-pages dl-book 6.3 dl-book_6-3.pdf
/extract-pdf-pages /absolute/path/to/textbook.pdf 204-212 dl-ch6-3.pdf --output-dir pdfs
```

### セッション全体の削除・非公開化

```
/remove-session <session-id> [--delete] [--dry-run]
```

デフォルトでは `docs/sessions/<session-id>/` を `archive/sessions/<session-id>/` へ移動し、`mkdocs.yml` の nav と `docs/index.md` の一覧から外します。
`--delete` を付けた場合のみ完全削除します。PDF は削除しません。

例:

```
# 変更予定だけ確認
/remove-session 2026-04-26-6-2 --dry-run

# archive へ退避
/remove-session 2026-04-26-6-2

# 完全削除
/remove-session 2026-04-26-6-2 --delete
```

### セッション内ページの削除・非公開化

```
/remove-session-page <session-id> <page-slug-or-md> [--delete] [--dry-run]
```

デフォルトでは `docs/sessions/<session-id>/<page>.md` を `archive/sessions/<session-id>/<page>.md` へ移動し、`mkdocs.yml` の該当 nav から外します。
`index.md` や同じセッション内の他ページから対象ページへのリンクが残っている場合は、削除・移動せず中断します。

例:

```
# 変更予定だけ確認
/remove-session-page 2026-04-26-6-2 6-2-3 --dry-run

# archive へ退避
/remove-session-page 2026-04-26-6-2 6-2-3

# 完全削除
/remove-session-page 2026-04-26-6-2 6-2-3.md --delete
```

**設定ファイル（任意）:** プロジェクトルートに `seminar_config.yml` を置くと、開催日・発表者名・PDFソースのデフォルト値を設定できます。

```yaml
next_seminar_date: 2026-04-25   # date引数省略時に使用
default_presenter: 山田太郎     # 担当:欄に自動挿入
pdf_output_dir: pdfs            # PDF抽出先のデフォルト
pdf_sources:
  dl-book: /absolute/path/to/deeplearning-book.pdf
```

生成物:
- 論文紹介: `docs/sessions/<DATE>-<slug>/index.md` と `diagrams/architecture.mmd`
- 教科書概要: `docs/sessions/<DATE>-<slug>/index.md` と `diagrams/architecture.mmd`
- 教科書サブセクション: `docs/sessions/<DATE>-<slug>/<subsection-slug>.md`
- PDF抽出: `pdfs/<output-filename>.pdf`（設定により変更可）
- セッション退避: `archive/sessions/<SESSION_ID>/`
- ページ退避: `archive/sessions/<SESSION_ID>/<page>.md`

## 動作確認済み環境

- Claude Code
- Codex
- MkDocs + Material テーマ（`mkdocs-material >= 9.5`）
- uv パッケージマネージャー
