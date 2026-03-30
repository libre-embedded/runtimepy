"""
A module implementing a binary data connection for the package's WebSocket
server interface.
"""

# built-in
import asyncio
from json import loads

# internal
from runtimepy.net.stream.string import StringMessageConnection
from runtimepy.net.websocket import WebsocketConnection

DATA_CONNECTIONS: dict[
    str, asyncio.Future["RuntimepyDataWebsocketConnection"]
] = {}


def data_connection_future(
    guid: str,
) -> asyncio.Future["RuntimepyDataWebsocketConnection"]:
    """Get a future for a data connection guid."""

    if guid not in DATA_CONNECTIONS:
        DATA_CONNECTIONS[guid] = asyncio.get_running_loop().create_future()
    return DATA_CONNECTIONS[guid]


class RuntimepyDataWebsocketConnection(
    StringMessageConnection, WebsocketConnection
):
    """A class implementing a WebSocket connection for streaming raw data."""

    async def process_message(
        self, data: str, addr: tuple[str, int] = None
    ) -> bool:
        """Process a string message."""

        del addr

        message = loads(data)

        if "ui" in message and "guid" in message["ui"]:
            data_connection_future(message["ui"]["guid"]).set_result(self)

        else:
            self.logger.info(message)

        return True
