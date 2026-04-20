---
name: remove-session-page
description: Use this skill to remove or archive one Markdown page inside an existing seminar session. Trigger when the user invokes /remove-session-page, wants to delete a specific .md page such as 6-2-3.md, archive a subsection page, or remove one page from a session nav.
argument-hint: "<session-id> <page-slug-or-md> [--delete] [--dry-run]"
allowed-tools: [Read, Edit, Bash, Glob, Grep]
---

# remove-session-page

既存セッション内の特定 `.md` ページだけを公開対象から外します。デフォルトでは `docs/` 外の `archive/sessions/` に退避し、`--delete` が明示された場合のみ完全削除します。

セッション全体、他のページ、`diagrams/`、PDF や `pdfs/` 配下の元資料は削除しません。

---

## 引数

`$ARGUMENTS` を次の形式でパースしてください：

```
<session-id> <page-slug-or-md> [--delete] [--dry-run]
```

- `session-id` (必須): `docs/sessions/<session-id>/` のディレクトリ名
- `page-slug-or-md` (必須): 対象ページ。`6-2-3` と `6-2-3.md` の両方を許容する
- `--delete` (任意): archive へ移動せず、対象ページを完全削除する
- `--dry-run` (任意): ファイル移動・削除・編集・ビルドを行わず、変更予定だけ表示する

変数を定義する：

- `SESSION_ID = <session-id>`
- `PAGE_FILE = <page-slug-or-md>` に `.md` がなければ付与した値
- `SESSION_DIR = docs/sessions/<SESSION_ID>`
- `TARGET_FILE = docs/sessions/<SESSION_ID>/<PAGE_FILE>`
- `ARCHIVE_FILE = archive/sessions/<SESSION_ID>/<PAGE_FILE>`
- `DELETE_MODE = --delete が指定されているか`
- `DRY_RUN = --dry-run が指定されているか`

---

## Step 1: 前提確認

以下を確認し、満たさない場合は中断する。

- `mkdocs.yml` が存在する
- `SESSION_DIR` が存在する
- `TARGET_FILE` が存在する
- `TARGET_FILE` は `SESSION_DIR` 直下の `.md` ファイルである
- `PAGE_FILE` は `index.md` ではない
- `DELETE_MODE` ではない場合、`ARCHIVE_FILE` が存在しない

`index.md` が指定された場合は、セッション全体を扱う `/remove-session <SESSION_ID>` を案内して中断する。

`ARCHIVE_FILE` が既に存在する場合は、上書きせず以下を出力して中断する：

```
Error: archive 先が既に存在します: archive/sessions/<SESSION_ID>/<PAGE_FILE>
既存 archive を確認してから再実行してください。
```

---

## Step 2: 参照と nav を検出する

以下を読み取り、対象箇所を特定する。

1. `mkdocs.yml` 内の `sessions/<SESSION_ID>/<PAGE_FILE>` を含む nav エントリ
2. `docs/sessions/<SESSION_ID>/index.md` 内の `<PAGE_FILE>` へのリンク
3. 同じ session 内の他 `.md` ファイルから `<PAGE_FILE>` へのリンク

`mkdocs.yml` の対象 nav は、通常次の形式の1行である。

```yaml
      - <page-title>: sessions/<SESSION_ID>/<PAGE_FILE>
```

この1行を削除する。対象 nav が見つからない場合は警告を出し、処理は続行する。

---

## Step 3: 残存リンクを扱う

`docs/sessions/<SESSION_ID>/index.md` または同じ session 内の他 `.md` ファイルから `PAGE_FILE` へのリンクが見つかった場合、`DRY_RUN` ではリンク元を表示する。`DRY_RUN` ではない場合は、削除・移動・編集を行わず中断する。

```
Error: 対象ページへのリンクが残っています。

リンク元:
  <file>: <line>

先にリンクを削除または更新してから再実行してください。
```

例外: 検出されたリンクが `mkdocs.yml` の nav エントリのみであれば中断しない。

---

## Step 4: dry-run 出力

`DRY_RUN` の場合は、変更を加えず以下を出力して終了する。残存リンクがある場合は `リンク元` として併記する。

```
Dry run: セッションページ削除プレビュー

対象:
  docs/sessions/<SESSION_ID>/<PAGE_FILE>

予定:
  <archive または delete の説明>
  mkdocs.yml の nav エントリ削除: <検出結果>
  残存リンク: <検出結果>

確認:
  実行する場合は --dry-run を外してください。
```

---

## Step 5: mkdocs.yml を更新

`mkdocs.yml` から `sessions/<SESSION_ID>/<PAGE_FILE>` を含む nav エントリ1行を `Edit` ツールで削除する。

対象 nav が見つからない場合は警告を出し、処理は続行する。

---

## Step 6: 対象ページを移動または削除

`DELETE_MODE` で分岐する。

### デフォルト: archive へ移動

```bash
mkdir -p "archive/sessions/<SESSION_ID>"
mv "docs/sessions/<SESSION_ID>/<PAGE_FILE>" "archive/sessions/<SESSION_ID>/<PAGE_FILE>"
```

### `--delete`: 完全削除

```bash
rm "docs/sessions/<SESSION_ID>/<PAGE_FILE>"
```

削除前に `TARGET_FILE` が `docs/sessions/<SESSION_ID>/` 直下の `.md` ファイルであり、`index.md` ではないことを再確認する。

---

## Step 7: ビルド確認

```bash
uv run mkdocs build --strict
```

- 成功した場合は完了メッセージに `✅ ビルド確認済み` を追加する
- 失敗した場合はエラー出力を表示し、`mkdocs.yml` や残存リンクなど修正対象を特定して報告する

---

## 完了メッセージ

archive の場合：

```
✅ セッションページを archive へ移動しました: <SESSION_ID>/<PAGE_FILE>

移動:
  docs/sessions/<SESSION_ID>/<PAGE_FILE>
  -> archive/sessions/<SESSION_ID>/<PAGE_FILE>

更新:
  mkdocs.yml（nav から削除）

確認:
  uv run mkdocs build --strict  ✅
```

`--delete` の場合：

```
✅ セッションページを完全削除しました: <SESSION_ID>/<PAGE_FILE>

削除:
  docs/sessions/<SESSION_ID>/<PAGE_FILE>

更新:
  mkdocs.yml（nav から削除）

確認:
  uv run mkdocs build --strict  ✅
```
