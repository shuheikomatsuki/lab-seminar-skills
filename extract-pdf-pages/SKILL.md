---
name: extract-pdf-pages
description: Use this skill to extract a range of pages from a source PDF and save them as a new PDF. Trigger when the user invokes /extract-pdf-pages, wants to clip pages from a textbook or paper PDF, or needs to prepare a partial PDF before running /add-textbook-session.
argument-hint: "<pdf-key-or-path> <pages-or-section> [output-filename] [--output-dir <dir>]"
allowed-tools: [Read, Bash, Glob]
---

# extract-pdf-pages

`seminar_config.yml` に登録されたPDFキーまたは絶対パスから、指定ページ範囲を新しいPDFとして書き出します。

---

## 引数

```
<pdf-key-or-path> <pages-or-section> [output-filename] [--output-dir <dir>]
```

- `pdf-key-or-path` (必須): `pdf_sources` のキー（例: `dl-book`）または絶対パス
  - **判定**: `/` を含む、または `.pdf` で終わる → パスとみなす。それ以外 → キーとみなす
- `pages-or-section` (任意): ページ指定またはセクション番号
  - **物理ページ指定**:
    - 単ページ: `5`
    - 範囲: `10-25`
    - カンマ区切り: `10,12,15`
    - 混合: `10-15,20-25`
  - **セクション番号指定**: `^\d+(\.\d+)+$` にマッチする文字列（例: `6.3`, `6.3.5`）
    - PDFの本文見出しを自動検索し、物理ページ範囲を解決する
  - **省略**: 省略された場合はユーザーに確認する
- `output-filename` (任意): 出力ファイル名。省略時:
  - キー指定 + 物理ページ: `<key>_pp<pages>.pdf`（例: `dl-book_pp10-25.pdf`）
  - キー指定 + セクション番号: `<key>_<section>.pdf`（ドットをハイフンに変換、例: `dl-book_6-3.pdf`）
  - パス直指定 + 物理ページ: `extracted_pp<pages>.pdf`
  - パス直指定 + セクション番号: `extracted_<section>.pdf`（ドットをハイフンに変換）
- `--output-dir <dir>` (任意): 出力先ディレクトリ（絶対パスまたはプロジェクトルートからの相対パス）。省略時は `seminar_config.yml` の `pdf_output_dir`（未設定なら `pdfs`）

以下の変数を定義する：
- `SOURCE_PATH`: 解決済みの絶対パス
- `INPUT_MODE`: `"pages"` または `"section"`
- `PAGES_STR`: ページ指定文字列（物理ページ指定時は即確定、セクション番号指定時は Step 1.5 で確定）
- `SECTION_NUM`: セクション番号（セクション指定時のみ、例: `6.3`）
- `OUTPUT_DIR`: 解決済みの出力ディレクトリパス
- `OUTPUT_FILENAME`: 決定済みの出力ファイル名
- `OUTPUT_PATH`: `<OUTPUT_DIR>/<OUTPUT_FILENAME>`
- `SKILL_SOURCE_DIR` = この `SKILL.md` が置かれている `extract-pdf-pages` ディレクトリ

---

## Step 0: 設定ファイルの読み込み

`seminar_config.yml` が存在する場合、`Read` ツールで読み込み以下を取得する：
- `pdf_sources`: キー→絶対パスのマッピング（存在しない場合は空として扱う）
- `pdf_output_dir`: 出力ディレクトリのデフォルト（存在しない場合は `pdfs`）

ファイル自体が存在しない場合は両方とも未設定として扱う。

---

## Step 1: 引数解決

### 1-0: pages-or-section の判定

引数から `pages-or-section` の値を取り出す。

- **省略されている場合**: 以下を表示してユーザーに入力を求め、受け取った値で処理を続ける：
  ```
  ページ指定が省略されています。以下のいずれかで指定してください:
    - 物理ページ: 例 5, 10-25, 10,12,15
    - セクション番号: 例 6.3, 6.3.5
  ```

- **`^\d+(\.\d+)+$` にマッチする場合（セクション番号）**:
  - `INPUT_MODE = "section"`
  - `SECTION_NUM = <入力値>`（例: `6.3`）
  - `PAGES_STR` は未確定（Step 1.5 で確定する）

- **それ以外の場合（物理ページ番号）**:
  - `INPUT_MODE = "pages"`
  - `PAGES_STR = <入力値>`（即確定）

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
  - キー指定 + 物理ページ: `<key>_pp<PAGES_STR>.pdf`
  - キー指定 + セクション番号: `<key>_<SECTION_NUM の . を - に置換>.pdf`（例: `dl-book_6-3.pdf`）
  - パス直指定 + 物理ページ: `extracted_pp<PAGES_STR>.pdf`
  - パス直指定 + セクション番号: `extracted_<SECTION_NUM の . を - に置換>.pdf`

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

## Step 2.5: セクション番号の解決（セクション番号指定時のみ）

`INPUT_MODE == "section"` の場合のみ実行する。

```bash
uv run --with pypdf "$SKILL_SOURCE_DIR/scripts/resolve_section_pages.py" \
  "<SOURCE_PATH>" "<SECTION_NUM>"
```

このスクリプトは、`pdftotext` が利用できる場合は `pdftotext -layout` でPDF全体をテキスト化して高速に本文見出しを検索する。

- 初回実行時は `.cache/pdf-text/` にテキストキャッシュとメタデータを作成する
- 2回目以降はPDFの `size` / `mtime` が変わっていなければキャッシュを再利用する
- 期待速度の目安:
  - 初回: 数秒程度
  - キャッシュ利用時: 概ね1秒未満
- `pdftotext` は `poppler` に含まれる外部コマンドであり、未導入環境では自動的に `pypdf` ベースの従来方式へフォールバックする
- 診断ログや警告は stderr に出力され、stdout にはページ範囲のみを出力する

- **exit 0 の場合**: stdout の出力（例: `204-212`）を `PAGES_STR` に設定し、以下を表示する：
  ```
  セクション <SECTION_NUM> → 物理ページ <PAGES_STR> に解決しました。
  ```
- **exit 非ゼロの場合**: スクリプトの stderr 出力をユーザーに表示し、さらに以下を出力して停止する：
  ```
  セクション番号を自動解決できませんでした。
  物理ページ番号を直接指定して再試行してください:
    /extract-pdf-pages <pdf-key-or-path> <pages> [output-filename]
  ```

---

## Step 3: 出力ディレクトリの作成

```bash
mkdir -p "<OUTPUT_DIR>"
```

---

## Step 4: ページ抽出の実行

```bash
uv run --with pypdf "$SKILL_SOURCE_DIR/scripts/extract_pages.py" \
  "<SOURCE_PATH>" "<PAGES_STR>" "<OUTPUT_PATH>"
```

- exit code 0 の場合: Step 5 へ進む。
- exit code 非ゼロの場合: スクリプトの stderr 出力をユーザーに表示して停止する。

---

## Step 5: 完了メッセージ

物理ページ指定の場合:
```
✅ PDFページ抽出完了

ソース : <SOURCE_PATH>
ページ : <PAGES_STR>
出力   : <OUTPUT_PATH>

次のステップ（例）:
  /add-textbook-session <OUTPUT_PATH>
```

セクション番号指定の場合:
```
✅ PDFページ抽出完了

ソース   : <SOURCE_PATH>
セクション: <SECTION_NUM>
ページ   : <PAGES_STR>（自動解決）
出力     : <OUTPUT_PATH>

次のステップ（例）:
  /add-textbook-session <OUTPUT_PATH>
```
