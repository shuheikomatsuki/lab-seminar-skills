# セッション追記フォーマット仕様

## mkdocs.yml — nav エントリの追記

### 対象ファイル
`mkdocs.yml`（リポジトリルート）

### 追記場所
`nav:` の `セッション:` リスト末尾

---

### Mode 1: 新規セッション（ネストグループとして追加）

新規セッションは**ネスト構造のグループ**として追加する。最初は概要ページのみ。

```yaml
nav:
  - ホーム: index.md
  - セッション:
    - 2026-04-18 DL Ch6.1 固定基底関数の限界: sessions/2026-04-18-dl-ch6-1/index.md  # 既存フラット
    - 2026-04-26 DL Ch6.2 多層ネットワーク: sessions/2026-04-26-6-2/index.md            # 既存フラット
    - <date> <display-title>:                                                             # ← ここに追加
      - 概要: sessions/<SESSION_ID>/index.md
```

**インデントルール:**
- セッション直下（グループ名行）: スペース4つ
- グループ内ページ: スペース6つ

**Edit ツール使用例（Mode 1）:**
```
old_string: "    - 2026-04-26 DL Ch6.2 多層ネットワーク: sessions/2026-04-26-6-2/index.md"
new_string:  "    - 2026-04-26 DL Ch6.2 多層ネットワーク: sessions/2026-04-26-6-2/index.md\n    - <date> <display-title>:\n      - 概要: sessions/<SESSION_ID>/index.md"
```

---

### Mode 2: 既存セッションへのサブページ追加

既存セッショングループの末尾のページ行の後に、新しいサブページ行を追加する。

```yaml
    - <date> <display-title>:
      - 概要: sessions/<SESSION_ID>/index.md
      - <subsection-title>: sessions/<SESSION_ID>/<subsection-slug>.md  ← ここに追加
```

**Edit ツール使用例（Mode 2、概要ページが最後の行の場合）:**
```
old_string: "      - 概要: sessions/<SESSION_ID>/index.md"
new_string:  "      - 概要: sessions/<SESSION_ID>/index.md\n      - <subsection-title>: sessions/<SESSION_ID>/<subsection-slug>.md"
```

すでに他のサブページがある場合は、最後のサブページ行を `old_string` として使うこと。

---

## docs/index.md — セッション一覧テーブルへの追記

### 対象ファイル
`docs/index.md`

### 追記場所
`## セッション一覧` テーブルの最終行の後

### テーブルの形式
```markdown
| 日付 | タイトル |
|------|----------|
| 2026-04-18 | [DL Ch6.1 固定基底関数の限界](sessions/2026-04-18-dl-ch6-1/index.md) |
| <date> | [<display-title>](sessions/<SESSION_ID>/index.md) |   ← ここに追加
```

### ルール
- 列数: 2列（日付・タイトル）
- タイトル列: Markdownリンク `[<display-title>](sessions/<SESSION_ID>/index.md)`

### Edit ツール使用例
既存の最後のテーブル行の後に追記する。
```
old_string: "| 2026-04-26 | [DL Ch6.2 多層ネットワーク](sessions/2026-04-26-6-2/index.md) |"
new_string:  "| 2026-04-26 | [DL Ch6.2 多層ネットワーク](sessions/2026-04-26-6-2/index.md) |\n| <date> | [<display-title>](sessions/<SESSION_ID>/index.md) |"
```
