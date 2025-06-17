"""
A module implementing web server markdown interfaces.
"""

# built-in
from io import StringIO
from pathlib import Path
from typing import Iterable, cast

# third-party
from vcorelib.io.file_writer import IndentedFileWriter
from vcorelib.paths import rel

LOGO_MARKDOWN = "[![logo](/static/png/chip-circle-bootstrap/128x128.png)](/)"
DIR_FILE = "dir.html"


def markdown_for_dir(
    paths_bases: Iterable[tuple[Path, Path]],
    extra_links: dict[str, Iterable[str]] = None,
) -> str:
    """Get markdown data for a directory."""

    with IndentedFileWriter.string() as writer:
        writer.write(f"# Directory {LOGO_MARKDOWN} Viewer")
        with writer.padding():
            writer.write("---")

        if extra_links:
            for category, apps in extra_links.items():
                if apps:
                    writer.write(f"## {category}")
                    with writer.padding():
                        for app in apps:
                            writer.write(f"* [{app}]({app})")

        writer.write("## directories")
        writer.empty()

        for path, base in paths_bases:
            curr_dir = rel(path, base=base)
            writer.write(f"### `{base.name}/{curr_dir}`")
            writer.empty()

            # Link to go up a directory.
            if curr_dir != Path():
                writer.write(f"* [..](/{curr_dir.parent}/{DIR_FILE})")

            for item in sorted(path.iterdir()):
                curr = rel(item, base=base)

                name = f"`{curr.name}`"
                if item.is_dir():
                    name = f"**{name}**"

                writer.write(f"* [{name}](/{curr})")

        result: str = cast(StringIO, writer.stream).getvalue()

    return result
