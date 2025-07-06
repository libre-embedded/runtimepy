"""
A module implementing web server markdown interfaces.
"""

# built-in
from io import StringIO
import mimetypes
from pathlib import Path
from typing import Iterable, cast

# third-party
from svgen.element.html import div
from vcorelib.io.file_writer import IndentedFileWriter
from vcorelib.math.time import byte_count_str
from vcorelib.paths import rel
from vcorelib.paths import stats as _stats

LOGO_MARKDOWN = "[![logo](/static/png/chip-circle-bootstrap/128x128.png)](/)"
DIR_FILE = "dir.html"


def file_preview(path: Path, link: Path) -> str:
    """Get possible preview text for a file."""

    preview = ""

    if path.is_file():
        mime, _ = mimetypes.guess_type(path, strict=False)
        if mime and mime.startswith("image"):
            preview = div(tag="img", src=f"/{link}", alt=str(link)).encode_str(
                newlines=False
            )

    return preview


def write_markdown_dir(
    writer: IndentedFileWriter, path: Path, base: Path
) -> None:
    """Write markdown contents for a single directory."""

    curr_dir = rel(path, base=base)

    line = f"### `{base.name}/{curr_dir}`"

    # Link to go up a directory.
    if curr_dir != Path():
        line += f" ([..](/{curr_dir.parent}/{DIR_FILE}))"

    writer.write(line)
    writer.empty()

    writer.write("| name | size | preview |")
    writer.write("|------|------|---------|")

    for item in sorted(path.iterdir()):
        curr = rel(item, base=base)

        name = f"`{curr.name}`"
        if item.is_dir():
            name = f"**{name}**"

        stats = _stats(item)
        assert stats
        size_str = byte_count_str(stats.st_size) if item.is_file() else ""

        writer.write(
            f"| [{name}](/{curr}) | {size_str} | {file_preview(item, curr)} |"
        )

    writer.empty()


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
            write_markdown_dir(writer, path, base)

        result: str = cast(StringIO, writer.stream).getvalue()

    return result
