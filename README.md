# lab-seminar-skills

Claude Code / Codex 向けのスキル集です。MkDocs ベースの勉強会まとめサイトを自動構築・更新するスキルを提供します。

## スキル一覧

| スキル | 説明 |
|--------|------|
| `setup-seminar-project` | MkDocs + Material テーマの勉強会サイトを新規初期化する |
| `add-paper-session` | 論文 PDF から論文紹介記事・Mermaid 図を生成し、セッションとして追加する |
| `add-textbook-session` | 教科書 PDF から概要ページやサブセクション深掘り記事を生成し、セッションとして追加する |
| `extract-pdf-pages` | 登録済み PDF または PDF パスからページ範囲・セクション範囲を抽出する |

## 導入方法

> **注意:** サブモジュール方式では `.claude/skills/` または `.codex/skills/` ディレクトリ全体がこのリポジトリに置き換わります。
> 独自スキルをそのディレクトリに置いている場合は、先にこのリポジトリへ移動してください。
> 独自スキルを別管理したい場合は、後述の **cp 方式** を使ってください。

### サブモジュール方式（推奨）

スキルの更新を `git submodule update --remote` で追跡できます。

#### Claude Code

```bash
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .claude/skills
```

#### Codex

```bash
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .codex/skills
```

#### 両方使う場合

```bash
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .claude/skills
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .codex/skills
```

#### サブモジュールの更新

```bash
git submodule update --remote .claude/skills
git submodule update --remote .codex/skills
```

### cp 方式（独自スキルと共存させたい場合）

既存の `.claude/skills/` に独自スキルがある場合や、サブモジュールを使いたくない場合はこちら。
スキルファイルを手動でコピーするため、更新は再度 `cp` を実行してください。

#### Claude Code

```bash
git clone https://github.com/shuheikomatsuki/lab-seminar-skills /tmp/lab-seminar-skills
cp -r /tmp/lab-seminar-skills/setup-seminar-project .claude/skills/
cp -r /tmp/lab-seminar-skills/add-paper-session .claude/skills/
cp -r /tmp/lab-seminar-skills/add-textbook-session .claude/skills/
cp -r /tmp/lab-seminar-skills/extract-pdf-pages .claude/skills/
```

#### Codex

```bash
git clone https://github.com/shuheikomatsuki/lab-seminar-skills /tmp/lab-seminar-skills
cp -r /tmp/lab-seminar-skills/setup-seminar-project .codex/skills/
cp -r /tmp/lab-seminar-skills/add-paper-session .codex/skills/
cp -r /tmp/lab-seminar-skills/add-textbook-session .codex/skills/
cp -r /tmp/lab-seminar-skills/extract-pdf-pages .codex/skills/
```

#### 更新（Claude Code）

```bash
git -C /tmp/lab-seminar-skills pull
cp -r /tmp/lab-seminar-skills/setup-seminar-project .claude/skills/
cp -r /tmp/lab-seminar-skills/add-paper-session .claude/skills/
cp -r /tmp/lab-seminar-skills/add-textbook-session .claude/skills/
cp -r /tmp/lab-seminar-skills/extract-pdf-pages .claude/skills/
```

#### 更新（Codex）

```bash
git -C /tmp/lab-seminar-skills pull
cp -r /tmp/lab-seminar-skills/setup-seminar-project .codex/skills/
cp -r /tmp/lab-seminar-skills/add-paper-session .codex/skills/
cp -r /tmp/lab-seminar-skills/add-textbook-session .codex/skills/
cp -r /tmp/lab-seminar-skills/extract-pdf-pages .codex/skills/
```

## 使い方

### 新規プロジェクトのセットアップ

```
/setup-seminar-project <project-name> [description] [output-dir]
```

例:

```
/setup-seminar-project 研究室勉強会 "深層学習輪講"
```

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

## 動作確認済み環境

- Claude Code
- Codex
- MkDocs + Material テーマ（`mkdocs-material >= 9.5`）
- uv パッケージマネージャー
