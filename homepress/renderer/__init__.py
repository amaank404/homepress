import logging
from pathlib import Path

from .multi_renderer import MultiRenderer
from .mupdf_renderer import MuPDFRenderer
from .page_range_renderer import PageRangeRenderer
from .pil_renderer import PILRenderer
from .renderer_abc import Renderer

# All the supported renderers
renderers = [MuPDFRenderer, PILRenderer]

# All the supported formats
formats = set()
for x in renderers:
    formats.update(x.supported_extensions)


def get_renderer(files, ignore_errors=False):
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
                sorted(list(path.iterdir()), key=lambda x: x.name), ignore_errors
            )
        elif path.is_file():
            ext = path.suffix.strip(".")
            if ext in formats:
                for x in renderers:
                    if ext in x.supported_extensions:
                        return x(files[0])
        raise TypeError("File format not supported")

    else:
        render = []
        for x in files:
            try:
                render.append(get_renderer([x]))
            except Exception as e:
                if ignore_errors:
                    logging.warning(f"ignored: {e}")
                else:
                    raise e

        return MultiRenderer(render)
