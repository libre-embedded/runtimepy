"""
A module implementing a channel environment.
"""

# built-in
from contextlib import ExitStack as _ExitStack
from typing import Iterator as _Iterator
from typing import Optional
from typing import cast as _cast

# internal
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
from runtimepy.primitives import AnyPrimitive
from runtimepy.ui.controls import Controls, Default, bit_slider


def regular_channel_controls(
    primitive: AnyPrimitive, commandable: bool
) -> Optional[Controls]:
    """Get channel controls for a regular primitive."""

    controls = None

    if commandable and primitive.kind.is_integer and primitive.kind.bits <= 32:
        controls = bit_slider(primitive.kind.bits, primitive.kind.signed)

    return controls


class ChannelEnvironment(
    _TelemetryChannelEnvironment,
    _ArrayChannelEnvironment,
    _FileChannelEnvironment,
    _CreateChannelEnvironment,
):
    """A class integrating channel and enumeration registries."""

    def register_protocol(
        self, protocol: _Protocol, commandable: bool
    ) -> None:
        """Register protocol elements as named channels and fields."""

        # Register any new enumerations.
        self.enums.register_from_other(protocol.enum_registry)

        # need to handle defaults

        for item in protocol.build:
            # Handle regular primitive fields.
            if isinstance(item, _FieldSpec):
                if item.is_array():
                    assert item.array_length is not None
                    with self.names_pushed(item.name):
                        for idx in range(item.array_length):
                            primitive = protocol.get_primitive(
                                item.name, index=idx
                            )
                            self.channel(
                                str(idx),
                                kind=primitive,
                                commandable=commandable,
                                enum=item.enum,
                                controls=regular_channel_controls(
                                    primitive, commandable
                                ),
                            )
                else:
                    primitive = protocol.get_primitive(item.name)
                    self.channel(
                        item.name,
                        kind=primitive,
                        commandable=commandable,
                        enum=item.enum,
                        controls=regular_channel_controls(
                            primitive, commandable
                        ),
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
                                    _cast(_Protocol, candidate), commandable
                                )

            # Handle bit fields.
            elif isinstance(item[0], int):
                fields = protocol.get_fields(item[0])
                for field in fields.fields.values():
                    field.commandable = commandable
                    # add sliders for non enum non bool (check enum fields too)
                self.add_fields(
                    item[1],
                    fields,
                    commandable=commandable,
                    controls=bit_slider(fields.raw.kind.bits, False),
                )

    def search_names(
        self, pattern: str, exact: bool = False
    ) -> _Iterator[str]:
        """Search for names belonging to this environment."""
        yield from self.channels.names.search(pattern, exact=exact)

    def set_default(self, key: str, default: Default) -> None:
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
