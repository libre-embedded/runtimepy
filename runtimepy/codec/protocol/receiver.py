"""
A module implementing an interface for receiving struct messages.
"""

# built-in
from io import BytesIO
import os
from typing import Callable, Optional

# third-party
from vcorelib.logging import LoggerMixin

# internal
from runtimepy.codec.protocol import Protocol, ProtocolFactory
from runtimepy.primitives.byte_order import ByteOrder
from runtimepy.primitives.int import UnsignedInt

StructHandler = Callable[[Protocol], None]
NonStructHandler = Callable[[BytesIO], bool]

NON_STRUCT_ID = 0


class StructReceiver(LoggerMixin):
    """A class for sending and receiving struct messages."""

    non_struct_message_prefix: bytes
    id_primitive: UnsignedInt
    byte_order: ByteOrder

    def __init__(self, *factories: type[ProtocolFactory]) -> None:
        """Initialize this instance."""

        super().__init__()

        self.non_struct_handler: Optional[NonStructHandler] = None
        self.handlers: dict[int, StructHandler] = {}
        self.instances: dict[int, Protocol] = {}
        for factory in factories:
            self.register(factory)

    def add_non_struct_handler(self, handler: NonStructHandler) -> None:
        """Set the non-struct handler for this instance."""
        assert self.non_struct_handler is None
        self.non_struct_handler = handler

    def add_handler(self, identifier: int, handler: StructHandler) -> None:
        """Add a struct message handler."""

        assert identifier not in self.handlers
        assert identifier != NON_STRUCT_ID
        self.handlers[identifier] = handler

    def register(self, factory: type[ProtocolFactory]) -> None:
        """Track a protocol factory's structure by identifier."""

        inst = factory.singleton()

        assert inst.id != NON_STRUCT_ID

        if not hasattr(self, "id_primitive"):
            self.id_primitive = inst.id_primitive.copy()  # type: ignore
            self.byte_order = inst.byte_order
            self.non_struct_message_prefix = self.id_primitive.kind.encode(
                NON_STRUCT_ID, byte_order=self.byte_order
            )
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

                # Handle non-struct messages.
                if ident == NON_STRUCT_ID:
                    if self.non_struct_handler is not None:
                        if not self.non_struct_handler(stream):
                            self.logger.error(
                                "Parsing non-struct message failed."
                            )
                            stream.seek(0, os.SEEK_END)
                    else:
                        self.logger.error(
                            "No handler for non-struct messages."
                        )
                        stream.seek(0, os.SEEK_END)

                # Handle struct messages.
                elif ident in self.instances:
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
                    self.logger.error("Unknown struct identifier '%d'.", ident)
                    stream.seek(0, os.SEEK_END)
