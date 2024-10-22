import data
import pytest

from homepress.renderer.pil_renderer import PILRenderer


@pytest.fixture(
    scope="module",
    params=list(data.dataset.filter_extension(PILRenderer.supported_extensions)),
)
def pil_renderer(request):
    return PILRenderer(request.param)


def test_render_preview(pil_renderer: PILRenderer):
    pil_renderer.render_preview(0)


@pytest.mark.parametrize("res", [0, 1, 64])
def test_render(pil_renderer: PILRenderer, res):
    if res <= 0:
        with pytest.raises(ValueError):
            pil_renderer.render(0, (res, res))
    else:
        pil_renderer.render(0, (res, res))


def test_out_of_range(pil_renderer: PILRenderer):
    with pytest.raises(IndexError):
        pil_renderer.render(1, (64, 64))
