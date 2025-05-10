"""
A module implementing an interface for receiving struct messages.
"""

# built-in
from io import BytesIO
import os
from typing import Callable

# third-party
from vcorelib.logging import LoggerMixin

# internal
from runtimepy.codec.protocol import Protocol, ProtocolFactory
from runtimepy.primitives.byte_order import ByteOrder
from runtimepy.primitives.int import UnsignedInt

StructHandler = Callable[[Protocol], None]


class StructReceiver(LoggerMixin):
    """A class for sending and receiving struct messages."""

    id_primitive: UnsignedInt
    byte_order: ByteOrder

    def __init__(self, *factories: type[ProtocolFactory]) -> None:
        """Initialize this instance."""

        super().__init__()

        self.handlers: dict[int, StructHandler] = {}
        self.instances: dict[int, Protocol] = {}
        for factory in factories:
            self.register(factory)

    def add_handler(self, identifier: int, handler: StructHandler) -> None:
        """Add a struct message handler."""

        assert identifier not in self.handlers
        self.handlers[identifier] = handler

    def register(self, factory: type[ProtocolFactory]) -> None:
        """Track a protocol factory's structure by identifier."""

        inst = factory.singleton()

        if not hasattr(self, "id_primitive"):
            self.id_primitive = inst.id_primitive.copy()  # type: ignore
            self.byte_order = inst.byte_order
        else:
            assert self.id_primitive.kind == inst.id_primitive.kind
            assert self.byte_order == inst.byte_order

        assert inst.id not in self.instances
        self.instances[inst.id] = inst

    def process(self, data: bytes) -> None:
        """Attempt to process a struct message."""

        with BytesIO(data) as stream:
            stream.seek(0, os.SEEK_END)
            end_pos = stream.tell()
            stream.seek(0, os.SEEK_SET)

            while stream.tell() < end_pos:
                ident = self.id_primitive.from_stream(
                    stream, byte_order=self.byte_order
                )
                if ident in self.instances:
                    inst = self.instances[ident]
                    inst.from_stream(stream)
                    if ident in self.handlers:
                        self.handlers[ident](inst)
                    else:
                        self.logger.warning(
                            "No message handler for struct '%d' (%s).",
                            ident,
                            inst,
                        )

                # Can't continue reading if we don't know this identifier.
                else:
                    self.logger.error(
                        "Unknown struct identifier '%d' "
                        "@%d/%d of stream (aborting).",
                        ident,
                        stream.tell(),
                        end_pos,
                    )
                    stream.seek(0, os.SEEK_END)
