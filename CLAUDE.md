# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A GitHub composite Action (published on the Marketplace as "Repo Dispatch Event Sender") plus a standalone Python script that fires a `repository_dispatch` event via the GitHub CLI (`gh api repos/<repo>/dispatches ...`). The runtime has **no third-party dependencies** (stdlib only, Python 3.11+); everything in `pyproject.toml`'s `dev` dependency group is tooling. The project is a uv *virtual* project (`[tool.uv] package = false`) — it is never built or installed as a package.

## Commands

Dependencies are managed with uv (`uv sync`; lockfile `uv.lock`). Tasks are defined via taskipy in `pyproject.toml`.

```bash
uv run pytest                                  # all tests (log_cli at INFO is enabled)
uv run pytest tests/test_send_payload.py::test_build_payload_with_custom_param   # single test
uv run task test_coverage                      # coverage (term-missing + htmlcov/)
uv run task test_ci_term                       # what CI uses: scripts/run_tests.py, writes pytest.xml / pytest-coverage.txt
uv run task test_testmon                       # pytest-testmon, only affected tests

uv run ruff check --fix repo_dispatch_event_sender
uv run ruff format
uv run mypy --config-file=pyproject.toml       # strict-ish: disallow_untyped_defs, covers src, tests, scripts
uv run pre-commit run --all-files              # also runs actionlint, shellcheck, markdownlint (README.md only), uv-lock
```

Run the script locally (requires `gh` authenticated and env vars `REPOSITORY_NAME`, `EVENT_TYPE`, `OS_LIST`, `VERSION_LIST`; optional `GHPAGES_BRANCH`, `CUSTOM_PARAM`):

```bash
uv run python repo_dispatch_event_sender/src/dispatch/send_payload.py
```

## Architecture

All logic lives in `repo_dispatch_event_sender/src/dispatch/send_payload.py`:

- `action.yml` (composite action) maps `with:` inputs to UPPERCASE env vars and runs the script with `python3 ${{ github.action_path }}/...` — so the script must stay runnable as a plain file with no installed deps.
- `main()` reads env vars for each key in `SUPPORTED_KEYS` (env name = key uppercased), then `build_payload()` turns them into a single `gh api` command string executed with `subprocess.run(..., shell=True)`.
- Keys in `ARRAY_KEYS` (`os_list`, `version_list`) use an unquoted bracket format `[a,b,c]` (parsed by `parse_array_input`) and are emitted as `-f client_payload[key][]=item`. Other string values become `-f client_payload[key]=value`.
- Values equal to entries in `DEFAULT_VALUES` are omitted from the payload, so the action's input defaults act as "not set". When changing a default in `action.yml`, keep `DEFAULT_VALUES` in sync.
- Adding a new payload field requires touching `SUPPORTED_KEYS` (and `ARRAY_KEYS`/`DEFAULT_VALUES` if relevant), `action.yml` inputs + `env:` mapping, and the README tables (`README.md` and `README-ja.md`).

### CI / workflows (the repo dogfoods itself)

- `send_payload_to_pytest.yml`: on push to `main` (paths: src, tests, `uv.lock`) it uses `7rikazhexde/repo-dispatch-event-sender@main` to send event `send_payload_to_pytest`.
- `receive_payload_to_pytest.yml`: triggered by that `repository_dispatch`; builds its OS × Python matrix directly from `client_payload.os_list` / `client_payload.version_list`. `repository_dispatch` only runs from the default branch, not on PRs.
- `prch_test_matrix_json.yml`: PR check; matrix comes from `.github/workflows/matrix.json` (via `json2vars-setter`), runs tests and enforces **≥90% coverage**.
- `update-version-and-release.yml`: manual `workflow_dispatch` that bumps `uv version --bump <type>`, tags `vX.Y.Z`, and creates a GitHub release. Commits starting with `Bump version` / `[skip ci]` are skipped by the dispatch workflow.

## Notes

- Coverage `branch = false` is intentional (pytest-testmon conflicts with branch coverage).
- Minimum Python is 3.11 (`requires-python`). Raising it was required because security fixes in transitive dev deps (e.g. `filelock` ≥4.2.1) dropped 3.10; Dependabot (`package-ecosystem: uv`) cannot resolve them otherwise. Keep `requires-python`, ruff `target-version`, `matrix.json`, `send_payload_to_pytest.yml`'s `version_list`, and the README "Requirements" sections consistent.
- Keep `README.md` and `README-ja.md` in sync when changing user-facing behavior.
