
# Repo Dispatch Event Sender

[English](README.md) | 日本語

`repo-dispatch-event-sender` は、GitHub CLI (`gh`) を使用して[repository_dispatch](https://docs.github.com/ja/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#repository_dispatch)イベントをトリガーするためのPythonプロジェクトです。環境変数に基づいてペイロードを生成し、リポジトリ内の特定のワークフローを開始するために `gh` コマンドを実行します。

## 機能

- GitHubリポジトリディスパッチイベント用のペイロードを動的に生成します。
- 複数の環境や、OSおよびPythonバージョンのカスタマイズをサポートします。
- CI/CDワークフローに簡単に統合して自動ディスパッチを実現します。
- 将来的にはその他のペイロードもサポートできるようにしたいと思います。

## 使用条件

### 必須

- Python 3.10+
- GitHub CLI (`gh`)

### 任意

- 依存関係管理では[Poetry](https://python-poetry.org/) を推奨しますが、`venv`など、その他、仮想環境でも問題ありません。

## インストール

### リポジトリをクローンする

```bash
git clone https://github.com/yourusername/repo-dispatch-event-sender.git
cd repo-dispatch-event-sender
```

### 依存関係をインストールする

[Poetry](https://python-poetry.org/) がインストールされていることを確認し、以下を実行します。

```bash
poetry install
```

これにより、仮想環境が作成され、必要な依存関係がインストールされます。

venvなどの仮想環境の場合は、下記で依存関係をインストールしてください。

```bash
pip install requirement.txt requirement-dev.txt
```

## 設定

プロジェクトは、GitHub APIに送信されるペイロードを構成するために環境変数を使用します。

> [!NOTE]
> 事前に以下の**環境変数**を設定してください。

### 必須

- `REPOSITORY_NAME`: 対象リポジトリの名前 (例: `yourusername/yourrepo`)
- `EVENT_TYPE`: トリガーするイベントの種類 (例: `test_workflow`)
- `OS_LIST`: 対象OSバージョンのスペース区切りリスト (例: `ubuntu-latest macos-13 windows-latest`)
- `PYTHON_VERSIONS`: Pythonバージョンのスペース区切りリスト (例: `3.11 3.12`)

### 任意

- `GHPAGES_BRANCH`: GitHub Pagesブランチ (デフォルトは `gh_pages`)
- `CUSTOM_PARAM`: ペイロードのカスタムパラメータ（オプション）

これらの環境変数は、ターミナルで設定するか、CI/CDパイプラインの設定内で指定できます。

## 使用方法

### ディスパッチコマンドを実行する

GitHubリポジトリディスパッチイベントをトリガーするには、以下のコマンドを実行します。

> [!NOTE]
> 事前に設定記載の**環境変数**を設定してください。  
> 設定後は設定された環境変数に基づいて、GitHubにペイロードが送信されます。

```bash
poetry run python repo_dispatch_event_sender/src/dispatch/send_payload.py
```

### ワークフローの例

以下は、このプロジェクトをGitHub Actionsのワークフロー内で使用する例です。

> **Note**  
> ワークフローで使用する場合は`gh`コマンドのインストールは不要です。

```yaml
name: Sample Use repo-dispatch-event-sender Action

on:
  push:
    branches:
      - 'main'

jobs:
  test-and-send-dispatch:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4.2.1

      - name: Send Payload to Pytest Testmon
        uses: 7rikazhexde/repo-dispatch-event-sender@main
        with:
          repository_name: '7rikazhexde/repo-dispatch-event-sender'
          event_tyoe: 'repo-dispatch-event-receive'
          ghpages_branch: 'ghpages'  # オプション1
          os_list: 'ubuntu-latest macos-13 windows-latest'
          python_versions: '3.11 3.12'
          custom_param: 'custom_param_test_val'  # オプション2
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

> [!NOTE]
> オプション1:\
> デフォルト値(`'gh_pages'`)と異なるブランチ名を指定する場合はその値でペイロードを作成する。\
> 省略した場合もデフォルト値(`'gh_pages'`)でペイロードを作成する。  
>
> オプション2:\
> 省略可能。省略した場合はペイロードで送信しない。\
>
> ワークフローの実例:\
> [send_payload_to_pytest_testmon.yml](https://github.com/7rikazhexde/python-project-sandbox/blob/main/.github/workflows/send_payload_to_pytest_testmon.yml)

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。
