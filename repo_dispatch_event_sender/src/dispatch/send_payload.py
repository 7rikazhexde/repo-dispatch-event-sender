"""
send_payload.py

This script is responsible for generating and sending a repository_dispatch event
using the GitHub CLI (gh) command. It constructs a payload based on the provided
inputs and triggers a webhook to start specific workflows in a repository.

Functions:
    build_payload(data_dict: Mapping[str, Union[str, List[str]]]) -> str:
        Constructs the payload command for the gh CLI.
"""

import os
import subprocess
from typing import Dict, List, Mapping, Union

# Supported keys in the payload
SUPPORTED_KEYS = {
    "repository_name",
    "event_type",
    "ghpages_branch",
    "os_list",
    "python_versions",
    "custom_param",
}

# Keys that require space-separated values to be split into lists
SPLIT_REQUIRED_KEYS = {"os_list", "python_versions"}

# Default values to be skipped in the payload if no user-defined values are provided
DEFAULT_VALUES = {"custom_param": "default_value", "ghpages_branch": "gh_pages"}


def build_payload(data_dict: Mapping[str, Union[str, List[str]]]) -> str:
    """
    Constructs the gh API command to trigger a repository_dispatch event.

    Args:
        data_dict (Mapping[str, Union[str, List[str]]]): The dictionary containing the payload data.

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
        if isinstance(value, list):
            for item in value:
                payload_cmd.append(f"-f client_payload[{key}][]={item}")
        # If the variable is not specified in client_payload, it should be explicitly excluded below.
        elif (
            isinstance(value, str) and key != "repository_name" and key != "event_type"
        ):
            payload_cmd.append(f"-f client_payload[{key}]={value}")

    return " ".join(payload_cmd)


def main() -> None:
    """
    Main function to load environment variables, build the payload, and execute the gh command.
    """
    env_vars: Dict[str, Union[str, List[str]]] = {}
    for key in SUPPORTED_KEYS:
        env_var_name = key.upper()
        value = os.getenv(env_var_name)

        if value:
            if key in SPLIT_REQUIRED_KEYS:
                env_vars[key] = value.split()
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
