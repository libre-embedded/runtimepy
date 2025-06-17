"""
A module implementing a DatagramProtocol for UdpConnection.
"""

# built-in
import asyncio as _asyncio
from asyncio import DatagramProtocol as _DatagramProtocol
import logging

# third-party
from vcorelib.io import BinaryMessage
from vcorelib.logging import LoggerMixin, LoggerType
from vcorelib.math import RateLimiter

# internal
from runtimepy.net.connection import Connection as _Connection


class UdpQueueProtocol(_DatagramProtocol):
    """A simple UDP protocol that populates a message queue."""

    logger: LoggerType
    conn: _Connection

    def __init__(self) -> None:
        """Initialize this protocol."""

        self.queue: _asyncio.Queue[tuple[BinaryMessage, tuple[str, int]]] = (
            _asyncio.Queue()
        )

        self.log_limiter = RateLimiter.from_s(1.0)

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Handle incoming data."""
        self.queue.put_nowait((data, addr))

    def error_received(self, exc: Exception) -> None:
        """Log any received errors."""

        LoggerMixin.governed_log(
            self,  # type: ignore
            self.log_limiter,
            "Exception occurred:",
            level=logging.ERROR,
            exc_info=exc,
        )

        # Most of the time this error occurs when sending to a loopback
        # destination (localhost) that is no longer listening.
        self.conn.disable(str(exc))
