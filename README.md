# lab-seminar-skills

Claude Code / Codex 向けのスキル集です。MkDocs ベースの勉強会まとめサイトを自動構築・更新するスキルを提供します。

## スキル一覧

| スキル | 説明 |
|--------|------|
| `add-seminar-session` | PDF（論文・教科書章）から解説記事・Marp スライド・Mermaid 図を自動生成し、セッションとして追加する |
| `setup-seminar-project` | MkDocs + Material テーマの勉強会サイトを新規初期化する |

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
cp -r /tmp/lab-seminar-skills/add-seminar-session .claude/skills/
cp -r /tmp/lab-seminar-skills/setup-seminar-project .claude/skills/
```

#### Codex

```bash
git clone https://github.com/shuheikomatsuki/lab-seminar-skills /tmp/lab-seminar-skills
cp -r /tmp/lab-seminar-skills/add-seminar-session .codex/skills/
cp -r /tmp/lab-seminar-skills/setup-seminar-project .codex/skills/
```

#### 更新

```bash
git -C /tmp/lab-seminar-skills pull
cp -r /tmp/lab-seminar-skills/add-seminar-session .claude/skills/
cp -r /tmp/lab-seminar-skills/setup-seminar-project .claude/skills/
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

### セッションの追加

```
/add-seminar-session [slug] <pdf-path> [display-title] [YYYY-MM-DD]
```

`slug` は省略可能です。省略時は PDF ファイル名から自動生成されます。
`date` は `seminar_config.yml` の `next_seminar_date` があればそちらを使います。

例:

```
# slug あり
/add-seminar-session dl-ch6-1 pdfs/deeplearning-ch6.pdf "DL Ch6.1 固定基底関数の限界"

# slug 省略（PDFファイル名から自動生成）
/add-seminar-session pdfs/deeplearning-ch6.pdf "DL Ch6.1 固定基底関数の限界"
```

**設定ファイル（任意）:** プロジェクトルートに `seminar_config.yml` を置くと、開催日・発表者名のデフォルト値を設定できます。

```yaml
next_seminar_date: 2026-04-25   # date引数省略時に使用
default_presenter: 山田太郎     # 担当:欄に自動挿入
```

生成物:
- `docs/sessions/<DATE>-<slug>/index.md` — 自己完結した解説記事
- `docs/sessions/<DATE>-<slug>/slides.md` — Marp スライド（10〜15枚）
- `docs/sessions/<DATE>-<slug>/diagrams/architecture.mmd` — Mermaid 概要図

## 動作確認済み環境

- Claude Code
- MkDocs + Material テーマ（`mkdocs-material >= 9.5`）
- uv パッケージマネージャー
