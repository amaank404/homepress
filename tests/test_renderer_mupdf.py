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


@pytest.mark.parametrize("res", [0, 1, 512])
def test_render(mupdf_renderer: MuPDFRenderer, res):
    for x in range(len(mupdf_renderer)):
        if res <= 0:
            with pytest.raises(ValueError):
                mupdf_renderer.render(x, (res, res))
        else:
            mupdf_renderer.render(x, (res, res))
