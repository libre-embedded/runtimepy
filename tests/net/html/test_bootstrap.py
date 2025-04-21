"""
Test the 'net.html.bootstrap' module.
"""

# module under test
from runtimepy.net.html.bootstrap import (
    bootsrap_css_url,
    bootstrap_icons_url,
    bootstrap_icons_url_base,
    bootstrap_js_url,
)


def test_bootstrap_basic():
    """Basic tests for bootstrap-related interfaces."""

    assert bootstrap_icons_url_base()

    assert bootstrap_icons_url(True)
    assert bootsrap_css_url(True)
    assert bootstrap_js_url(True)
