import pytest
from test_renderer import TestRenderer

from homepress.renderer import MultiRenderer
from homepress.renderer.page_range_renderer import PageRangeRenderer


@pytest.fixture(scope="module")
def page_renderer():
    return PageRangeRenderer(
        MultiRenderer([TestRenderer(render_res=x) for x in range(10)]), range(2, 8)
    )


def test_page_renderer_out_of_range(page_renderer: PageRangeRenderer):
    with pytest.raises(IndexError):
        page_renderer.render(6, (10, 10))


def test_page_renderer_in_range(page_renderer: PageRangeRenderer):
    assert 7 == page_renderer.render(5, (10, 10))


def test_page_renderer_preview(page_renderer: PageRangeRenderer):
    assert "RESPREV" == page_renderer.render_preview(2)


def test_page_renderer_get_text(page_renderer: PageRangeRenderer):
    assert TestRenderer().get_text(0) == page_renderer.get_text(1)


def test_page_renderer_len(page_renderer: PageRangeRenderer):
    assert 6 == len(page_renderer)
