"""
A module for creating various bootstrap-related elements.
"""

# built-in
from io import StringIO

# third-party
from svgen.element import Element
from svgen.element.html import div
from vcorelib.io.file_writer import IndentedFileWriter

# internal
from runtimepy.net.html.bootstrap import icon_str

TEXT = "font-monospace"
BOOTSTRAP_BUTTON = f"rounded-0 {TEXT} text-start text-nowrap"


def flex(kind: str = "row", **kwargs) -> Element:
    """Get a flexbox row container."""

    container = div(**kwargs)
    container["class"] = f"d-flex flex-{kind}"
    return container


DEFAULT_PLACEMENT = "right"


def set_tooltip(
    element: Element, data: str, placement: str = DEFAULT_PLACEMENT
) -> None:
    """Set a tooltip on an element."""

    element["data-bs-title"] = data
    element["data-bs-placement"] = placement
    element.add_class("has-tooltip")


BUTTON_COLOR = "secondary"


def bootstrap_button(
    text: str,
    tooltip: str = None,
    color: str = BUTTON_COLOR,
    placement: str = DEFAULT_PLACEMENT,
    **kwargs,
) -> Element:
    """Create a bootstrap button."""

    button = div(
        tag="button",
        type="button",
        text=text,
        **kwargs,
        class_str=f"btn btn-{color} " + BOOTSTRAP_BUTTON,
    )
    if tooltip:
        set_tooltip(button, tooltip, placement=placement)
    return button


def collapse_button(
    target: str,
    tooltip: str = None,
    icon: str = "arrows-collapse-vertical",
    toggle: str = "collapse",
    **kwargs,
) -> Element:
    """Create a collapse button."""

    collapse = bootstrap_button(icon_str(icon), tooltip=tooltip, **kwargs)
    if target:
        collapse["data-bs-toggle"] = toggle
        collapse["data-bs-target"] = target

    return collapse


def toggle_button(
    parent: Element,
    icon: str = "toggles",
    title: str = None,
    icon_classes: list[str] = None,
    tooltip: str = None,
    placement: str = "top",
    **kwargs,
) -> Element:
    """Add a boolean-toggle button."""

    # if title and not tooltip:
    if not title and tooltip:
        kwargs["title"] = "see tooltip"
    elif title:
        kwargs["title"] = title

    button = div(
        tag="button",
        type="button",
        text=icon_str(icon, classes=icon_classes),
        parent=parent,
        class_str=f"btn {BOOTSTRAP_BUTTON}",
        **kwargs,
    )
    if tooltip:
        set_tooltip(button, tooltip, placement=placement)

    return button


def input_box(
    parent: Element,
    label: str = "",
    pattern: str = ".*",
    description: str = None,
    placement: str = "top",
    icon: str = "",
    **kwargs,
) -> tuple[Element, Element, Element]:
    """Create command input box."""

    container = div(parent=parent, class_str="input-group")

    label_elem = div(tag="span", parent=container)
    label_elem.add_class("input-group-text", "rounded-0", TEXT)

    if description:
        set_tooltip(label_elem, description, placement=placement)

    if icon:
        div(text=icon_str(icon), parent=label_elem)

    box = div(
        tag="input",
        type="text",
        placeholder=pattern,
        parent=container,
        name=label,
        title=label + " input",
        **kwargs,
    )
    box.add_class("form-control", "rounded-0", TEXT)

    return container, label_elem, box


def slider(
    min_val: int | float, max_val: int | float, steps: int, **kwargs
) -> Element:
    """Create a phase-control slider element."""

    elem = div(
        tag="input",
        type="range",
        class_str="m-auto form-range slider",
        **kwargs,
    )

    assert min_val < max_val, (min_val, max_val)

    elem["min"] = min_val
    elem["max"] = max_val

    step = (max_val - min_val) / steps
    if isinstance(min_val, int) and isinstance(max_val, int):
        step = int(step)

    elem["step"] = step

    # add tick marks - didn't seem to work (browser didn't render anything)

    # list_name = f"{name}-datalist"
    # elem["list"] = list_name
    # markers = div(tag="datalist", id=list_name, parent=container, front=True)
    # start = float(elem["min"])
    # num_steps = 8
    # step = (float(elem["max"]) - float(elem["min"])) / num_steps
    # for idx in range(num_steps):
    #     div(tag="option", value=start + (idx * step), parent=markers)

    return elem


TABLE_CLASSES = ["table", "table-hover", "table-striped", "table-bordered"]


def centered_markdown(
    parent: Element,
    markdown: str,
    *container_classes: str,
    table_classes: list[str] = None,
) -> Element:
    """Add centered markdown."""

    container = div(parent=parent)
    container.add_class(
        "flex-grow-1",
        "d-flex",
        "flex-row",
        "justify-content-between",
        *container_classes,
    )

    div(parent=container, class_str="flex-grow-1")

    horiz_container = div(parent=container)
    horiz_container.add_class(
        "d-flex", "flex-column", "justify-content-between"
    )

    div(parent=horiz_container, class_str="flex-grow-1")

    with StringIO() as stream:
        writer = IndentedFileWriter(stream)

        if table_classes is None:
            table_classes = TABLE_CLASSES

        def render_hook(data: str) -> str:
            """Make some adjustments to various element declarations."""

            if table_classes:
                data = data.replace(
                    "<table>", f'<table class="{' '.join(table_classes)}">'
                )

            return data

        writer.write_markdown(markdown, hook=render_hook)
        div(
            text=stream.getvalue(),
            parent=horiz_container,
            class_str="text-body p-3 pb-0",
            preformatted=True,
        )

    div(parent=horiz_container, class_str="flex-grow-1")

    div(parent=container, class_str="flex-grow-1")

    return container
