---
name: setup-github-pages-deploy
description: Use this skill to add an optional GitHub Actions workflow that deploys a MkDocs-based seminar site to GitHub Pages. Trigger when the user invokes /setup-github-pages-deploy, wants to publish the site, configure GitHub Pages, add GitHub Actions deployment, or deploy MkDocs to GitHub Pages.
argument-hint: "[--method actions|gh-pages] [--package-manager auto|uv|pip] [--branch main] [--python-version 3.12] [--site-url <url>] [--output .github/workflows/deploy.yml] [--dry-run]"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# setup-github-pages-deploy

MkDocs ベースの勉強会サイトに、GitHub Pages へデプロイするための GitHub Actions workflow を追加します。

既存 CI/CD を持つプロジェクトでは不要です。このスキルは任意で使うもので、既存 workflow は上書きしません。

---

## 引数

`$ARGUMENTS` を次の形式でパースしてください：

```
[--method actions|gh-pages] [--package-manager auto|uv|pip] [--branch main] [--python-version 3.12] [--site-url <url>] [--output .github/workflows/deploy.yml] [--dry-run]
```

- `--method` (任意): デプロイ方式。省略時は `actions`
  - `actions`: GitHub 公式 Pages Actions (`actions/upload-pages-artifact` + `actions/deploy-pages`) を使う
  - `gh-pages`: `peaceiris/actions-gh-pages` で `gh-pages` ブランチへ公開する
- `--package-manager` (任意): 依存インストール方式。省略時は `auto`
  - `auto`: `uv.lock` または `pyproject.toml` があれば `uv`、なければ `pip`
  - `uv`: `astral-sh/setup-uv` と `uv sync` / `uv run mkdocs build --strict` を使う
  - `pip`: `pip install mkdocs-material` と `mkdocs build --strict` を使う
- `--branch` (任意): workflow を発火するブランチ。省略時は `main`
- `--python-version` (任意): GitHub Actions 上の Python バージョン。省略時は `3.12`
- `--site-url` (任意): `mkdocs.yml` に設定する `site_url`
- `--output` (任意): workflow 出力先。省略時は `.github/workflows/deploy.yml`
- `--dry-run` (任意): ファイル作成・編集を行わず、変更予定だけ表示する

変数を定義する：

- `METHOD` = `--method` の値、未指定なら `actions`
- `PACKAGE_MANAGER` = `--package-manager` の値、未指定なら `auto`
- `BRANCH` = `--branch` の値、未指定なら `main`
- `PYTHON_VERSION` = `--python-version` の値、未指定なら `3.12`
- `SITE_URL_ARG` = `--site-url` の値
- `OUTPUT_PATH` = `--output` の値、未指定なら `.github/workflows/deploy.yml`
- `DRY_RUN` = `--dry-run` が指定されているか
- `SKILL_SOURCE_DIR` = この `SKILL.md` が置かれている `setup-github-pages-deploy` ディレクトリ

---

## Step 1: 前提確認

以下を確認し、満たさない場合は中断する。

- `mkdocs.yml` が存在する
- `METHOD` が `actions` または `gh-pages`
- `PACKAGE_MANAGER` が `auto`、`uv`、`pip` のいずれか

`OUTPUT_PATH` が既に存在する場合は、上書きせず以下を出力して中断する：

```
Error: workflow が既に存在します: <OUTPUT_PATH>
既存 CI/CD を確認し、必要であれば別の --output を指定するか、手動で統合してください。
```

---

## Step 2: package manager を決定

`PACKAGE_MANAGER` が `auto` の場合：

- `uv.lock` または `pyproject.toml` が存在すれば `RESOLVED_PACKAGE_MANAGER = uv`
- どちらも存在しなければ `RESOLVED_PACKAGE_MANAGER = pip`

`PACKAGE_MANAGER` が `uv` または `pip` の場合は、その値を `RESOLVED_PACKAGE_MANAGER` にする。

`RESOLVED_PACKAGE_MANAGER = uv` の場合：

- `uv.lock` が存在すれば `UV_SYNC_COMMAND = uv sync --frozen`
- `uv.lock` が存在しなければ `UV_SYNC_COMMAND = uv sync`

---

## Step 3: site_url を決定

`SITE_URL_ARG` が指定されている場合は、その値を `SITE_URL` にする。

未指定の場合は、以下のコマンドで GitHub remote URL を取得し、推定できる場合のみ `SITE_URL` を設定する：

```bash
git remote get-url origin
```

対応する remote 形式：

- `https://github.com/<owner>/<repo>.git`
- `https://github.com/<owner>/<repo>`
- `git@github.com:<owner>/<repo>.git`
- `git@github.com:<owner>/<repo>`

推定結果：

```
https://<owner>.github.io/<repo>/
```

ただし `<repo>` が `<owner>.github.io` の場合は、ユーザー/Organization Pages として次の URL にする：

```
https://<owner>.github.io/
```

remote がない、GitHub 以外、または形式を解釈できない場合は `SITE_URL` を未設定のままにする。

---

## Step 4: dry-run 出力

`DRY_RUN` の場合は、変更を加えず以下を出力して終了する。

```
Dry run: GitHub Pages デプロイ設定プレビュー

予定:
  workflow: <OUTPUT_PATH>
  method: <METHOD>
  package manager: <RESOLVED_PACKAGE_MANAGER>
  branch: <BRANCH>
  python: <PYTHON_VERSION>
  site_url: <SITE_URL または 未設定>

GitHub 側の設定:
  <METHOD に応じた案内>

確認:
  実行する場合は --dry-run を外してください。
```

GitHub 側の設定は次のように出力する：

- `actions`: `Settings > Pages > Build and deployment > Source を GitHub Actions に設定`
- `gh-pages`: `Settings > Pages > Build and deployment > Source を Deploy from a branch、Branch を gh-pages / root に設定`

---

## Step 5: workflow を生成

`METHOD` に応じてテンプレートを選ぶ。

- `actions`: `$SKILL_SOURCE_DIR/assets/deploy_pages_actions.yml`
- `gh-pages`: `$SKILL_SOURCE_DIR/assets/deploy_gh_pages.yml`

テンプレートを Read し、以下を置換して `OUTPUT_PATH` に Write する。

- `{{BRANCH}}` → `BRANCH`
- `{{PYTHON_VERSION}}` → `PYTHON_VERSION`
- `{{INSTALL_STEPS}}` → `RESOLVED_PACKAGE_MANAGER` に応じたインストール手順
- `{{BUILD_COMMAND}}` → `RESOLVED_PACKAGE_MANAGER` に応じたビルドコマンド

`OUTPUT_PATH` の親ディレクトリが存在しない場合は作成する。

### uv の置換値

`{{INSTALL_STEPS}}`:

```yaml
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "{{PYTHON_VERSION}}"

      - name: Install uv
        uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true

      - name: Install dependencies
        run: <UV_SYNC_COMMAND>
```

`{{BUILD_COMMAND}}`:

```yaml
uv run mkdocs build --strict
```

### pip の置換値

`{{INSTALL_STEPS}}`:

```yaml
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "{{PYTHON_VERSION}}"

      - name: Install MkDocs Material
        run: pip install mkdocs-material
```

`{{BUILD_COMMAND}}`:

```yaml
mkdocs build --strict
```

---

## Step 6: mkdocs.yml に site_url を設定

`SITE_URL` が未設定の場合、このステップはスキップする。

`SITE_URL` が設定されている場合：

- `mkdocs.yml` に `site_url:` が存在するなら、その値を `SITE_URL` に更新する
- `site_url:` が存在しないなら、`site_name:` 行の直後に `site_url: <SITE_URL>` を追加する

`site_name:` 行が見つからない場合は、ファイル先頭に `site_url: <SITE_URL>` を追加する。

---

## Step 7: 完了メッセージ

全ステップ完了後、以下を出力する。

`METHOD = actions` の場合：

```
✅ GitHub Pages デプロイ workflow を追加しました: <OUTPUT_PATH>

方式: GitHub 公式 Pages Actions
GitHub 側の設定:
  Settings > Pages > Build and deployment > Source を GitHub Actions に設定してください。

次のステップ:
  1. git add <OUTPUT_PATH> mkdocs.yml
  2. git commit -m "Add GitHub Pages deployment workflow"
  3. git push origin <BRANCH>
```

`METHOD = gh-pages` の場合：

```
✅ GitHub Pages デプロイ workflow を追加しました: <OUTPUT_PATH>

方式: gh-pages ブランチ
GitHub 側の設定:
  Settings > Pages > Build and deployment > Source を Deploy from a branch に設定し、
  Branch を gh-pages / root に設定してください。

次のステップ:
  1. git add <OUTPUT_PATH> mkdocs.yml
  2. git commit -m "Add GitHub Pages deployment workflow"
  3. git push origin <BRANCH>
```

`SITE_URL` が未設定だった場合は、完了メッセージに以下を追加する：

```
注意: site_url を自動推定できなかったため mkdocs.yml は更新していません。
必要に応じて mkdocs.yml に site_url: https://<owner>.github.io/<repo>/ を追加してください。
```
