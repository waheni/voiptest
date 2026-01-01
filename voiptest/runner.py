"""Test runner that loads YAML, validates, expands matrix, and executes tests."""

from pathlib import Path
from typing import Any, Dict, List

import yaml

from voiptest.config import VoipTestConfig
from voiptest.engines import sipp


def load_test_config(yaml_path: Path) -> VoipTestConfig:
    """Load and validate a YAML test configuration.

    Args:
        yaml_path: Path to YAML test configuration file

    Returns:
        Validated VoipTestConfig object

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        yaml.YAMLError: If YAML is malformed
        pydantic.ValidationError: If configuration is invalid
    """
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    return VoipTestConfig(**data)


def expand_matrix(config: VoipTestConfig) -> List[VoipTestConfig]:
    """Expand a test configuration with matrix into multiple test cases.

    Args:
        config: Test configuration, possibly with matrix

    Returns:
        List of test configurations (expanded if matrix present, or single item)
    """
    if config.matrix is None:
        return [config]

    expanded = []
    for to_value in config.matrix.to:
        # Create a copy of the config with the new 'to' value
        config_dict = config.model_dump(by_alias=True)
        config_dict["call"]["to"] = to_value
        # Remove matrix from expanded configs
        config_dict.pop("matrix", None)
        # Add suffix to name to differentiate
        config_dict["name"] = f"{config.name} (to={to_value})"

        expanded.append(VoipTestConfig(**config_dict))

    return expanded


def run_single_test(config: VoipTestConfig) -> Dict[str, Any]:
    """Run a single test case using the appropriate engine.

    Args:
        config: Test configuration for a single test case

    Returns:
        Dictionary with test result:
        {
            "name": str,
            "passed": bool,
            "config": dict,
            "actual": dict,
            "error": str (optional)
        }
    """
    try:
        # Currently only SIPp engine is supported
        result = sipp.execute_test(config)
        return result
    except Exception as e:
        return {
            "name": config.name,
            "passed": False,
            "config": config.model_dump(by_alias=True),
            "actual": {},
            "error": str(e),
        }


def run_test_file(yaml_path: Path) -> Dict[str, Any]:
    """Load a YAML test file, expand matrix if present, and run all cases.

    Args:
        yaml_path: Path to YAML test configuration

    Returns:
        Dictionary with aggregated results:
        {
            "name": str,
            "passed": bool,
            "runs": List[Dict]
        }
    """
    # Load and validate configuration
    config = load_test_config(yaml_path)

    # Expand matrix if present
    test_cases = expand_matrix(config)

    # Run all test cases
    runs = []
    all_passed = True

    for test_config in test_cases:
        result = run_single_test(test_config)
        runs.append(result)
        if not result["passed"]:
            all_passed = False

    return {
        "name": config.name,
        "passed": all_passed,
        "runs": runs,
    }
