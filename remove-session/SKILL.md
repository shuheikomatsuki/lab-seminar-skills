---
name: remove-session
description: Use this skill to remove or archive an entire seminar session from a MkDocs-based lab-seminars project. Trigger when the user invokes /remove-session, wants to delete a セッション, archive a session, hide a session from GitHub Pages, or remove a session from nav and the session list.
argument-hint: "<session-id> [--delete] [--dry-run]"
allowed-tools: [Read, Edit, Bash, Glob, Grep]
---

# remove-session

セッション全体を公開対象から外します。デフォルトでは `docs/` 外の `archive/sessions/` に退避し、`--delete` が明示された場合のみ完全削除します。

PDF や `pdfs/` 配下の元資料は削除しません。

---

## 引数

`$ARGUMENTS` を次の形式でパースしてください：

```
<session-id> [--delete] [--dry-run]
```

- `session-id` (必須): `docs/sessions/<session-id>/` のディレクトリ名
- `--delete` (任意): archive へ移動せず、セッションディレクトリを完全削除する
- `--dry-run` (任意): ファイル移動・削除・編集・ビルドを行わず、変更予定だけ表示する

変数を定義する：

- `SESSION_ID = <session-id>`
- `SESSION_DIR = docs/sessions/<SESSION_ID>`
- `ARCHIVE_DIR = archive/sessions/<SESSION_ID>`
- `DELETE_MODE = --delete が指定されているか`
- `DRY_RUN = --dry-run が指定されているか`

---

## Step 1: 前提確認

以下を確認し、満たさない場合は中断する。

- `mkdocs.yml` が存在する
- `docs/index.md` が存在する
- `SESSION_DIR` が存在する
- `DELETE_MODE` ではない場合、`ARCHIVE_DIR` が存在しない

`ARCHIVE_DIR` が既に存在する場合は、上書きせず以下を出力して中断する：

```
Error: archive 先が既に存在します: archive/sessions/<SESSION_ID>
既存 archive を確認してから再実行してください。
```

---

## Step 2: 削除対象を検出する

以下を読み取り、対象箇所を特定する。

1. `SESSION_DIR` 配下の全ファイル
2. `mkdocs.yml` 内の `sessions/<SESSION_ID>/` を含む nav エントリ
3. `docs/index.md` 内の `sessions/<SESSION_ID>/index.md` を含むテーブル行

`mkdocs.yml` は次の2形式の両方に対応する。

### フラット形式

```yaml
    - <date> <display-title>: sessions/<SESSION_ID>/index.md
```

この1行を削除する。

### ネスト形式

```yaml
    - <date> <display-title>:
      - 概要: sessions/<SESSION_ID>/index.md
      - <subpage-title>: sessions/<SESSION_ID>/<subpage>.md
```

`sessions/<SESSION_ID>/` を含むセッショングループ全体を削除する。グループの範囲は、同じインデント階層の次の session 見出し、または `nav:` ブロック末尾までとする。

---

## Step 3: dry-run 出力

`DRY_RUN` の場合は、変更を加えず以下を出力して終了する。

```
Dry run: セッション削除プレビュー

対象:
  docs/sessions/<SESSION_ID>/

予定:
  <archive または delete の説明>
  mkdocs.yml の nav エントリ削除: <検出結果>
  docs/index.md の一覧行削除: <検出結果>

確認:
  実行する場合は --dry-run を外してください。
```

nav または一覧行が見つからない場合も dry-run は成功扱いとし、`未検出` と表示する。

---

## Step 4: mkdocs.yml を更新

Step 2 で特定した nav エントリを `Edit` ツールで削除する。

- フラット形式は該当1行のみ削除する
- ネスト形式はセッショングループ全体を削除する
- 対象 nav が見つからない場合は警告を出し、処理は続行する

---

## Step 5: docs/index.md を更新

`docs/index.md` のセッション一覧テーブルから、`sessions/<SESSION_ID>/index.md` を含む行を `Edit` ツールで削除する。

対象行が見つからない場合は警告を出し、処理は続行する。テーブルヘッダと区切り行は削除しない。

---

## Step 6: セッションディレクトリを移動または削除

`DELETE_MODE` で分岐する。

### デフォルト: archive へ移動

```bash
mkdir -p archive/sessions
mv "docs/sessions/<SESSION_ID>" "archive/sessions/<SESSION_ID>"
```

### `--delete`: 完全削除

```bash
rm -rf "docs/sessions/<SESSION_ID>"
```

`rm -rf` は `SESSION_DIR` が `docs/sessions/` 直下の既存ディレクトリであることを再確認してから実行する。

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
✅ セッションを archive へ移動しました: <SESSION_ID>

移動:
  docs/sessions/<SESSION_ID>/
  -> archive/sessions/<SESSION_ID>/

更新:
  mkdocs.yml（nav から削除）
  docs/index.md（一覧から削除）

確認:
  uv run mkdocs build --strict  ✅
```

`--delete` の場合：

```
✅ セッションを完全削除しました: <SESSION_ID>

削除:
  docs/sessions/<SESSION_ID>/

更新:
  mkdocs.yml（nav から削除）
  docs/index.md（一覧から削除）

確認:
  uv run mkdocs build --strict  ✅
```
