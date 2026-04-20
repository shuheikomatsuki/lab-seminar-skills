---
name: insert-generated-images
description: Use this skill to replace image-slot comments in seminar articles with generated image Markdown links after the user has saved image files under a session images directory. Trigger when the user invokes /insert-generated-images or wants to embed generated Gemini, Google AI Studio, or nanobanana images into articles.
argument-hint: "<session-id> [--dry-run]"
allowed-tools: [Read, Bash]
---

# insert-generated-images

`image_prompts.yml` と `images/` 内の実ファイルを照合し、存在する画像だけを本文の `<!-- image-slot: <id> -->` に埋め込みます。画像生成APIは使いません。

---

## 引数

`$ARGUMENTS` を次の形式でパースしてください：

```
<session-id> [--dry-run]
```

- `session-id` (必須): `docs/sessions/<session-id>/` のディレクトリ名
- `--dry-run` (任意): 置換予定だけ表示し、Markdown ファイルは変更しない

変数を定義する：

- `SESSION_ID = <session-id>`
- `SESSION_DIR = docs/sessions/<SESSION_ID>`
- `PROMPTS_FILE = docs/sessions/<SESSION_ID>/image_prompts.yml`
- `SKILL_SOURCE_DIR` = この `SKILL.md` が置かれている `insert-generated-images` ディレクトリ
- `DRY_RUN = --dry-run が指定されているか`

---

## Step 1: 前提確認

以下を確認し、満たさない場合は中断する。

- `SESSION_DIR` が存在する
- `PROMPTS_FILE` が存在する

`image_prompts.yml` が存在しない場合は、先に `/plan-article-images <SESSION_ID>` を実行するよう案内して中断する。

---

## Step 2: 置換スクリプトを実行する

`DRY_RUN` の場合：

```bash
uv run python "$SKILL_SOURCE_DIR/scripts/insert_generated_images.py" \
  "docs/sessions/<SESSION_ID>" --dry-run
```

通常実行の場合：

```bash
uv run python "$SKILL_SOURCE_DIR/scripts/insert_generated_images.py" \
  "docs/sessions/<SESSION_ID>"
```

スクリプトは以下を行う：

- `image_prompts.yml` の `images` 配列を読み込む
- 各エントリの `article` と `filename` を `SESSION_DIR` からの相対パスとして扱う
- `filename` の画像ファイルが存在する場合だけ、対象記事内の `<!-- image-slot: <id> -->` を `![<alt>](<filename>)` に置換する
- 画像ファイルが存在しない場合はスロットを残し、未生成一覧に出す
- 対象記事やスロットが見つからない場合は警告として表示する
- `--dry-run` ではファイルを書き換えない

---

## Step 3: ビルド確認

`DRY_RUN` ではない場合のみ実行する。

```bash
uv run mkdocs build --strict
```

- 成功した場合は完了メッセージに `✅ ビルド確認済み` を追加する
- 失敗した場合はエラー出力を表示し、原因箇所を特定して修正してから再実行する

---

## 完了メッセージ

通常実行の場合：

```
✅ 生成画像を本文へ埋め込みました: <SESSION_ID>

置換:
  <スクリプト出力の置換一覧>

未生成:
  <スクリプト出力の未生成一覧>

確認:
  uv run mkdocs build --strict  ✅
```

`--dry-run` の場合：

```
Dry run: 生成画像の埋め込みプレビュー

置換予定:
  <スクリプト出力の置換予定>

未生成:
  <スクリプト出力の未生成一覧>

確認:
  実行する場合は --dry-run を外してください。
```
