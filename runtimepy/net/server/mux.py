"""
A module implementing an interface for serving a web application that allows
iframe-based grid multiplexing.
"""

# built-in
from typing import Optional

# third-party
from svgen.element.html import Html

# internal
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader


async def mux_app(
    document: Html,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytearray],
) -> Html:
    """An iframe multiplexing application."""

    del request
    del response
    del request_data

    return document
