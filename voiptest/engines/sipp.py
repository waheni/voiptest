"""SIPp engine for executing VoIP test scenarios.

This module provides the interface to SIPp (SIP test tool) for executing
VoIP regression tests.
"""

import csv
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

from voiptest.config import VoipTestConfig

# Get the directory where this module lives
ENGINE_DIR = Path(__file__).parent
SCENARIO_DIR = ENGINE_DIR / "sipp_scenarios"


def execute_test(config: VoipTestConfig) -> Dict[str, Any]:
    """Execute a VoIP test using SIPp.

    Args:
        config: Validated test configuration

    Returns:
        Dictionary with test results:
        {
            "name": str,
            "passed": bool,
            "config": dict,  # Original config
            "actual": dict,  # Actual outcomes
            "duration_s": float,
            "error": str (optional)
        }
    """
    start_time = time.time()

    try:
        # Validate SIPp is available
        if not validate_sipp_installed():
            return {
                "name": config.name,
                "passed": False,
                "config": config.model_dump(by_alias=True),
                "actual": {},
                "duration_s": 0.0,
                "error": "SIPp not found in PATH. Please install SIPp.",
            }

        # Run SIPp and get raw results
        sipp_result = run_sipp(config)

        # Extract actual outcome from SIPp results
        actual = {
            "outcome": determine_outcome(sipp_result, config),
            "sip_code": sipp_result.get("final_code"),
            "answer_time_s": None,  # Could parse from trace if needed
            "duration_s": time.time() - start_time,
        }

        # Compare actual vs expected
        passed = check_expectations(config, actual, sipp_result)

        result = {
            "name": config.name,
            "passed": passed,
            "config": config.model_dump(by_alias=True),
            "actual": actual,
            "duration_s": time.time() - start_time,
        }

        # Include error if present
        if "reason" in sipp_result and not passed:
            result["error"] = sipp_result["reason"]

        # Include logs for debugging
        if "logs" in sipp_result:
            result["logs"] = sipp_result["logs"]

        return result

    except Exception as e:
        return {
            "name": config.name,
            "passed": False,
            "config": config.model_dump(by_alias=True),
            "actual": {},
            "duration_s": time.time() - start_time,
            "error": f"Exception during test execution: {str(e)}",
        }


def run_sipp(config: VoipTestConfig) -> Dict[str, Any]:
    """Run SIPp subprocess and return raw results.

    Args:
        config: Test configuration

    Returns:
        Dictionary with:
        {
            "final_code": int | None,
            "reason": str,
            "logs": {
                "stdout": str,
                "stderr": str,
                "message_log": str,
                "error_log": str,
                "temp_dir": str
            },
            "exit_code": int
        }
    """
    # Create temp directory for this run
    temp_dir = tempfile.mkdtemp(prefix="voiptest_sipp_")
    temp_path = Path(temp_dir)

    try:
        # Generate CSV injection file
        csv_file = temp_path / "inject.csv"
        generate_csv_file(csv_file, config)

        # Prepare SIPp command
        scenario_file = SCENARIO_DIR / "uac_basic.xml"
        if not scenario_file.exists():
            return {
                "final_code": None,
                "reason": f"Scenario file not found: {scenario_file}",
                "logs": {"temp_dir": temp_dir},
                "exit_code": -1,
            }

        # Extract domain from config
        domain = config.target.domain or config.target.host

        # Build SIPp command
        cmd = [
            "sipp",
            config.target.host,
            "-i", "127.0.0.1",  # Local IP (use IPv4 to match localhost resolution)
            "-p", "5070",  # Local port (avoid conflict with target)
            "-sf", str(scenario_file),
            "-inf", str(csv_file),
            "-m", "1",  # Max calls
            "-l", "1",  # Call rate limit
            "-r", "1",  # Call rate
            "-timeout", str(config.call.timeout_s),
            "-timeout_error",
            "-trace_msg",
            "-trace_err",
            "-nd",  # No default behavior on unexpected messages
        ]

        # Add transport
        if config.target.transport.lower() == "tcp":
            cmd.append("-t")
            cmd.append("t1")
        elif config.target.transport.lower() == "tls":
            cmd.append("-t")
            cmd.append("l1")

        # Add remote port
        cmd.extend(["-rsa", f"{config.target.host}:{config.target.port}"])

        # Set auth if provided
        if config.accounts.caller.username and config.accounts.caller.password:
            cmd.extend(["-au", config.accounts.caller.username])
            cmd.extend(["-ap", config.accounts.caller.password])

        # Set message log file
        msg_log = temp_path / "messages.log"
        err_log = temp_path / "errors.log"
        cmd.extend(["-message_file", str(msg_log)])
        cmd.extend(["-error_file", str(err_log)])

        # Run SIPp
        result = subprocess.run(
            cmd,
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=config.call.timeout_s + 10,  # Add buffer
        )

        # Read logs
        stdout = result.stdout
        stderr = result.stderr
        message_log = msg_log.read_text() if msg_log.exists() else ""
        error_log = err_log.read_text() if err_log.exists() else ""

        # Extract final SIP code from message log
        final_code = extract_final_sip_code(message_log)

        # Determine reason
        reason = "success"
        if result.returncode != 0:
            if "timeout" in stderr.lower() or "timeout" in error_log.lower():
                reason = "timeout"
            elif final_code and final_code >= 400:
                reason = f"SIP error {final_code}"
            else:
                reason = f"SIPp exit code {result.returncode}"

        return {
            "final_code": final_code,
            "reason": reason,
            "logs": {
                "stdout": stdout,
                "stderr": stderr,
                "message_log": message_log,
                "error_log": error_log,
                "temp_dir": temp_dir,
            },
            "exit_code": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "final_code": None,
            "reason": "SIPp process timeout",
            "logs": {"temp_dir": temp_dir},
            "exit_code": -1,
        }
    except Exception as e:
        return {
            "final_code": None,
            "reason": f"SIPp execution error: {str(e)}",
            "logs": {"temp_dir": temp_dir},
            "exit_code": -1,
        }


def resolve_destination(config: VoipTestConfig, dest_key: str) -> str:
    """Resolve a destination (account key or literal) to a username.
    
    Args:
        config: Test configuration
        dest_key: Either an account key (e.g., "callee") or a literal (e.g., "2000")
    
    Returns:
        Username/extension to use as destination
    """
    # Get all account names from the accounts object
    accounts_data = config.accounts.model_dump()
    
    # Check if dest_key is an account key
    if dest_key in accounts_data:
        account = getattr(config.accounts, dest_key, None)
        if account and hasattr(account, 'username'):
            return account.username
    
    # It's a literal destination (e.g., "2000" or a phone number)
    return dest_key


def generate_csv_file(csv_path: Path, config: VoipTestConfig) -> None:
    """Generate CSV injection file for SIPp.

    Format:
    First line: SEQUENTIAL
    Second line: to;from_user;domain;password
    """
    # Resolve caller and destination
    from_account = config.accounts.caller
    from_user = from_account.username
    
    # Resolve 'to' - can be account key or literal
    to_user = resolve_destination(config, config.call.to)
    
    domain = config.target.domain or config.target.host
    password = from_account.password or ""

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        # First line must be SEQUENTIAL, RANDOM, or USER
        f.write("SEQUENTIAL\n")
        # Write data row (no header for field names)
        writer.writerow([to_user, from_user, domain, password])


def extract_final_sip_code(message_log: str) -> Optional[int]:
    """Extract final SIP response code from message log.

    Scans for lines like "SIP/2.0 200 OK", ignoring 100 Trying.
    Returns the last response code >= 200.

    Args:
        message_log: SIPp message log content

    Returns:
        Final SIP response code or None
    """
    final_code = None

    # Pattern to match SIP responses: "SIP/2.0 <code> <reason>"
    pattern = r"SIP/2\.0\s+(\d{3})\s+"

    for match in re.finditer(pattern, message_log):
        code = int(match.group(1))
        # Ignore provisional responses (100-199)
        if code >= 200:
            final_code = code

    return final_code


def determine_outcome(sipp_result: Dict[str, Any], config: VoipTestConfig) -> str:
    """Determine call outcome from SIPp results.

    Args:
        sipp_result: Raw SIPp execution results
        config: Test configuration

    Returns:
        Outcome string: "answered", "failed", "busy", "no_answer"
    """
    exit_code = sipp_result.get("exit_code", -1)
    final_code = sipp_result.get("final_code")
    reason = sipp_result.get("reason", "")

    # Check for timeout/no_answer
    if "timeout" in reason.lower():
        return "no_answer"

    # Check SIP response code
    if final_code:
        if 200 <= final_code < 300:
            return "answered"
        elif final_code == 486:  # Busy Here
            return "busy"
        elif 400 <= final_code < 700:
            return "failed"

    # Check exit code
    if exit_code == 0:
        return "answered"

    return "failed"


def check_expectations(
    config: VoipTestConfig, actual: Dict[str, Any], sipp_result: Dict[str, Any]
) -> bool:
    """Check if actual results match expected outcomes.

    Args:
        config: Test configuration with expectations
        actual: Actual outcomes
        sipp_result: Raw SIPp results

    Returns:
        True if expectations are met, False otherwise
    """
    expect = config.expect
    final_code = actual["sip_code"]
    actual_outcome = actual["outcome"]

    # Outcome-based expectations
    if expect.outcome == "answered":
        # Must receive 200 OK
        if actual_outcome != "answered" or final_code != 200:
            return False
    elif expect.outcome == "busy":
        # Must receive 486 Busy or similar
        if actual_outcome != "busy" or final_code != 486:
            return False
    elif expect.outcome == "failed":
        # Must NOT be success/answered, and must be a failure
        if actual_outcome == "answered":
            return False
        # If final_sip_code is specified, enforce it
        if expect.final_sip_code is not None and final_code != expect.final_sip_code:
            return False
    elif expect.outcome == "no_answer":
        # Timeout or no response
        if actual_outcome not in ("no_answer", "failed"):
            return False

    # Check final SIP code if specified (overrides outcome logic for verification)
    if expect.final_sip_code is not None:
        if final_code != expect.final_sip_code:
            return False

    # Additional checks could be added for answer_within_s, min_duration_s
    # These would require parsing timing information from SIPp logs

    return True


def validate_sipp_installed() -> bool:
    """Check if SIPp is installed and available.

    Returns:
        True if SIPp is available, False otherwise
    """
    return shutil.which("sipp") is not None


def get_sipp_version() -> str:
    """Get installed SIPp version.

    Returns:
        SIPp version string or "unknown"
    """
    try:
        result = subprocess.run(
            ["sipp", "-v"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Parse version from output
        output = result.stdout + result.stderr
        version_match = re.search(r"SIPp\s+v?([\d.]+)", output, re.IGNORECASE)
        if version_match:
            return version_match.group(1)
    except Exception:
        pass

    return "unknown"
