"""
Test the 'ui.controls' module.
"""

# module under test
from runtimepy.ui.controls import signed_slider, unsigned_slider


def test_ui_controls_basic():
    """Exercise basic interfaces."""

    assert signed_slider(5)
    assert unsigned_slider(5)
