---
name: extract-pdf-pages
description: Use this skill to extract a range of pages from a source PDF and save them as a new PDF. Trigger when the user invokes /extract-pdf-pages, wants to clip pages from a textbook or paper PDF, or needs to prepare a partial PDF before running /add-textbook-session.
argument-hint: "<pdf-key-or-path> <pages> [output-filename] [--output-dir <dir>]"
allowed-tools: [Read, Bash, Glob]
---

# extract-pdf-pages

`seminar_config.yml` に登録されたPDFキーまたは絶対パスから、指定ページ範囲を新しいPDFとして書き出します。

---

## 引数

```
<pdf-key-or-path> <pages> [output-filename] [--output-dir <dir>]
```

- `pdf-key-or-path` (必須): `pdf_sources` のキー（例: `dl-book`）または絶対パス
  - **判定**: `/` を含む、または `.pdf` で終わる → パスとみなす。それ以外 → キーとみなす
- `pages` (必須): 1-indexed のページ指定
  - 単ページ: `5`
  - 範囲: `10-25`
  - カンマ区切り: `10,12,15`
  - 混合: `10-15,20-25`
- `output-filename` (任意): 出力ファイル名。省略時:
  - キー指定の場合: `<key>_pp<pages>.pdf`（例: `dl-book_pp10-25.pdf`）
  - パス直指定の場合: `extracted_pp<pages>.pdf`
- `--output-dir <dir>` (任意): 出力先ディレクトリ（絶対パスまたはプロジェクトルートからの相対パス）。省略時は `seminar_config.yml` の `pdf_output_dir`（未設定なら `pdfs`）

以下の変数を定義する：
- `SOURCE_PATH`: 解決済みの絶対パス
- `PAGES_STR`: ページ指定文字列（そのまま）
- `OUTPUT_DIR`: 解決済みの出力ディレクトリパス
- `OUTPUT_FILENAME`: 決定済みの出力ファイル名
- `OUTPUT_PATH`: `<OUTPUT_DIR>/<OUTPUT_FILENAME>`

---

## Step 0: 設定ファイルの読み込み

`seminar_config.yml` が存在する場合、`Read` ツールで読み込み以下を取得する：
- `pdf_sources`: キー→絶対パスのマッピング（存在しない場合は空として扱う）
- `pdf_output_dir`: 出力ディレクトリのデフォルト（存在しない場合は `pdfs`）

ファイル自体が存在しない場合は両方とも未設定として扱う。

---

## Step 1: 引数解決

### 1-a: ソースPDFパスの解決

- **キーと判定された場合**: `pdf_sources[key]` を `SOURCE_PATH` とする。
  キーが `pdf_sources` に存在しない場合は以下を出力して停止する：

  ```
  Error: キー '<key>' が seminar_config.yml の pdf_sources に見つかりません。

  登録済みキー: <登録キー一覧、または「なし」>

  seminar_config.yml に以下を追加してください：
    pdf_sources:
      <key>: /absolute/path/to/your.pdf
  ```

- **パスと判定された場合**: そのまま `SOURCE_PATH` とする。

### 1-b: 出力ディレクトリの解決

- `--output-dir` が指定された場合: その値を `OUTPUT_DIR` とする。
- 省略された場合: `pdf_output_dir`（デフォルト: `pdfs`）を `OUTPUT_DIR` とする。

### 1-c: 出力ファイル名の決定

- `output-filename` が指定された場合: そのまま `OUTPUT_FILENAME` とする。
- 省略された場合:
  - キー指定なら: `<key>_pp<pages>.pdf`
  - パス直指定なら: `extracted_pp<pages>.pdf`

`OUTPUT_PATH = <OUTPUT_DIR>/<OUTPUT_FILENAME>` を確定する。

---

## Step 2: ソースPDFの存在確認

```bash
test -f "<SOURCE_PATH>"
```

ファイルが存在しない場合は以下を出力して停止する：

```
Error: ソースPDFが見つかりません: <SOURCE_PATH>
```

---

## Step 3: 出力ディレクトリの作成

```bash
mkdir -p "<OUTPUT_DIR>"
```

---

## Step 4: ページ抽出の実行

```bash
uv run --with pypdf .claude/skills/extract-pdf-pages/assets/extract_pages.py \
  "<SOURCE_PATH>" "<PAGES_STR>" "<OUTPUT_PATH>"
```

- exit code 0 の場合: Step 5 へ進む。
- exit code 非ゼロの場合: スクリプトの stderr 出力をユーザーに表示して停止する。

---

## Step 5: 完了メッセージ

```
✅ PDFページ抽出完了

ソース : <SOURCE_PATH>
ページ : <PAGES_STR>
出力   : <OUTPUT_PATH>

次のステップ（例）:
  /add-textbook-session <OUTPUT_PATH>
```
