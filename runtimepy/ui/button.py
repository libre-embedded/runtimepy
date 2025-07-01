"""
A module implementing an action-button interface.
"""

# built-in
from json import dumps
from typing import NamedTuple

# third-party
from svgen.element import Element
from svgen.element.html import div
from vcorelib.dict import GenericStrDict

# internal
from runtimepy.net.html.bootstrap import icon_str


class ActionButton(NamedTuple):
    """A class implementing an interface for action buttons."""

    key: str
    payload: GenericStrDict
    text: str
    icon: str
    variant: str
    outline: bool

    @staticmethod
    def from_dict(data: GenericStrDict) -> "ActionButton":
        """Create an action button from dictionary data."""

        return ActionButton(
            data["key"],
            data["payload"],
            data.get("text", ""),
            data.get("icon", ""),
            data.get("variant", "primary"),
            data.get("outline", True),
        )

    @staticmethod
    def from_top_level(
        data: GenericStrDict | list[GenericStrDict],
    ) -> list["ActionButton"]:
        """Create an action button from dictionary data."""

        return (
            [ActionButton.from_dict(x) for x in data.get("buttons", [])]
            if isinstance(data, dict)
            else [ActionButton.from_dict(x) for x in data]
        )

    def element(self) -> Element:
        """Create an action button element."""

        payload = dumps(self.payload).replace('"', "&quot;")

        text_parts = []
        if self.icon:
            text_parts.append(
                icon_str(
                    self.icon,
                    [f"text-{self.variant}-emphasis"] if self.text else [],
                )
            )
        if self.text:
            text_parts.append(self.text)

        return div(
            tag="button",
            type="button",
            onclick=f"tabs[shown_tab].worker.bus('{self.key}', {payload})",
            class_str=f"btn btn{'-outline' if self.outline else ''}"
            f"-{self.variant} m-2 ms-1 me-0",
            text=" ".join(text_parts),
        )
