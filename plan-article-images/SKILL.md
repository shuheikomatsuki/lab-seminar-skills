---
name: plan-article-images
description: Use this skill to add manual image-generation prompts and image-slot comments to existing seminar articles. Trigger when the user invokes /plan-article-images, wants to improve beginner readability with generated images, or wants prompts for Gemini, Google AI Studio, or nanobanana without calling an image API.
argument-hint: "<session-id> [page-md]"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# plan-article-images

既存のセッション記事を読み、初学者の理解を助けるための画像候補を設計します。画像生成APIは使いません。本文には `<!-- image-slot: <id> -->` を挿入し、生成プロンプトは `image_prompts.yml` に集約します。

---

## 引数

`$ARGUMENTS` を次の形式でパースしてください：

```
<session-id> [page-md]
```

- `session-id` (必須): `docs/sessions/<session-id>/` のディレクトリ名
- `page-md` (任意): 対象ページ。`index.md`、`6-3-1.md`、`6-3-1` のように指定できる。省略時はセッション内の `*.md` を対象にする

変数を定義する：

- `SESSION_ID = <session-id>`
- `SESSION_DIR = docs/sessions/<SESSION_ID>`
- `PROMPTS_FILE = docs/sessions/<SESSION_ID>/image_prompts.yml`
- `IMAGES_DIR = docs/sessions/<SESSION_ID>/images`
- `TARGET_FILES`: 対象 Markdown ファイルの配列

---

## Step 1: 前提確認

以下を確認し、満たさない場合は中断する。

- `SESSION_DIR` が存在する
- `page-md` が指定された場合、対象ファイルが `SESSION_DIR` 直下に存在する

`page-md` が指定されていない場合は、`SESSION_DIR` 直下の `*.md` を対象にする。`archive` やサブディレクトリ内の Markdown は対象外とする。

`IMAGES_DIR` が存在しない場合は作成する。

---

## Step 2: 既存プロンプトとスロットを把握する

以下を読み取る：

1. `PROMPTS_FILE` が存在する場合は全内容
2. `TARGET_FILES` 内の既存 `<!-- image-slot: ... -->`
3. `TARGET_FILES` 内の既存 Markdown 画像 `![...](images/...)`

既存の `id`、既存スロット、既存画像リンクは変更・削除しない。

---

## Step 3: 画像候補を選ぶ

各記事につき、追加候補は最大3件までにする。以下の優先順で、初学者の理解に効く箇所だけ選ぶ。

1. 直感説明の直後
2. 数式に入る直前、または数式の意味を説明した直後
3. 提案手法・処理フローの全体像説明の直後
4. `!!! warning` の近くで、誤解しやすい比較を補助する箇所

次のものは画像候補にしない：

- 論文や教科書の厳密な数値結果・表・原図の再現
- Mermaid で十分に表現できている構造図
- 画像がなくても本文だけで十分に理解できる箇所
- 1枚に複数の論点を詰め込む図

---

## Step 4: 本文に image-slot を挿入する

選んだ箇所に次の形式でコメントを挿入する。

```markdown
<!-- image-slot: <image-id> -->
```

`image-id` は次のルールで作る：

- ASCII小文字、数字、ハイフンのみ
- 記事内・`PROMPTS_FILE` 内で一意
- 内容がわかる短い名前にする（例: `function-composition-intuition`, `loss-landscape-comparison`）

既に適切な位置にスロットがある場合は重複して追加しない。

---

## Step 5: image_prompts.yml を作成または更新する

`PROMPTS_FILE` を次のスキーマで作成・更新する。

```yaml
images:
  - id: <image-id>
    article: <page.md>
    filename: images/<image-id>.png
    alt: "<画像の代替テキスト>"
    insert_after_heading: "<スロットを置いた見出し>"
    purpose: "<この画像で理解しやすくしたいポイント>"
    prompt: |
      <画像生成用プロンプト>
    notes: "<生成時の注意。文字崩れ・ラベル量・事実性など>"
```

既存ファイルがある場合：

- 既存の `images:` 配列を保つ
- 既存エントリの `id`、`filename`、`article` を変更しない
- 今回追加したスロットに対応するエントリだけ追記する
- 既存スロットに対応するエントリが欠けている場合は補完してよい

画像候補が1件もない場合、`PROMPTS_FILE` がなければ次の内容で作成する。

```yaml
images: []
```

---

## Step 6: ビルド確認

```bash
uv run mkdocs build --strict
```

- 成功した場合は完了メッセージに `✅ ビルド確認済み` を追加する
- 失敗した場合はエラー出力を表示し、原因箇所を特定して修正してから再実行する

---

## 完了メッセージ

```
✅ 画像プロンプト計画を追加しました: <SESSION_ID>

更新:
  docs/sessions/<SESSION_ID>/<対象ページ>（image-slot を追加）
  docs/sessions/<SESSION_ID>/image_prompts.yml
  docs/sessions/<SESSION_ID>/images/

次のステップ:
  1. image_prompts.yml の prompt を Gemini / Google AI Studio / nanobanana に貼り付ける
  2. 生成画像を filename のパスに保存する
  3. /insert-generated-images <SESSION_ID> で本文へ埋め込む

確認:
  uv run mkdocs build --strict  ✅
```
