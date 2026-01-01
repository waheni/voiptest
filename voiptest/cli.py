"""CLI interface for voiptest using Typer."""

from pathlib import Path
from typing import Optional

import typer

from voiptest import runner
from voiptest.report import junit

app = typer.Typer(
    name="voiptest",
    help="VoIP regression smoke tests for CI",
    add_completion=False,
)


def _run_tests(path: Path, junit_output: bool, out: Optional[Path]) -> None:
    """Shared runner used by both the default invocation and the run subcommand."""
    output_dir = out if out else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect test files
    if path.is_file():
        test_files = [path]
    elif path.is_dir():
        test_files = sorted(path.glob("*.yaml")) + sorted(path.glob("*.yml"))
    else:
        typer.echo(f"❌ Path not found: {path}", err=True)
        raise typer.Exit(code=1)

    if not test_files:
        typer.echo(f"❌ No test files found in {path}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Running {len(test_files)} test file(s)...")

    all_results = []
    total_passed = 0
    total_failed = 0

    for test_file in test_files:
        typer.echo(f"\n📋 Running: {test_file.name}")
        try:
            result = runner.run_test_file(test_file)
            all_results.append(result)

            passed = sum(1 for run in result["runs"] if run["passed"])
            failed = len(result["runs"]) - passed
            total_passed += passed
            total_failed += failed

            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            typer.echo(f"   {status} - {passed}/{len(result['runs'])} tests passed")

        except Exception as e:
            typer.echo(f"   ❌ ERROR: {e}", err=True)
            total_failed += 1
            all_results.append({
                "name": test_file.stem,
                "passed": False,
                "runs": [],
                "error": str(e),
            })

    if junit_output:
        junit_file = output_dir / "voiptest-results.xml"
        junit.write_junit_xml(all_results, junit_file)
        typer.echo(f"\n📄 JUnit XML written to: {junit_file}")

    typer.echo("\n" + "=" * 50)
    typer.echo(f"Summary: {total_passed} passed, {total_failed} failed")
    typer.echo("=" * 50)

    if total_failed > 0:
        raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Show help when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=1)


@app.command()
def run(
    path: Path = typer.Argument(
        ...,
        help="Path to YAML test file or directory containing test files",
        exists=False,
    ),
    junit_output: bool = typer.Option(
        False,
        "--junit",
        help="Generate JUnit XML output",
    ),
    out: Optional[Path] = typer.Option(
        None,
        "--out",
        help="Output directory for reports (default: current directory)",
    ),
) -> None:
    """Run VoIP regression tests from YAML configuration."""
    _run_tests(path, junit_output, out)


if __name__ == "__main__":
    app()
