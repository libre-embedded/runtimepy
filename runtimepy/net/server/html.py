"""
A module implementing HTML interfaces for web applications.
"""

# built-in
from typing import Awaitable, Callable, Optional, TextIO

# third-party
from svgen.element import Element
from svgen.element.html import Html
from vcorelib import DEFAULT_ENCODING

# internal
from runtimepy.net.http.header import RequestHeader
from runtimepy.net.http.response import ResponseHeader
from runtimepy.net.tcp.http import HttpConnection

HtmlApp = Callable[
    [Html, RequestHeader, ResponseHeader, Optional[bytearray]], Awaitable[Html]
]
HtmlApps = dict[str, HtmlApp]


def get_html(
    title: str = HttpConnection.identity,
    cache_control: str = "public",
    description: str = None,
    **kwargs,
) -> Html:
    """Get a default HTML document."""

    elem = Html(title, **kwargs)

    elem.head.children.append(
        Element(
            tag="meta",
            attrib={"http-equiv": "Cache-Control", "content": cache_control},
        )
    )

    elem.head.children.append(
        Element(tag="link", rel="icon", href="/favicon.ico")
    )

    if description:
        elem.head.children.append(
            Element(
                tag="meta",
                attrib={"name": "description", "content": description},
            )
        )

    return elem


async def html_handler(
    apps: HtmlApps,
    stream: TextIO,
    request: RequestHeader,
    response: ResponseHeader,
    request_data: Optional[bytearray],
    default_app: HtmlApp = None,
    **kwargs,
) -> bool:
    """Render an HTML document in response to an HTTP request."""

    # Set response headers.
    response["Content-Type"] = f"text/html; charset={DEFAULT_ENCODING}"

    # Create the application.
    app = apps.get(request.target.path, default_app)
    if app is not None:
        (
            await app(get_html(**kwargs), request, response, request_data)
        ).render(stream)

    return app is not None
