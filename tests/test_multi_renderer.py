import pytest
from test_renderer import TestRenderer

from homepress.renderer.multi_renderer import MultiRenderer


@pytest.fixture(scope="module")
def multi_renderer():
    return MultiRenderer([TestRenderer() for _ in range(10)])


def test_multi_renderer_out_of_range(multi_renderer: MultiRenderer):
    with pytest.raises(IndexError):
        multi_renderer.render(17, (10, 10))


def test_multi_renderer_in_range(multi_renderer: MultiRenderer):
    assert "RES" == multi_renderer.render(8, (10, 10))


def test_multi_renderer_preview(multi_renderer: MultiRenderer):
    assert "RESPREV" == multi_renderer.render_preview(7)


def test_multi_renderer_get_text(multi_renderer: MultiRenderer):
    assert TestRenderer().get_text(0) == multi_renderer.get_text(1)
