"""
A module implementing a stateful data interface for per-connection tabs.
"""

# built-in
from collections import defaultdict
from dataclasses import dataclass
import logging
from typing import Optional

# third-party
from vcorelib.io import ByteFifo
from vcorelib.logging import ListLogger

# internal
from runtimepy.channel.environment.base import ValueMap
from runtimepy.message import JsonMessage
from runtimepy.net.server.websocket.data import (
    RuntimepyDataWebsocketConnection,
)
from runtimepy.primitives import AnyPrimitive

# (value, nanosecond timestamp)
Point = tuple[str | int | float | bool, int]


@dataclass
class TabState:
    """Stateful information relevant to individual tabs."""

    shown: bool
    tab_logger: ListLogger

    points: dict[str, list[Point]]
    primitives: dict[str, AnyPrimitive]
    callbacks: dict[str, int]

    latest_ui_values: ValueMap

    _loggers: list[logging.Logger]

    binary: ByteFifo

    def frame(
        self,
        time: float,
        data_connection: Optional[RuntimepyDataWebsocketConnection] = None,
    ) -> JsonMessage:
        """Handle a new UI frame."""

        # Not used yet.
        del time

        result: JsonMessage = {}

        # Handle log messages.
        if self.tab_logger:
            result["log_messages"] = self.tab_logger.drain_str()

        # Handle channel updates.
        if self.points:
            result["points"] = self.points
            self.points = defaultdict(list)

        # Forward binary data.
        msg = self.binary.pop(self.binary.size)
        if msg and data_connection is not None:
            data_connection.send_message(msg)

        return result

    def clear_telemetry(self) -> None:
        """Clear all telemetry interactions."""

        # Remove callbacks for primitives.
        for name, val in self.callbacks.items():
            self.primitives[name].remove_callback(val)
        self.callbacks.clear()
        self.primitives.clear()

        # Clear points.
        self.points.clear()
        self.binary.pop(self.binary.size)

    def clear_loggers(self) -> None:
        """Clear all logging handlers."""

        # Remove handlers.
        for logger in self._loggers:
            logger.removeHandler(self.tab_logger)
        self._loggers.clear()

        self.tab_logger.drain_str()

        self.clear_telemetry()

    def add_logger(self, logger: logging.Logger) -> None:
        """Add a logger."""

        if logger not in self._loggers:
            logger.addHandler(self.tab_logger)
            self._loggers.append(logger)

    @staticmethod
    def create() -> "TabState":
        """Create a new instance."""

        return TabState(
            False,
            ListLogger.create(),
            defaultdict(list),
            {},
            {},
            {},
            [],
            ByteFifo(),
        )
