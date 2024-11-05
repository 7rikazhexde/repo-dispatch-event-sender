"""
send_payload.py

This script is responsible for generating and sending a repository_dispatch event
using the GitHub CLI (gh) command. It constructs a payload based on the provided
inputs and triggers a webhook to start specific workflows in a repository.

Functions:
    build_payload(data_dict: Mapping[str, Any]) -> str:
        Constructs the payload command for the gh CLI.
"""

import os
import subprocess
from typing import Any, Dict, List, Mapping, Union

# Supported keys in the payload
SUPPORTED_KEYS = {
    "repository_name",
    "event_type",
    "ghpages_branch",
    "os_list",
    "version_list",
    "custom_param",
}

# Keys that require array handling (in [item1,item2] format)
ARRAY_KEYS = {"os_list", "version_list"}

# Default values to be skipped in the payload if no user-defined values are provided
DEFAULT_VALUES = {"custom_param": "default_value", "ghpages_branch": "gh_pages"}


def parse_array_input(value: str) -> List[str]:
    """
    Parse input string in bracket format [item1,item2,item3].

    Args:
        value (str): Input string in [item1,item2,item3] format (no quotes required)

    Returns:
        List[str]: List of parsed values
    """
    # Remove whitespace and brackets
    cleaned = value.strip().strip("[]")
    if not cleaned:
        return []
    # Split by comma and strip each item
    return [item.strip() for item in cleaned.split(",")]


def build_payload(data_dict: Mapping[str, Any]) -> str:
    """
    Constructs the gh API command to trigger a repository_dispatch event.

    Args:
        data_dict (Mapping[str, Any]): The dictionary containing the payload data.
                                      For array inputs (os_list, version_list),
                                      values should be in [item1,item2] format.

    Returns:
        str: The complete gh API command(repository_dispatch webhook payload) to be executed.

    Note:
        Create a repository dispatch event
        <https://docs.github.com/ja/rest/repos/repos?apiVersion=2022-11-28#create-a-repository-dispatch-event>
    """
    payload_cmd = []
    payload_cmd.append(f"gh api repos/{data_dict['repository_name']}/dispatches")
    payload_cmd.append(f"-f event_type={data_dict['event_type']}")

    for key, value in data_dict.items():
        if key in ARRAY_KEYS:
            items = value if isinstance(value, list) else parse_array_input(str(value))
            for item in items:
                payload_cmd.append(f"-f client_payload[{key}][]={item}")
        elif (
            isinstance(value, str)
            and key != "repository_name"
            and key != "event_type"
            and not (key in DEFAULT_VALUES and value == DEFAULT_VALUES[key])
        ):
            payload_cmd.append(f"-f client_payload[{key}]={value}")

    return " ".join(payload_cmd)


def main() -> None:
    """
    Main function to load environment variables, build the payload, and execute the gh command.
    Values from with: section in actions.yml are passed as environment variables.
    Array values should be specified in [item1,item2] format without quotes.
    """
    env_vars: Dict[str, Union[str, List[str]]] = {}
    for key in SUPPORTED_KEYS:
        env_var_name = key.upper()
        value = os.getenv(env_var_name)

        if value:
            if key in ARRAY_KEYS:
                env_vars[key] = parse_array_input(value)
            elif key in DEFAULT_VALUES and value == DEFAULT_VALUES[key]:
                continue
            else:
                env_vars[key] = value

    try:
        command = build_payload(env_vars)
        print(f"Executing command: {command}")
        subprocess.run(command, shell=True, check=True)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
