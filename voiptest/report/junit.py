"""JUnit XML report generation for CI integration."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List


def write_junit_xml(results: List[Dict[str, Any]], output_path: Path) -> None:
    """Generate JUnit XML report from test results.

    Args:
        results: List of test file results, each containing:
                 {name, passed, runs:[{name, passed, ...}]}
        output_path: Path where XML file should be written
    """
    # Calculate totals
    total_tests = sum(len(r.get("runs", [])) for r in results)
    total_failures = sum(
        sum(1 for run in r.get("runs", []) if not run.get("passed", False))
        for r in results
    )
    total_errors = sum(1 for r in results if "error" in r)

    # Create root testsuites element
    testsuites = ET.Element("testsuites")
    testsuites.set("tests", str(total_tests))
    testsuites.set("failures", str(total_failures))
    testsuites.set("errors", str(total_errors))

    # Create a testsuite for each test file
    for result in results:
        testsuite = ET.SubElement(testsuites, "testsuite")
        testsuite.set("name", result["name"])

        runs = result.get("runs", [])
        testsuite.set("tests", str(len(runs)))

        failures = sum(1 for run in runs if not run.get("passed", False))
        testsuite.set("failures", str(failures))

        # Handle file-level errors
        if "error" in result:
            testsuite.set("errors", "1")
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", result["name"])
            testcase.set("classname", "voiptest")

            error = ET.SubElement(testcase, "error")
            error.set("message", "Test file error")
            error.text = result["error"]
            continue

        testsuite.set("errors", "0")

        # Add testcase for each run
        for run in runs:
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", run.get("name", "unknown"))
            testcase.set("classname", result["name"])

            # Add duration if available
            if "duration_s" in run:
                testcase.set("time", str(run["duration_s"]))

            # Add failure or error information
            if not run.get("passed", False):
                if "error" in run:
                    error = ET.SubElement(testcase, "error")
                    error.set("message", "Test execution error")
                    error.text = run["error"]
                else:
                    failure = ET.SubElement(testcase, "failure")
                    failure.set("message", "Test assertion failed")

                    # Include expected vs actual in failure message
                    failure_text = []
                    if "config" in run and "expect" in run["config"]:
                        failure_text.append(f"Expected: {run['config']['expect']}")
                    if "actual" in run:
                        failure_text.append(f"Actual: {run['actual']}")

                    failure.text = "\n".join(failure_text)

            # Add stdout with test details
            stdout = ET.SubElement(testcase, "system-out")
            stdout_lines = [
                f"Test: {run.get('name', 'unknown')}",
            ]
            if "config" in run:
                stdout_lines.append(f"Config: {run['config']}")
            if "actual" in run:
                stdout_lines.append(f"Actual: {run['actual']}")
            stdout.text = "\n".join(stdout_lines)

    # Write XML to file
    tree = ET.ElementTree(testsuites)
    ET.indent(tree, space="  ")  # Pretty print (Python 3.9+)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
