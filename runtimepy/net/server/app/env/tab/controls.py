"""
A module implementing channel control HTML rendering.
"""

# built-in
from typing import Optional, cast

# third-party
from svgen.element import Element
from svgen.element.html import div

# internal
from runtimepy.channel import AnyChannel
from runtimepy.channel.environment import ChannelEnvironment
from runtimepy.enum import RuntimeEnum
from runtimepy.net.html.bootstrap.elements import slider, toggle_button
from runtimepy.net.server.app.env.tab.base import ChannelEnvironmentTabBase
from runtimepy.net.server.app.env.widgets import (
    TABLE_BUTTON_CLASSES,
    enum_dropdown,
    value_input_box,
)
from runtimepy.ui.controls import Controls, Default


def get_channel_kind_str(
    env: ChannelEnvironment, chan: AnyChannel, enum: Optional[RuntimeEnum]
) -> str:
    """Get a string for this channel's type for a UI."""

    kind_str = str(chan.type)
    if enum is not None:
        enum_name = env.enums.names.name(enum.id)
        assert enum_name is not None
        kind_str = enum_name

    return kind_str


def default_button(
    parent: Element,
    name: str,
    default: Default,
    *classes: str,
    front: bool = True,
) -> Element:
    """Create a default-value button."""

    button = toggle_button(
        parent,
        id=name,
        icon="arrow-counterclockwise",
        title=f"Reset '{name}' to default value '{default}'.",
        value=default,
        front=front,
    )
    button.add_class("default-button", *classes)
    return button


def handle_controls(parent: Element, name: str, controls: Controls) -> None:
    """Add control elements."""

    # Determine if a slider should be created.
    if "slider" in controls:
        elem = controls["slider"]

        slider(
            elem["min"],  # type: ignore
            elem["max"],  # type: ignore
            int(elem["step"]),  # type: ignore
            parent=parent,
            id=name,
            title=f"Value control for '{name}'.",
        ).add_class("bg-body", "rounded-pill", "me-2")


class ChannelEnvironmentTabControls(ChannelEnvironmentTabBase):
    """A channel-environment tab interface."""

    def _handle_controls(
        self,
        parent: Element,
        name: str,
        chan: AnyChannel,
        enum: Optional[RuntimeEnum],
    ) -> None:
        """Handle channel controls."""

        env = self.command.env

        # Add boolean/bit toggle button.
        control = div(tag="td", parent=parent, class_str="p-0")

        if chan.commandable:
            control.add_class("border-start-info-subtle")
            parent.add_class("channel-commandable")
        else:
            parent.add_class("channel-regular")

        chan_type = div(
            tag="td",
            text=get_channel_kind_str(env, chan, enum),
            parent=parent,
            title=f"Underlying primitive type for '{name}'.",
            class_str="p-0 ps-2 pe-1",
        )

        control_added = False

        if enum:
            chan_type.add_class("fw-bold")

            if chan.commandable and not chan.type.is_boolean:
                enum_dropdown(
                    control, name, enum, cast(int, chan.raw.value)
                ).add_class(
                    "border-0",
                    "text-secondary-emphasis",
                    "pt-0",
                    "pb-0",
                    "d-inline",
                )
                control.add_class("border-end-info-subtle")
                control_added = True

                if chan.default is not None:
                    default_button(
                        control,
                        name,
                        chan.default,
                        "p-0",
                        "d-inline",
                        *TABLE_BUTTON_CLASSES,
                        front=False,
                    )

        if chan.type.is_boolean:
            chan_type.add_class("text-primary")
            if chan.commandable:
                button = toggle_button(
                    control, id=name, title=f"Toggle '{name}'."
                )
                button.add_class(
                    "toggle-value",
                    "pt-0",
                    "pb-0",
                    "fs-5",
                    "border-end-info-subtle",
                    *TABLE_BUTTON_CLASSES,
                )
                control_added = True

                if chan.default is not None:
                    default_button(
                        control,
                        name,
                        chan.default,
                        "p-0",
                        *TABLE_BUTTON_CLASSES,
                        front=False,
                    )

        elif chan.type.is_float:
            chan_type.add_class("text-secondary-emphasis")
        else:
            chan_type.add_class("text-primary-emphasis")

        # Input box with send button.
        if not control_added and chan.commandable:
            control.add_class("border-end-info-subtle")

            container = value_input_box(name, control).add_class(
                "justify-content-start"
            )

            # Reset-to-default button if a default value exists.
            if chan.default is not None:
                default_button(
                    container,
                    name,
                    chan.default,
                    "pt-0",
                    "pb-0",
                    *TABLE_BUTTON_CLASSES,
                    front=False,
                )

            if chan.controls:
                handle_controls(container, name, chan.controls)

    def _bit_field_controls(
        self,
        parent: Element,
        name: str,
        is_bit: bool,
        enum: Optional[RuntimeEnum],
    ) -> None:
        """Add control elements for bit fields."""

        control = div(tag="td", parent=parent, class_str="p-0")

        field = self.command.env.fields[name]
        if field.commandable:
            control.add_class("border-start-info-subtle")
            parent.add_class("channel-commandable")

            if not is_bit:
                control.add_class("border-end-info-subtle")

            if is_bit:
                button = toggle_button(
                    control, id=name, title=f"Toggle '{name}'."
                )
                button.add_class(
                    "toggle-value",
                    "pt-0",
                    "pb-0",
                    "fs-5",
                    "border-start-0",
                    "border-end-info-subtle",
                    *TABLE_BUTTON_CLASSES,
                )
                if field.default is not None:
                    default_button(
                        control,
                        name,
                        field.default,  # type: ignore
                        "p-0",
                        *TABLE_BUTTON_CLASSES,
                        front=False,
                    )

            elif enum:
                enum_dropdown(control, name, enum, field()).add_class(
                    "border-0",
                    "text-secondary-emphasis",
                    "pt-0",
                    "pb-0",
                    "d-inline",
                )
                if field.default is not None:
                    default_button(
                        control,
                        name,
                        field.default,  # type: ignore
                        "p-0",
                        "d-inline",
                        *TABLE_BUTTON_CLASSES,
                        front=False,
                    )
            else:
                container = value_input_box(name, control).add_class(
                    "justify-content-start"
                )

                if field.default is not None:
                    default_button(
                        container,
                        name,
                        field.default,  # type: ignore
                        "pt-0",
                        "pb-0",
                        *TABLE_BUTTON_CLASSES,
                        front=False,
                    )

                if field.controls:
                    handle_controls(container, name, field.controls)
        else:
            parent.add_class("channel-regular")
