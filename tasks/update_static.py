"""
A module implementing an interface to update static package content from
internet sources.
"""

# built-in
from pathlib import Path

# third-party
import aiofiles
import requests
from vcorelib.paths import find_file

# internal
from runtimepy import PKG_NAME
from runtimepy.net.arbiter import AppInfo
from runtimepy.net.html.bootstrap import (
    BOOTSTRAP_CSS_FILE,
    BOOTSTRAP_ICONS_FILE,
    BOOTSTRAP_JS_FILE,
    bootsrap_css_url,
    bootstrap_icons_url,
    bootstrap_icons_url_base,
    bootstrap_js_url,
)

WEBGL_FILE = "webglplot.umd.min.js"
BOOTSTRAP_HASH = "dd67030699838ea613ee6dbda90effa6"


async def url_to(url: str, dest: Path) -> None:
    """Write a URL to a destination path."""

    req = requests.request("GET", url, timeout=10.0)
    req.raise_for_status()
    async with aiofiles.open(dest, mode="wb") as path_fd:
        await path_fd.write(req.content)


async def bootstrap_icons(
    css_out: Path, hash_str: str = BOOTSTRAP_HASH
) -> None:
    """Update bootstrap icon static assets."""

    await url_to(
        bootstrap_icons_url(True), css_out.joinpath(BOOTSTRAP_ICONS_FILE)
    )

    fonts = css_out.joinpath("fonts")
    fonts.mkdir(parents=True, exist_ok=True)

    for filename in ["bootstrap-icons.woff2", "bootstrap-icons.woff"]:
        await url_to(
            bootstrap_icons_url_base() + f"/fonts/{filename}?{hash_str}",
            fonts.joinpath(filename),
        )


async def run(_: AppInfo) -> int:
    """Download internet dependencies."""

    path = find_file("favicon.ico", package=PKG_NAME)
    assert path is not None
    path = path.parent.joinpath("static")

    css_out = path.joinpath("css")
    css_out.mkdir(parents=True, exist_ok=True)

    await bootstrap_icons(css_out)

    # bootstrap css
    await url_to(bootsrap_css_url(True), css_out.joinpath(BOOTSTRAP_CSS_FILE))

    js_out = path.joinpath("js")
    js_out.mkdir(parents=True, exist_ok=True)

    # bootstrap js
    await url_to(bootstrap_js_url(True), js_out.joinpath(BOOTSTRAP_JS_FILE))

    # webgl plotter
    await url_to(
        "https://cdn.jsdelivr.net/gh/danchitnis/webgl-plot@master"
        f"/dist/{WEBGL_FILE}",
        js_out.joinpath(WEBGL_FILE),
    )

    return 0
