"""
A module implementing interfaces to include Bootstrap
(https://getbootstrap.com/) in an application.
"""

# third-party
from svgen.element import Element
from svgen.element.html import div

CDN = "cdn.jsdelivr.net"
BOOTSTRAP_VERSION = "5.3.6"
ICONS_VERSION = "1.13.1"


def icon_str(icon: str, classes: list[str] = None) -> str:
    """Get a boostrap icon string."""

    if classes is None:
        classes = []
    classes = ["bi", f"bi-{icon}"] + classes

    return f'<i class="{" ".join(classes)}"></i>'


BOOTSTRAP_ICONS_FILE = "bootstrap-icons.min.css"


def bootstrap_icons_url_base(version: str = ICONS_VERSION) -> str:
    """Get a base URL for bootstrap icon dependencies."""
    return f"https://{CDN}/npm/bootstrap-icons@{version}/font"


def bootstrap_icons_url(online: bool, version: str = ICONS_VERSION) -> str:
    """Get a URL for bootstrap-icons CSS."""

    path = "/" + BOOTSTRAP_ICONS_FILE
    if online:
        path = bootstrap_icons_url_base(version=version) + path
    else:
        path = "/static/css" + path

    return path


BOOTSTRAP_CSS_FILE = "bootstrap.min.css"


def bootsrap_css_url(online: bool, version: str = BOOTSTRAP_VERSION) -> str:
    """Get a URL for bootstrap's CSS."""

    path = "/css/" + BOOTSTRAP_CSS_FILE
    if online:
        path = f"https://{CDN}/npm/bootstrap@{version}/dist" + path
    else:
        path = "/static" + path

    return path


def add_bootstrap_css(element: Element, online: bool) -> None:
    """Add boostrap CSS sources as a child of element."""

    div(
        tag="link",
        rel="stylesheet",
        href=bootstrap_icons_url(online),
        parent=element,
    )

    div(
        tag="link",
        href=bootsrap_css_url(online),
        rel="stylesheet",
        crossorigin="anonymous",
        parent=element,
    )


BOOTSTRAP_JS_FILE = "bootstrap.bundle.min.js"


def bootstrap_js_url(online: bool, version: str = BOOTSTRAP_VERSION) -> str:
    """Get bootstrap's JavaScript URL."""

    path = "/js/" + BOOTSTRAP_JS_FILE
    if online:
        path = f"https://cdn.jsdelivr.net/npm/bootstrap@{version}/dist" + path
    else:
        path = "/static" + path

    return path


def add_bootstrap_js(element: Element, online: bool) -> None:
    """Add bootstrap JavaScript as a child of element."""

    div(
        tag="script",
        src=bootstrap_js_url(online),
        crossorigin="anonymous",
        parent=element,
    )
