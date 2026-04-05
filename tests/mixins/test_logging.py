"""
Test the 'mixins.logging' module.
"""

# built-in
import asyncio
from contextlib import AsyncExitStack
import logging

# third-party
from pytest import mark
from vcorelib.logging import ListLogger, LoggerMixin
from vcorelib.paths.context import tempfile

# module under test
from runtimepy.mixins.logging import LogCaptureMixin, handle_safe_log


class SampleLogger(LoggerMixin, LogCaptureMixin):
    """A sample class."""


def test_handle_safe_log_basic():
    """Test basic scenarios for the 'handle_safe_log' method."""

    logger = logging.getLogger(__name__)
    logger.addHandler(ListLogger.create())

    handle_safe_log(logger, logging.INFO, "message", True)
    handle_safe_log(logger, logging.INFO, "message", False)


@mark.asyncio
async def test_log_capture_mixin_basic():
    """Test basic interactions with a log capture."""

    inst = SampleLogger()

    async with AsyncExitStack() as stack:
        path = stack.enter_context(tempfile())
        await inst.init_log_capture(stack, [("info", path)])

        for idx in range(5):
            with path.open("w") as writer:
                await inst.dispatch_log_capture()

                for _ in range(10):
                    writer.write(f"Hello, world! ({idx}.1)\n")
                    writer.flush()
                    await inst.dispatch_log_capture()

                await inst.dispatch_log_capture()

            await asyncio.sleep(0.1)
            path.unlink()
            await inst.dispatch_log_capture()
            await inst.dispatch_log_capture()

            with path.open("w") as writer:
                await inst.dispatch_log_capture()

                for _ in range(10):
                    writer.write(f"Hello, world! ({idx}.2)\n")
                    writer.flush()
                    await inst.dispatch_log_capture()
