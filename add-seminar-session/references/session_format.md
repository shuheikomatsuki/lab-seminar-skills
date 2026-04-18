# セッション追記フォーマット仕様

## mkdocs.yml — nav エントリの追記

### 対象ファイル
`mkdocs.yml`（リポジトリルート）

### 追記場所
`nav:` の `セッション:` リスト末尾

### 形式
```yaml
nav:
  - ホーム: index.md
  - セッション:
    - 2026-04-18 DL Ch6.1 固定基底関数の限界: sessions/2026-04-18-dl-ch6-1/index.md
    - <date> <display-title>: sessions/<date>-<slug>/index.md   ← ここに追加
```

### ルール
- インデント: スペース4つ（既存エントリと揃える）
- キー形式: `<date> <display-title>` （クォートなし）
- 値形式: `sessions/<SESSION_ID>/index.md` （クォートなし）
- `<SESSION_ID>` = `<date>-<slug>`

### Edit ツール使用例
既存の最後のセッションエントリの後に追記する。
```
old_string: "    - 2026-04-18 DL Ch6.1 固定基底関数の限界: sessions/2026-04-18-dl-ch6-1/index.md"
new_string:  "    - 2026-04-18 DL Ch6.1 固定基底関数の限界: sessions/2026-04-18-dl-ch6-1/index.md\n    - <date> <display-title>: sessions/<SESSION_ID>/index.md"
```

---

## docs/index.md — セッション一覧テーブルへの追記

### 対象ファイル
`docs/index.md`

### 追記場所
`## セッション一覧` テーブルの最終行の後

### テーブルの形式
```markdown
| 日付 | タイトル | 発表資料 |
|------|----------|----------|
| 2026-04-18 | [DL Ch6.1 固定基底関数の限界](sessions/2026-04-18-dl-ch6-1/index.md) | [スライド](sessions/2026-04-18-dl-ch6-1/slides.html) |
| <date> | [<display-title>](sessions/<SESSION_ID>/index.md) | [スライド](sessions/<SESSION_ID>/slides.html) |   ← ここに追加
```

### ルール
- 列数: 3列（日付・タイトル・発表資料）
- タイトル列: Markdownリンク `[<display-title>](sessions/<SESSION_ID>/index.md)`
- 発表資料列: `[スライド](sessions/<SESSION_ID>/slides.html)`
  - `slides.html` はCIで生成される（`slides.md` から Marp が生成）

### Edit ツール使用例
既存の最後のテーブル行の後に追記する。
```
old_string: "| 2026-04-18 | [DL Ch6.1 固定基底関数の限界](sessions/2026-04-18-dl-ch6-1/index.md) | [スライド](sessions/2026-04-18-dl-ch6-1/slides.html) |"
new_string:  "| 2026-04-18 | [DL Ch6.1 固定基底関数の限界](sessions/2026-04-18-dl-ch6-1/index.md) | [スライド](sessions/2026-04-18-dl-ch6-1/slides.html) |\n| <date> | [<display-title>](sessions/<SESSION_ID>/index.md) | [スライド](sessions/<SESSION_ID>/slides.html) |"
```
