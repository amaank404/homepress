import logging

import data
import pytest

import homepress.renderer
from homepress.renderer import get_renderer

# Uncomment this if u wish to run the code
# at test_get_renderer_files_unsupported_with_ignore_errors
#
# def _flatten(e, d=None):
#     if d is None:
#         d = []
#     for x in e:
#         if hasattr(x, "renderers"):
#             _flatten(x.renderers, d)
#         elif hasattr(x, "renderer"):
#             _flatten([x.renderer], d)
#         else:
#             d.append(x)
#
#     return d


def test_get_renderer_files():
    get_renderer(list(data.dataset.filter_extension(["pdf", "svg", "xps"])))


def test_get_renderer_files_unsupported():
    with pytest.raises(TypeError):
        get_renderer(list(data.dataset.filter_extension(["bin"])))


def test_get_renderer_files_unsupported_with_ignore_errors():
    a = get_renderer([data.root], True)
    b = get_renderer(list(data.dataset.filter_extension(homepress.renderer.formats)))

    # Code below was used to find differences as to where the file might've been and where it might've not been
    # taken up by the get_renderer method

    # sortbyfname = lambda x: str(x.file.resolve())
    # sortbyfname2 = lambda x: str(x.file.resolve().name)

    # a_flat = _flatten(a.renderers)
    # b_flat = _flatten(b.renderers)

    # a_flat.sort(key=sortbyfname)
    # b_flat.sort(key=sortbyfname)

    # a_n = [sortbyfname2(x) for x in a_flat]
    # b_n = [sortbyfname2(x) for x in b_flat]

    # for x, y in zip(a_n, b_n):
    #     logging.warning(f"{x} {y}")

    assert len(a) == len(b)


def test_get_renderer_files_folder():
    assert len(get_renderer([data.root / "testdata" / "filesamples.com"])) != 0
