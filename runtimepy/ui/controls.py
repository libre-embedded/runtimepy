"""
A module implementing UI controls instances for configuring UI widgets.
"""

# built-in
import math
from typing import Optional

# internal
from runtimepy.primitives.types.bounds import IntegerBounds

Literal = int | float | bool
Default = Optional[Literal]
Controls = dict[str, Literal | dict[str, Literal]]
DEFAULT_STEPS = 64.0


def make_slider(
    min_val: int | float,
    max_val: int | float,
    step: int | float,
    default: Optional[int | float] = None,
) -> Controls:
    """Create dictionary data for a slider element."""

    result: Controls = {
        "slider": {"min": min_val, "max": max_val, "step": step}
    }

    if default is not None:
        result["default"] = default

    return result


def bit_slider(width: int, signed: bool) -> Controls:
    """Make a slider for an unsigned integer width."""
    bounds = IntegerBounds.create_bit(width, signed)
    return make_slider(bounds.min, bounds.max, 2**width - 1)


def signed_slider(width: int) -> Controls:
    """Make a slider for an unsigned integer width."""
    return bit_slider(width, True)


def unsigned_slider(width: int) -> Controls:
    """Make a slider for an unsigned integer width."""
    return bit_slider(width, False)


CANONICAL: dict[str, Controls] = {
    "phase": make_slider(-math.pi, math.pi, 90, default=0.0),
    "amplitude": make_slider(0.0, 2.0, 100.0, default=1.0),
    "period": make_slider(0.0, 0.05, 100.0, default=0.01),
    "steps": make_slider(
        DEFAULT_STEPS / 4,
        DEFAULT_STEPS * 4,
        DEFAULT_STEPS * 2,
        default=DEFAULT_STEPS,
    ),
    "steps_1_1000": make_slider(1, 1000, 100, default=1),
}


Controlslike = Controls | str


def normalize_controls(data: Controlslike) -> Controls:
    """Resolve a canonical control name if necessary."""

    if isinstance(data, str):
        data = CANONICAL[data]
    return data
