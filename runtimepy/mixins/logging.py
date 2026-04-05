"""
A module implementing a logger-mixin extension.
"""

# built-in
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
import io
import logging
from typing import Any, AsyncIterator, Iterable, Optional

# third-party
import aiofiles
from vcorelib.logging import ListLogger, LoggerMixin, LoggerType
from vcorelib.paths import Pathlike, normalize

# internal
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.enum.registry import RuntimeIntEnum


class LogLevel(RuntimeIntEnum):
    """A runtime enumeration for log level."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def id(cls) -> Optional[int]:
        """Override in sub-class to coerce enum id."""
        return 2


LogLevellike = LogLevel | int | str


class LoggerMixinLevelControl(LoggerMixin):
    """A logger mixin that exposes a runtime-controllable level."""

    def _log_level_changed(self, _: int, new_value: int) -> None:
        """Handle a change in log level."""

        self.logger.setLevel(new_value)
        self.logger.log(new_value, "Log level updated to %d.", new_value)

    def setup_level_channel(
        self,
        env: ChannelEnvironment,
        name: str = "log_level",
        initial: str = "info",
        description: str = "Text-log level filter for this environment.",
    ) -> None:
        """Add a commandable log-level channel to the environment."""

        chan = env.int_channel(
            name,
            enum=LogLevel.register_enum(env.enums),
            commandable=True,
            description=description,
        )

        # Set up change handler.
        chan[0].raw.register_callback(self._log_level_changed)

        # Set the initial log level.
        env.set(name, initial)

        del chan


LogPaths = Iterable[tuple[LogLevellike, Pathlike]]
EXT_LOG_EXTRA = {"external": True}


def handle_safe_log(
    logger: LoggerType, level: int, data: str, safe_to_log: bool
) -> None:
    """handle a log filtering scenario."""

    if safe_to_log:
        logger.log(level, data, extra=EXT_LOG_EXTRA)
    else:
        record = logging.LogRecord(
            logger.name, level, __file__, -1, data, (), None
        )
        record.external = True

        for handler in logger.handlers:  # type: ignore
            if isinstance(handler, ListLogger):
                handler.emit(record)


class FileWatcher:
    """A class implementing an interface for watching file contents."""

    def __init__(self, level: LogLevellike, path: Pathlike) -> None:
        """Initialize this instance."""

        self.level = LogLevel.normalize(level)
        self.path = path
        self.stream: Optional[Any] = None
        self.ctime: int = 0

    async def get_ctime(self) -> int:
        """Get ctime for this path."""

        return round(  # type: ignore
            await aiofiles.os.path.getctime(self.path),
        )

    async def handle_open(self) -> None:
        """Handle opening the stream."""

        if not self.stream and normalize(self.path).is_file():
            self.stream = await aiofiles.open(self.path, mode="r")
            await self.stream.seek(0, io.SEEK_END)
            self.ctime = await self.get_ctime()

    async def poll(self) -> AsyncIterator[tuple[LogLevel, str]]:
        """Poll stream contents."""

        try:
            # Handle re-opening file if necessary.
            if self.ctime != await self.get_ctime():
                await self.close()

            await self.handle_open()
            if self.stream:
                while line := (await self.stream.readline()).rstrip():
                    yield self.level, line.rstrip()

        except FileNotFoundError:
            await self.close()

    async def close(self) -> None:
        """Close this stream."""

        if self.stream:
            await self.stream.close()
        self.stream = None

    @asynccontextmanager
    @staticmethod
    async def running(
        level: LogLevellike, path: Pathlike
    ) -> AsyncIterator["FileWatcher"]:
        """Handle closing stream."""

        inst = FileWatcher(level, path)
        await inst.handle_open()
        try:
            yield inst
        finally:
            await inst.close()


class LogCaptureMixin:
    """A simple async file-reading interface."""

    logger: LoggerType

    watchers: list[FileWatcher]

    # Set false to only forward to ListLogger handlers. Required for when the
    # system log / process-management logs are being forwarded (otherwise also
    # logging would lead to infinite spam).
    safe_to_log = True

    async def init_log_capture(
        self, stack: AsyncExitStack, log_paths: LogPaths
    ) -> None:
        """Initialize this task with application information."""

        self.watchers = [
            await stack.enter_async_context(FileWatcher.running(level, path))
            for level, path in log_paths
        ]

    def log_line(self, level: int, data: str) -> None:
        """Log a line for output."""

        handle_safe_log(self.logger, level, data, self.safe_to_log)

    async def handle_watcher(self, watcher: FileWatcher) -> None:
        """Handle any file watcher lines."""

        async for level, line in watcher.poll():
            self.log_line(level, line)

    async def dispatch_log_capture(self) -> None:
        """Get the next line from this log stream."""

        await asyncio.gather(*(self.handle_watcher(x) for x in self.watchers))
