"""
Test the 'commands.arbiter' module.
"""

# built-in
from platform import system

# third-party
from pytest import mark
from vcorelib.platform import is_windows

# module under test
from runtimepy.entry import main as runtimepy_main

# internal
from tests.resources import base_args, resource

TIMEOUT = 180


def run_main(entry: str) -> int:
    """Run a test scenario."""

    base = base_args("arbiter")
    return runtimepy_main(
        base + [str(resource("connection_arbiter", f"{entry}.yaml"))]
    )


def test_arbiter_command_init_only():
    """Test basic usages of the 'arbiter' command."""

    assert (
        runtimepy_main(
            base_args("arbiter")
            + ["-w", "--init_only", str(resource("empty.yaml"))]
        )
        == 0
    )


@mark.timeout(TIMEOUT * 2)
def test_arbiter_command_basic():
    """Test basic usages of the 'arbiter' command."""

    # https://github.com/libre-embedded/runtimepy/issues/343
    if system() != "Darwin":
        assert run_main("basic") == 0


@mark.timeout(TIMEOUT)
def test_arbiter_command_http():
    """Test basic usages of the 'arbiter' command."""
    assert run_main("http") == 0


@mark.timeout(TIMEOUT)
def test_arbiter_command_control():
    """Test basic usages of the 'arbiter' command."""
    assert run_main("control") == 0


@mark.timeout(TIMEOUT)
def test_arbiter_command_tftp():
    """Test basic usages of the 'arbiter' command."""
    assert run_main("tftp") == 0


@mark.timeout(TIMEOUT)
def test_arbiter_command_basic_telemetry():
    """Test basic usages of the 'arbiter' command."""
    assert run_main("basic_telemetry") == 0


@mark.timeout(TIMEOUT)
def test_arbiter_command_advanced():
    """Test advanced usages of the 'arbiter' command."""

    base = base_args("arbiter")

    # Run with dummy load.
    for entry in ["runtimepy_http"]:
        args = base + [str(resource("connection_arbiter", f"{entry}.yaml"))]
        if not is_windows():
            args.append("dummy_load")
            args.append("browser")

        assert runtimepy_main(args) == 0
