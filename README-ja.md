# Repo Dispatch Event Sender

[![Run Tests Multi-OS](https://github.com/7rikazhexde/repo-dispatch-event-sender/actions/workflows/receive_payload_to_pytest.yml/badge.svg)](https://github.com/7rikazhexde/repo-dispatch-event-sender/actions/workflows/receive_payload_to_pytest.yml)

[English](README.md) | 日本語

`repo-dispatch-event-sender` は、GitHub CLI ([gh](https://docs.github.com/ja/github-cli/github-cli)) を使用して[repository_dispatch](https://docs.github.com/ja/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#repository_dispatch) webhookイベントをトリガーするためのPythonプロジェクトです。環境変数に基づいてペイロードを作成し、リポジトリ内の特定のワークフローを開始するために `gh` コマンドを実行します。

## 目次

- [Repo Dispatch Event Sender](#repo-dispatch-event-sender)
  - [目次](#目次)
  - [機能](#機能)
  - [使用条件](#使用条件)
    - [必須](#必須)
    - [任意](#任意)
  - [使用方法](#使用方法)
    - [Python向け](#python向け)
      - [プロジェクトをクローンする](#プロジェクトをクローンする)
      - [依存関係をインストールする](#依存関係をインストールする)
      - [設定](#設定)
      - [使用方法](#使用方法-1)
    - [ワークフロー向け](#ワークフロー向け)
      - [ワークフローの実例](#ワークフローの実例)
  - [ライセンス](#ライセンス)

## 機能

- [repository_dispatch](https://docs.github.com/ja/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#repository_dispatch) webhookイベントのトリガーはPythonコマンドとGitHub Actionsのアクションコンポーネントで実行できます。
- 複数の環境や、OSおよびPythonバージョンのカスタマイズをサポートします。(現状はバージョンはPythonのみサポート)

## 使用条件

### 必須

- Python 3.10+
- GitHub CLI (`gh`)

### 任意

- [Poetry](https://python-poetry.org/)

## 使用方法

### Python向け

#### プロジェクトをクローンする

```bash
git clone https://github.com/yourusername/repo-dispatch-event-sender.git
cd repo-dispatch-event-sender
```

#### 依存関係をインストールする

[Poetry](https://python-poetry.org/) がインストールされていることを確認し、以下を実行します。これにより、仮想環境が作成され、必要な依存関係がインストールされます。

```bash
poetry install
```

`venv`などの仮想環境を使用する場合は、下記で依存関係をインストールしてください。

```bash
pip install requirement.txt requirement-dev.txt
```

#### 設定

プロジェクトでは、GitHub APIに送信されるペイロードを作成するために環境変数を使用します。

> [!NOTE]
> 事前に以下の**環境変数**を設定してください。

| 入力項目           | 説明                                                                           |Required|
|-------------------|--------------------------------------------------------------------------------|--------|
| `REPOSITORY_NAME` | 対象リポジトリの名前 (例: `yourusername/yourrepo`)                              | Yes    |
| `EVENT_TYPE`      | トリガーするイベントの種類 (例: `test_workflow`)                                 | Yes    |
| `OS_LIST`         | ブラケット形式のカンマ区切りOS一覧 (例: '[ubuntu-latest,macos-13,windows-latest]') | Yes    |
| `VERSION_LIST` | ブラケット形式のカンマ区切りPythonバージョン一覧 (例: Pythonの場合: '[3.11,3.12]')               | Yes    |
| `GHPAGES_BRANCH`  | GitHub Pagesブランチ (デフォルトは `gh_pages`)                                  | No     |
| `CUSTOM_PARAM`    | ペイロードのカスタムパラメータ（オプション）                                      | No     |

#### 使用方法

GitHubリポジトリディスパッチイベントをトリガーするには、以下のコマンドを実行します。

```bash
poetry run python repo_dispatch_event_sender/src/dispatch/send_payload.py
```

### ワークフロー向け

> [!NOTE]
> ワークフローで使用する場合は`gh`コマンドのインストールは不要です。
>
> ペイロードは環境変数を元に送信されますが、ワークフローではアクションコンポーネントによって定義される入力パラメーターを`with`で設定してください。ワークフロー内で指定することで内部で環境変数の設定とペイロード作成と送信が実行されます。

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
          event_type: 'repo-dispatch-event-receive'
          ghpages_branch: 'ghpages'  # オプション1
          os_list: '[ubuntu-latest,macos-13,windows-latest]'
          version_list: '[3.11,3.12]'
          custom_param: 'custom_param_test_val'  # オプション2
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }} # オプション3
          #GH_TOKEN: ${{ secrets.YOURT_GHA_PAT }} # オプション3
```

> [!NOTE]
> **オプション1:**\
> デフォルト値(`'gh_pages'`)と異なるブランチ名を指定する場合はその値でペイロードを作成します。\
> 省略した場合はデフォルト値(`'gh_pages'`)でペイロードを作成します。  
>
> **オプション2:**\
> 省略可能です。省略した場合はペイロードに含まれません。

> [!IMPORTANT]
> **オプション3:**\
>\
> `GITHUB_TOKEN`:\
> GitHub Actions で自動的に発行されるトークンで、リポジトリへのアクセス権を持ちます。\
> GITHUB_TOKEN を使用する場合は、Actions -> Workflow permissions から Read and write permissions を有効にしてください。\
> セキュリティの観点から、`GITHUB_TOKEN` の使用が推奨されます。\
>\
> `Personal Access Token (PAT)`:\
> `GITHUB_TOKEN` では対応できない操作が必要な場合は、リポジトリ権限を付与した `PAT` を設定する必要があります。\
> `PAT` は適切に管理し、漏洩リスクを防ぐよう注意してください。

#### ワークフローの実例

[send_payload_to_pytest_testmon.yml](https://github.com/7rikazhexde/python-project-sandbox/blob/main/.github/workflows/send_payload_to_pytest_testmon.yml)

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。
