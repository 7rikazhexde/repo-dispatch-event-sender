# Repo Dispatch Event Sender

[![Run Tests Multi-OS](https://github.com/7rikazhexde/repo-dispatch-event-sender/actions/workflows/receive_payload_to_pytest.yml/badge.svg)](https://github.com/7rikazhexde/repo-dispatch-event-sender/actions/workflows/receive_payload_to_pytest.yml) [![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Repo%20Dispatch%20Event%20Sender-green?colorA=24292e&colorB=3fb950&logo=github)](https://github.com/marketplace/actions/repo-dispatch-event-sender)

English | [日本語](README-ja.md)

`repo-dispatch-event-sender` is a Python project designed to trigger [repository_dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#repository_dispatch) webhook events using the GitHub CLI ([gh](https://docs.github.com/en/github-cli/github-cli)). It generates payloads based on environment variables and executes the `gh` command to start specific workflows within a repository.

## ToC

- [Repo Dispatch Event Sender](#repo-dispatch-event-sender)
  - [ToC](#toc)
  - [Features](#features)
  - [Requirements](#requirements)
    - [Mandatory](#mandatory)
    - [Optional](#optional)
  - [Usage](#usage)
    - [For Python Use](#for-python-use)
      - [Clone the Project](#clone-the-project)
      - [Install Dependencies](#install-dependencies)
      - [Configuration](#configuration)
      - [How to Use](#how-to-use)
    - [For Workflow Use](#for-workflow-use)
      - [Example workflow](#example-workflow)
        - [Send payload workflow: send\_payload\_to\_pytest.yml](#send-payload-workflow-send_payload_to_pytestyml)
        - [Receive payload workflow: receive\_payload\_to\_pytest.yml](#receive-payload-workflow-receive_payload_to_pytestyml)
  - [License](#license)

## Features

- Triggers [repository_dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#repository_dispatch) webhook events via Python commands and GitHub Actions components.
- Support payloads such as `os` and `version`.

> [!IMPORTANT]
> The repository_dispatch event works with push triggers to the main branch, but it does not trigger on pull request events. Therefore, please be aware that the repository_dispatch event cannot be used with pull request events. For more details, please refer to the [official GitHub documentation](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow#triggering-a-workflow-from-a-workflow).

## Requirements

### Mandatory

- Python 3.10+
- GitHub CLI (`gh`)

### Optional

- [Poetry](https://python-poetry.org/)

## Usage

### For Python Use

#### Clone the Project

```bash
git clone https://github.com/7rikazhexde/repo-dispatch-event-sender.git
cd repo-dispatch-event-sender
```

#### Install Dependencies

If [Poetry](https://python-poetry.org/) is installed, run the following to create a virtual environment and install all necessary dependencies:

```bash
poetry install
```

If you are using another virtual environment like `venv`, install dependencies with:

```bash
pip install -r requirements.txt requirements-dev.txt
```

#### Configuration

The project uses environment variables to create the payloads sent to the GitHub API.

> [!NOTE]
> Please ensure the following **environment variables** are set beforehand.

| Input             | Description                                                                                | Required |
|-------------------|--------------------------------------------------------------------------------------------|----------|
| `REPOSITORY_NAME` | The name of the target repository (e.g., 'yourusername/yourrepo')                          | Yes      |
| `EVENT_TYPE`      | The type of event to trigger (e.g., 'test_workflow')                                       | Yes      |
| `OS_LIST`         | A comma-separated list of OS in brackets (e.g., '[ubuntu-latest,macos-13,windows-latest]') | Yes      |
| `VERSION_LIST`    | A comma-separated list of versions in brackets (e.g., for Python: '[3.11,3.12,3.13]')      | Yes      |
| `GHPAGES_BRANCH`  | The GitHub Pages branch (default is 'gh_pages')                                            | No       |
| `CUSTOM_PARAM`    | Custom parameters for the payload (optional)                                               | No       |

#### How to Use

To trigger the GitHub repository dispatch event, run the following command:

```bash
poetry run python repo_dispatch_event_sender/src/dispatch/send_payload.py
```

### For Workflow Use

> [!NOTE]
> When using this in a workflow, the `gh` command installation is not required.
>
> The payload will be sent based on the environment variables, but in workflows, you should configure the input parameters defined by the action component using `with`. Once specified in the workflow, it will automatically set the environment variables, create, and send the payload internally.

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
          ghpages_branch: 'ghpages'  # Option 1
          os_list: '[ubuntu-latest,macos-13,windows-latest]'
          version_list: '[3.11,3.12]'
          custom_param: 'custom_param_test_val'  # Option 2
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }} # Option 3
          #GH_TOKEN: ${{ secrets.YOURT_GHA_PAT }} # Option 3
```

> [!NOTE]
> **Option 1:**\
> If you want to specify a branch name different from the default (`'gh_pages'`), use that value to create the payload.\
> If omitted, the default value (`'gh_pages'`) will be used.  
>
> **Option 2:**\
> This is optional. If omitted, the custom parameter will not be included in the payload.

> [!IMPORTANT]  
> **Option 3:**\
> `GITHUB_TOKEN`:  
> This is a token automatically issued by GitHub Actions, providing access to the repository.  
> If you use `GITHUB_TOKEN`, please enable **Read and write permissions** under **Actions -> Workflow permissions**.  
> For security reasons, the use of `GITHUB_TOKEN` is recommended.  
>\
> `Personal Access Token (PAT)`:  
> If you need to perform actions that are not supported by `GITHUB_TOKEN`, you must configure a `PAT` with repository permissions.  
> Make sure to manage `PAT` carefully to prevent any leakage risks.  

#### Example workflow

##### Send payload workflow: [send_payload_to_pytest.yml](https://github.com/7rikazhexde/repo-dispatch-event-sender/blob/main/.github/workflows/send_payload_to_pytest.yml)

##### Receive payload workflow: [receive_payload_to_pytest.yml](https://github.com/7rikazhexde/repo-dispatch-event-sender/blob/main/.github/workflows/receive_payload_to_pytest.yml)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
