import logging
from functools import cmp_to_key
from pathlib import Path

from .multi_renderer import MultiRenderer
from .mupdf_renderer import MuPDFRenderer
from .page_range_renderer import PageRangeRenderer
from .pil_renderer import PILRenderer
from .renderer_abc import Renderer

__all__ = ["get_renderer", "MultiRenderer", "PageRangeRenderer", "Renderer"]

# All the supported real renderers
renderers: list[Renderer] = [MuPDFRenderer, PILRenderer]

# All the supported formats
formats: set[str] = set()
for x in renderers:
    formats.update(x.supported_extensions)


def _split_into_parts(k: str):
    """
    Splits the input string into multiple parts
    "a124eajnf.12.@32" would turn to
        ['a', '123', 'eajnf', '.', '12', '.@', '32']


    Args:
        k (str): The string to split

    Returns:
        list[str]: The returned list
    """
    d = []
    buff = ""
    mode = "s"
    for x in k:
        if x.isdigit():
            if mode == "i":
                buff += x
            else:
                mode = "i"
                d.append(buff)
                buff = x
        else:
            if mode == "s":
                buff += x
            else:
                mode = "s"
                d.append(int(buff))
                buff = x

    if buff:
        if mode == "i":
            d.append(int(buff))
        else:
            d.append(buff)

    return d


# TODO: Implement this
def _name_num_sort_cmp(a: str, b: str):
    a_parts = _split_into_parts(a)
    b_parts = _split_into_parts(b)

    for x, y in zip(a_parts, b_parts):
        if x > y:
            return 1
        elif x < y:
            return -1

    if len(a_parts) > len(b_parts):
        return 1
    elif len(b_parts) > len(a_parts):
        return -1
    return 0


_name_num_sort_key = cmp_to_key(_name_num_sort_cmp)


def get_renderer(files: list | Renderer, ignore_errors: bool = False) -> Renderer:
    """
    Given a set of files (May contain recursivly traversed folders), return a renderer that
    aggregates all the given files into a single renderer instance.
    """
    global renderers

    if isinstance(files, Renderer):
        return files

    if len(files) == 1:
        path = Path(files[0])
        if path.is_dir():
            return get_renderer(
                sorted(list(path.iterdir()), key=lambda x: _name_num_sort_key(x.name)),
                ignore_errors,
            )
        elif path.is_file():
            ext = path.suffix.strip(".")
            if ext in formats:
                for x in renderers:
                    if ext in x.supported_extensions:
                        return x(files[0])
        elif not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        raise TypeError(f"File format not supported for {path}")

    else:
        render = []
        for x in files:
            try:
                render.append(get_renderer([x], ignore_errors=ignore_errors))
            except TypeError as e:
                if ignore_errors:
                    logging.warning(f"ignored: {e}")
                else:
                    raise e

        return MultiRenderer(render)
