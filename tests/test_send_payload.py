import logging
import subprocess
from typing import Any, Dict

import pytest
from pytest_mock import MockerFixture

from repo_dispatch_event_sender.src.dispatch.send_payload import build_payload, main

# Set up logging
logger = logging.getLogger(__name__)


def format_command(command: str) -> str:
    """Helper function to format a long command into multiple lines."""
    return "\n".join(command.split(" -f "))


def test_build_payload_with_bracket_array(caplog: pytest.LogCaptureFixture) -> None:
    """Test if the correct command is generated when using bracket array format."""
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "version_list": "[3.10,3.11,3.12]",
        "os_list": "[ubuntu-latest,macos-latest,windows-latest]",
    }
    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[version_list][]=3.10 "
        "-f client_payload[version_list][]=3.11 "
        "-f client_payload[version_list][]=3.12 "
        "-f client_payload[os_list][]=ubuntu-latest "
        "-f client_payload[os_list][]=macos-latest "
        "-f client_payload[os_list][]=windows-latest"
    )

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_with_single_item_array(caplog: pytest.LogCaptureFixture) -> None:
    """Test if the correct command is generated when using single item in bracket array."""
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "version_list": "[3.10]",
        "os_list": "[ubuntu-latest]",
    }
    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[version_list][]=3.10 "
        "-f client_payload[os_list][]=ubuntu-latest"
    )

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_with_empty_array(caplog: pytest.LogCaptureFixture) -> None:
    """Test if the correct command is generated when using empty arrays."""
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "version_list": "[]",
        "os_list": "[]",
    }
    expected_cmd = "gh api repos/example-repo/dispatches -f event_type=test_workflow"

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_with_custom_param(caplog: pytest.LogCaptureFixture) -> None:
    """Test if the correct command is generated when a custom parameter is provided."""
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "custom_param": "custom_value",
        "version_list": "[3.10]",
    }
    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[custom_param]=custom_value "
        "-f client_payload[version_list][]=3.10"
    )

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_with_list_input(caplog: pytest.LogCaptureFixture) -> None:
    """Test if the correct command is generated when input is already a list."""
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "version_list": ["3.10", "3.11"],
        "os_list": ["ubuntu-latest"],
    }
    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[version_list][]=3.10 "
        "-f client_payload[version_list][]=3.11 "
        "-f client_payload[os_list][]=ubuntu-latest"
    )

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_with_whitespace(caplog: pytest.LogCaptureFixture) -> None:
    """Test if the correct command is generated when input contains whitespace."""
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "version_list": "[ 3.10, 3.11 ]",
        "os_list": "[ubuntu-latest, macos-latest]",
    }
    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[version_list][]=3.10 "
        "-f client_payload[version_list][]=3.11 "
        "-f client_payload[os_list][]=ubuntu-latest "
        "-f client_payload[os_list][]=macos-latest"
    )

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_skips_default_values(caplog: pytest.LogCaptureFixture) -> None:
    """Test if default values are correctly skipped in the payload."""
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "ghpages_branch": "gh_pages",
        "custom_param": "default_value",
    }
    expected_cmd = "gh api repos/example-repo/dispatches -f event_type=test_workflow"

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_missing_required_keys(caplog: pytest.LogCaptureFixture) -> None:
    """Test if KeyError is raised when required keys are missing."""
    data: Dict[str, Any] = {"event_type": "test_workflow"}

    with caplog.at_level(logging.ERROR):
        with pytest.raises(KeyError):
            build_payload(data)
        logger.error("KeyError raised due to missing repository_name")


def test_main_with_all_variables(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test main function with all environment variables set."""
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: {
            "REPOSITORY_NAME": "example-repo",
            "EVENT_TYPE": "test_workflow",
            "GHPAGES_BRANCH": "custom-branch",
            "OS_LIST": "[ubuntu-latest,macos-latest]",
            "VERSION_LIST": "[3.10,3.11,3.12]",
            "CUSTOM_PARAM": "custom_value",
        }.get(key),
    )

    mock_subprocess = mocker.patch("subprocess.run", return_value=None)

    with caplog.at_level(logging.INFO):
        main()

    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[ghpages_branch]=custom-branch "
        "-f client_payload[os_list][]=ubuntu-latest "
        "-f client_payload[os_list][]=macos-latest "
        "-f client_payload[version_list][]=3.10 "
        "-f client_payload[version_list][]=3.11 "
        "-f client_payload[version_list][]=3.12 "
        "-f client_payload[custom_param]=custom_value"
    )

    actual_cmd = mock_subprocess.call_args[0][0]
    assert sorted(actual_cmd.split()) == sorted(expected_cmd.split())


def test_main_minimal_variables(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test main function with only required environment variables set."""
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: {
            "REPOSITORY_NAME": "example-repo",
            "EVENT_TYPE": "test_workflow",
        }.get(key),
    )

    mock_subprocess = mocker.patch("subprocess.run", return_value=None)

    with caplog.at_level(logging.INFO):
        main()

    expected_cmd = "gh api repos/example-repo/dispatches -f event_type=test_workflow"

    actual_cmd = mock_subprocess.call_args[0][0]
    assert actual_cmd == expected_cmd


def test_main_subprocess_error(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test main function when subprocess.run raises an error."""
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: {
            "REPOSITORY_NAME": "example-repo",
            "EVENT_TYPE": "test_workflow",
        }.get(key),
    )

    mock_subprocess = mocker.patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, "command")
    )

    with pytest.raises(subprocess.CalledProcessError):
        main()

    assert mock_subprocess.called
