# lab-seminar-skills

Claude Code / Codex 向けのスキル集です。MkDocs ベースの勉強会まとめサイトを自動構築・更新するスキルを提供します。

## スキル一覧

| スキル | 説明 |
|--------|------|
| `add-seminar-session` | PDF（論文・教科書章）から解説記事・Marp スライド・Mermaid 図を自動生成し、セッションとして追加する |
| `setup-seminar-project` | MkDocs + Material テーマの勉強会サイトを新規初期化する |

## 導入方法

### Claude Code

```bash
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .claude/skills
```

### Codex

```bash
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .codex/skills
```

### 両方使う場合

```bash
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .claude/skills
git submodule add https://github.com/shuheikomatsuki/lab-seminar-skills .codex/skills
```

### サブモジュールの更新

```bash
git submodule update --remote .claude/skills
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
/add-seminar-session <slug> <pdf-path> [display-title] [YYYY-MM-DD]
```

例:

```
/add-seminar-session dl-ch6-1 pdfs/deeplearning-ch6.pdf "DL Ch6.1 固定基底関数の限界"
```

生成物:
- `docs/sessions/<DATE>-<slug>/index.md` — 自己完結した解説記事
- `docs/sessions/<DATE>-<slug>/slides.md` — Marp スライド（10〜15枚）
- `docs/sessions/<DATE>-<slug>/diagrams/architecture.mmd` — Mermaid 概要図

## 動作確認済み環境

- Claude Code
- MkDocs + Material テーマ（`mkdocs-material >= 9.5`）
- uv パッケージマネージャー
