"""
Test the 'net.server.markdown' module.
"""

# module under test
from runtimepy.net.server.markdown import markdown_for_dir

# internal
from tests.resources import resource


def test_markdown_for_dir():
    """Test basic directory-to-markdown conversions."""

    base = resource("")
    path = resource("channels")
    assert markdown_for_dir(base, base)
    assert markdown_for_dir(path, base)
    assert markdown_for_dir(path, base, extra_links={"a": ["a", "b", "c"]})
