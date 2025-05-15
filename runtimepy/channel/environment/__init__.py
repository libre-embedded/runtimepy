"""
A module implementing a channel environment.
"""

# built-in
from contextlib import ExitStack as _ExitStack
from typing import Iterator as _Iterator
from typing import cast as _cast

# internal
from runtimepy.channel import Default as _Default
from runtimepy.channel.environment.array import (
    ArrayChannelEnvironment as _ArrayChannelEnvironment,
)
from runtimepy.channel.environment.create import (
    CreateChannelEnvironment as _CreateChannelEnvironment,
)
from runtimepy.channel.environment.file import (
    FileChannelEnvironment as _FileChannelEnvironment,
)
from runtimepy.channel.environment.telemetry import (
    TelemetryChannelEnvironment as _TelemetryChannelEnvironment,
)
from runtimepy.codec.protocol import Protocol as _Protocol
from runtimepy.codec.protocol.base import FieldSpec as _FieldSpec


class ChannelEnvironment(
    _TelemetryChannelEnvironment,
    _ArrayChannelEnvironment,
    _FileChannelEnvironment,
    _CreateChannelEnvironment,
):
    """A class integrating channel and enumeration registries."""

    def register_protocol(self, protocol: _Protocol) -> None:
        """Register protocol elements as named channels and fields."""

        # Register any new enumerations.
        self.enums.register_from_other(protocol.enum_registry)

        for item in protocol.build:
            # Handle regular primitive fields.
            if isinstance(item, _FieldSpec):
                if item.is_array():
                    assert item.array_length is not None
                    with self.names_pushed(item.name):
                        for idx in range(item.array_length):
                            self.channel(
                                str(idx),
                                kind=protocol.get_primitive(
                                    item.name, index=idx
                                ),
                                commandable=item.commandable,
                                enum=item.enum,
                            )
                else:
                    self.channel(
                        item.name,
                        kind=protocol.get_primitive(item.name),
                        commandable=item.commandable,
                        enum=item.enum,
                    )

            # Handle nested protocols.
            elif isinstance(item[0], str):
                name = item[0]
                candidates = protocol.serializables[name]
                if isinstance(candidates[0], _Protocol):
                    with self.names_pushed(name):
                        for idx, candidate in enumerate(candidates):
                            with _ExitStack() as stack:
                                # Enter array-index namespace if applicable.
                                if len(candidates) > 1:
                                    stack.enter_context(
                                        self.names_pushed(str(idx))
                                    )

                                self.register_protocol(
                                    _cast(_Protocol, candidate)
                                )

            # Handle bit fields.
            elif isinstance(item[0], int):
                self.add_fields(item[1], protocol.get_fields(item[0]))

    def search_names(
        self, pattern: str, exact: bool = False
    ) -> _Iterator[str]:
        """Search for names belonging to this environment."""
        yield from self.channels.names.search(pattern, exact=exact)

    def set_default(self, key: str, default: _Default) -> None:
        """Set a new default value for a channel."""

        chan, _ = self[key]
        chan.default = default

    @property
    def num_defaults(self) -> int:
        """
        Determine the number of channels in this environment configured with
        a default value.
        """

        result = 0

        for name in self.names:
            chan = self.get(name)
            if chan is not None and chan[0].has_default:
                result += 1

        return result
