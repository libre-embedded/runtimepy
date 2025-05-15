"""
Channel-environment tab widget interfaces.
"""

# built-in
from typing import cast

# third-party
from svgen.element import Element
from svgen.element.html import div

# internal
from runtimepy.channel.environment.command.processor import (
    ChannelCommandProcessor,
)
from runtimepy.enum import RuntimeEnum
from runtimepy.net.html.bootstrap.elements import (
    flex,
    input_box,
    set_tooltip,
    toggle_button,
)


def plot_checkbox(parent: Element, name: str) -> None:
    """Add a checkbox for individual channel plot status."""

    container = div(tag="td", parent=parent, class_str="text-center p-0 fs-5")

    set_tooltip(
        div(
            tag="input",
            type="checkbox",
            value="",
            id=f"plot-{name}",
            allow_no_end_tag=True,
            parent=container,
            class_str="form-check-input rounded-0",
        ),
        f"Enable plotting channel '{name}'.",
        placement="left",
    )


def select_element(**kwargs) -> Element:
    """Create a select element."""

    select = div(tag="select", **kwargs)
    select.add_class(
        "form-select", "rounded-0", "border-top-0", "border-bottom-0"
    )
    if "title" in kwargs:
        select["aria-label"] = kwargs["title"]
    return select


def enum_dropdown(
    parent: Element, name: str, enum: RuntimeEnum, current: int | bool
) -> Element:
    """Implement a drop down for enumeration options."""

    select = select_element(
        parent=parent, title=f"Enumeration selection for '{name}'.", id=name
    )

    for key, val in cast(dict[str, dict[str, int | bool]], enum.asdict())[
        "items"
    ].items():
        opt = div(tag="option", value=val, text=key, parent=select)
        if current == val:
            opt.booleans.add("selected")

    return select


TABLE_BUTTON_CLASSES = ()


def channel_table_header(
    parent: Element, command: ChannelCommandProcessor
) -> None:
    """Add header row to channel table."""

    env = command.env

    # Add header.
    header_row = div(
        tag="tr", parent=parent, class_str="border-start border-end"
    )
    for heading, desc in [
        ("plot", "Toggle plotting for channels."),
        ("name", "Channel names."),
        ("value", "Channel values."),
        ("ctl", "Type-specific channel controls."),
        ("type", "Channel types."),
    ]:
        set_tooltip(
            div(
                tag="th",
                scope="col",
                parent=header_row,
                text=heading,
                class_str="text-secondary p-1",
            ),
            desc,
            placement="left",
        )

    # Add some controls.
    ctl_row = div(tag="tr", parent=parent, class_str="border-start border-end")

    # Button for clearing plotted channels.
    toggle_button(
        div(tag="th", parent=ctl_row, class_str="text-center p-0"),
        tooltip="Clear plotted channels.",
        icon="x-lg",
        id="clear-plotted-channels",
        title="button for clearing plotted channels",
    )

    _, label, box = input_box(
        div(tag="th", parent=ctl_row, class_str="p-0"),
        description="Channel name filter.",
        id="channel-filter",
    )
    label.add_class("border-top-0", "border-bottom-0")
    box.add_class("border-top-0", "border-bottom-0")

    cell = flex(
        parent=div(tag="th", parent=ctl_row, class_str="p-0")
    ).add_class("justify-content-evenly")

    # Button for clearing plot points.
    toggle_button(
        cell,
        icon="trash",
        tooltip="Clear all plot points.",
        id="clear-plotted-points",
        title="button for clearing plot point data",
        icon_classes=["text-secondary-emphasis"],
    )

    toggle_button(
        cell,
        icon="eye-slash",
        tooltip="Toggle command channels.",
        id="toggle-command-channels",
        title="button for toggling command-channel visibility",
        icon_classes=["text-info-emphasis"],
    )
    toggle_button(
        cell,
        icon="eye-slash-fill",
        tooltip="Toggle regular channels.",
        id="toggle-regular-channels",
        title="button for toggling regular-channel visibility",
    )

    cell = flex(
        parent=div(tag="th", parent=ctl_row, class_str="p-0")
    ).add_class("justify-content-evenly")

    # Button for 'reset all defaults' if this tab has more than one channel
    # with a default value.
    if env.num_defaults > 1:
        toggle_button(
            cell,
            id="set-defaults",
            icon="arrow-counterclockwise",
            tooltip="Reset all channels to their default values.",
        ).add_class(*TABLE_BUTTON_CLASSES)

    # Add a selection menu for custom commands.
    select = select_element(
        parent=cell, id="custom-commands", title="Custom command selector."
    )
    if command.custom_commands:
        for key in command.custom_commands:
            opt = div(tag="option", value=key, text=key, parent=select)
            if len(select.children) == 1:
                opt.booleans.add("selected")

        # Add button to send command.
        toggle_button(
            cell,
            icon="send",
            id="send-custom-commands",
            title="Send selected command.",
        ).add_class(*TABLE_BUTTON_CLASSES)
    else:
        div(
            tag="option",
            parent=select,
            value="noop",
            text="no custom commands",
        )
        select.booleans.add("disabled")

    # Empty for now.
    div(tag="th", parent=ctl_row, class_str="p-0")


def value_input_box(name: str, parent: Element) -> Element:
    """Create an input box for channel values."""

    input_container = flex(parent=parent)
    div(
        tag="input",
        type="text",
        parent=input_container,
        title=f"Set command value for '{name}'.",
        id=name,
    ).add_class(
        "channel-value-input",
        "rounded-0",
        "font-monospace",
        "form-control",
        "p-0",
        "ps-2",
        "border-0",
        "text-secondary-emphasis",
    )
    toggle_button(
        input_container,
        icon="send",
        id=name,
        title=f"Send command value for '{name}'.",
    ).add_class("pt-0", "pb-0", "ps-1", *TABLE_BUTTON_CLASSES)

    return input_container
