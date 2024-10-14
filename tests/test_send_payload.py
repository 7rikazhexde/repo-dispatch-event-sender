import logging
from typing import Any, Dict

import pytest
from pytest_mock import MockerFixture

from repo_dispatch_event_sender.src.dispatch.send_payload import build_payload, main

# Set up logging
logger = logging.getLogger(__name__)


def format_command(command: str) -> str:
    """Helper function to format a long command into multiple lines."""
    return "\n".join(command.split(" -f "))


def test_build_payload_with_os_list(caplog: pytest.LogCaptureFixture) -> None:
    """
    Test if the correct command is generated when OS list and Python versions are included.

    Args:
        None

    Returns:
        None
    """
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "ghpages_branch": "gh_pages",
        "os_list": ["ubuntu-latest", "macos-13", "windows-latest"],
        "python_versions": ["3.11", "3.12"],
    }
    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[ghpages_branch]=gh_pages "
        "-f client_payload[os_list][]=ubuntu-latest "
        "-f client_payload[os_list][]=macos-13 "
        "-f client_payload[os_list][]=windows-latest "
        "-f client_payload[python_versions][]=3.11 "
        "-f client_payload[python_versions][]=3.12"
    )

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_with_custom_param(caplog: pytest.LogCaptureFixture) -> None:
    """
    Test if the correct command is generated when a custom parameter is provided.

    Args:
        None

    Returns:
        None
    """
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "custom_param": "custom_value",
    }
    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[custom_param]=custom_value"
    )

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_skips_default_values(caplog: pytest.LogCaptureFixture) -> None:
    """
    Test if the command correctly skips default values like 'gh_pages' for ghpages_branch.

    Args:
        None

    Returns:
        None
    """
    data: Dict[str, Any] = {
        "repository_name": "example-repo",
        "event_type": "test_workflow",
        "ghpages_branch": "gh_pages",
    }
    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[ghpages_branch]=gh_pages"
    )

    with caplog.at_level(logging.INFO):
        assert build_payload(data) == expected_cmd
        logger.info(f"Generated command:\n{format_command(expected_cmd)}")


def test_build_payload_missing_required_keys(caplog: pytest.LogCaptureFixture) -> None:
    """
    Test if the correct error (KeyError) is raised when required keys are missing.

    Args:
        None

    Returns:
        None
    """
    data: Dict[str, Any] = {
        "event_type": "test_workflow",
    }

    with caplog.at_level(logging.ERROR):
        with pytest.raises(KeyError):
            build_payload(data)
        logger.error("KeyError raised due to missing repository_name")


def test_main_success_1(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test if the correct command is generated when ghpages_branch is set to the default value
    and other environment variables are present.

    Args:
        mocker: MockerFixture
        caplog: LogCaptureFixture

    Returns:
        None
    """
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: {
            "REPOSITORY_NAME": "example-repo",
            "EVENT_TYPE": "test_workflow",
            "GHPAGES_BRANCH": "gh_pages",  # Default value
            "OS_LIST": "ubuntu-latest macos-13 windows-latest",
            "PYTHON_VERSIONS": "3.11 3.12",
            "CUSTOM_PARAM": "custom_value",
        }.get(key),
    )

    mock_subprocess = mocker.patch("subprocess.run", return_value=None)

    main()

    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[os_list][]=ubuntu-latest "
        "-f client_payload[os_list][]=macos-13 "
        "-f client_payload[os_list][]=windows-latest "
        "-f client_payload[python_versions][]=3.11 "
        "-f client_payload[python_versions][]=3.12 "
        "-f client_payload[custom_param]=custom_value"
    )

    actual_cmd = mock_subprocess.call_args[0][0].split()
    expected_cmd_parts = expected_cmd.split()

    with caplog.at_level(logging.INFO):
        assert sorted(actual_cmd) == sorted(expected_cmd_parts)
        logger.info(f"Expected command:\n{format_command(expected_cmd)}")
        logger.info("\n")  # Add a blank line for better readability
        logger.info(f"Actual command:\n{format_command(' '.join(actual_cmd))}")


def test_main_success_2(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test if the correct command is generated when a non-default ghpages_branch is used.

    Args:
        mocker: MockerFixture
        caplog: LogCaptureFixture

    Returns:
        None
    """
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: {
            "REPOSITORY_NAME": "example-repo",
            "EVENT_TYPE": "test_workflow",
            "GHPAGES_BRANCH": "ghpages",  # Non-default value
            "OS_LIST": "ubuntu-latest macos-13 windows-latest",
            "PYTHON_VERSIONS": "3.11 3.12",
            "CUSTOM_PARAM": "custom_value",
        }.get(key),
    )

    mock_subprocess = mocker.patch("subprocess.run", return_value=None)

    main()

    expected_cmd = (
        "gh api repos/example-repo/dispatches -f event_type=test_workflow "
        "-f client_payload[ghpages_branch]=ghpages "
        "-f client_payload[os_list][]=ubuntu-latest "
        "-f client_payload[os_list][]=macos-13 "
        "-f client_payload[os_list][]=windows-latest "
        "-f client_payload[python_versions][]=3.11 "
        "-f client_payload[python_versions][]=3.12 "
        "-f client_payload[custom_param]=custom_value"
    )

    actual_cmd = mock_subprocess.call_args[0][0].split()
    expected_cmd_parts = expected_cmd.split()

    with caplog.at_level(logging.INFO):
        assert sorted(actual_cmd) == sorted(expected_cmd_parts)
        logger.info(f"Expected command:\n{format_command(expected_cmd)}")
        logger.info("\n")  # Add a blank line for better readability
        logger.info(f"Actual command:\n{format_command(' '.join(actual_cmd))}")


def test_main_value_error(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Test if SystemExit is raised when build_payload raises a ValueError.

    Args:
        mocker: MockerFixture
        caplog: LogCaptureFixture

    Returns:
        None
    """
    mocker.patch(
        "os.getenv",
        side_effect=lambda key: {
            "REPOSITORY_NAME": "example-repo",
            "EVENT_TYPE": "test_workflow",
        }.get(key),
    )

    mocker.patch(
        "repo_dispatch_event_sender.src.dispatch.send_payload.build_payload",
        side_effect=ValueError("Invalid payload"),
    )

    with caplog.at_level(logging.ERROR):
        with pytest.raises(SystemExit):  # Expecting SystemExit due to exit(1)
            main()
        logger.error("SystemExit raised due to invalid payload")
