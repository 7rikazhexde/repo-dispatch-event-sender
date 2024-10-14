
# Repo Dispatch Event Sender

English | [日本語](README-ja.md)

`repo-dispatch-event-sender` is a Python project designed to trigger [repository dispatch](https://docs.github.com/ja/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#repository_dispatch) events using the GitHub CLI (`gh`). It generates a payload based on environment variables and executes the `gh` command to initiate specific workflows in a repository.

## Features

- Dynamically generates payloads for GitHub repository dispatch events.
- Supports multiple environments and customizable parameters like OS and Python versions.
- Easily integrates with CI/CD workflows to automate dispatching.
- I hope to be able to support other payloads in the future.


## Requirements

### Mandatory

- Python 3.10+
- GitHub CLI (`gh`)

### Optional

- [Poetry](https://python-poetry.org/) is recommended for dependency management, but you can use other virtual environments like `venv`.

## Installation

### Clone the repository

```bash
git clone https://github.com/yourusername/repo-dispatch-event-sender.git
cd repo-dispatch-event-sender
```

### Install dependencies

If you are using [Poetry](https://python-poetry.org/), run the following command:

```bash
poetry install
```

This will create a virtual environment and install the necessary dependencies.

If using `venv` or another virtual environment, install the dependencies with:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

## Configuration

The project uses environment variables to configure the payload that will be sent to the GitHub API.

> [!NOTE]  
> Set the following **environment variables** before running the command.

### Mandatory

- `REPOSITORY_NAME`: Name of the target repository (e.g., `yourusername/yourrepo`)
- `EVENT_TYPE`: The event type to trigger (e.g., `test_workflow`)
- `OS_LIST`: Space-separated list of target OS versions (e.g., `ubuntu-latest macos-13 windows-latest`)
- `PYTHON_VERSIONS`: Space-separated list of Python versions (e.g., `3.11 3.12`)

### Optional

- `GHPAGES_BRANCH`: The branch used for GitHub Pages (default: `gh_pages`)
- `CUSTOM_PARAM`: Custom parameters for the payload (optional)

You can set these environment variables either in your terminal or within your CI/CD pipeline configuration.

## Usage

### Run the Dispatch Command

To trigger a GitHub repository dispatch event, run the following command.

> [!NOTE]  
> Ensure you have set the **environment variables** as listed in the configuration section.  
> Once set, the payload will be sent to GitHub based on these environment variables.

```bash
poetry run python repo_dispatch_event_sender/src/dispatch/send_payload.py
```

### Example Workflow

Below is an example of how to use this project in a GitHub Actions workflow.

> [!NOTE]
> Installation of the `gh` command is not required for use in workflow.

```yaml
name: Sample Use of repo-dispatch-event-sender Action

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
        # Temporarily using local path.
        # Replace with the remote URL after the repository is public.
        uses: ./
        with:
          repository_name: '7rikazhexde/repo-dispatch-event-sender'
          event_type: 'repo-dispatch-event-receive'
          ghpages_branch: 'ghpages'  # Optional-1
          os_list: 'ubuntu-latest macos-13 windows-latest'
          python_versions: '3.11 3.12'
          custom_param: 'custom_param_test_val'  # Optional-2
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

> [!NOTE]
> Optional-1
> - If you specify a branch name different from the default value (`'gh_pages'`), the payload is created with that value.
> - If omitted, payload is created with default value (`'gh_pages'`).
> 
> Optional-2
> - Can be omitted. The omitted double is not sent in the payload.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
