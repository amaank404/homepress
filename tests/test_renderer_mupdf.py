import logging

import data
import pytest

from homepress.renderer.mupdf_renderer import MuPDFRenderer


@pytest.fixture(
    scope="module",
    params=list(data.dataset.filter_extension(MuPDFRenderer.supported_extensions)),
)
def mupdf_renderer(request):
    return MuPDFRenderer(request.param)


def test_get_text(mupdf_renderer: MuPDFRenderer):
    for x in range(len(mupdf_renderer)):
        mupdf_renderer.get_text(x)


def test_render_preview(mupdf_renderer: MuPDFRenderer):
    for x in range(len(mupdf_renderer)):
        mupdf_renderer.render_preview(x)


@pytest.mark.parametrize("res", [0, 1, 64])
def test_render(mupdf_renderer: MuPDFRenderer, res):
    logging.info(f"render test for: {mupdf_renderer.file}")
    for x in range(len(mupdf_renderer)):
        if res <= 0:
            with pytest.raises(ValueError):
                mupdf_renderer.render(x, (res, res))
        else:

            mupdf_renderer.render(x, (res, res))


def test_out_of_range(mupdf_renderer: MuPDFRenderer):
    with pytest.raises(IndexError):
        mupdf_renderer.render(len(mupdf_renderer) + 10, (64, 64))


def test_file_exists():
    with pytest.raises(FileNotFoundError):
        renderer = MuPDFRenderer(
            "asbsladoibibqwiogriobibhgioiovhaoivhgiovhgiovhari.pdf"
        )
        renderer.render(1, (1000, 1000))
