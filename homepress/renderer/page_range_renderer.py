from pymupdf import Pixmap

from .renderer_abc import Renderer


class PageRangeRenderer(Renderer):
    def __init__(self, renderer: Renderer, *page_range) -> None:
        self.renderer = renderer
        self.pages = []
        for x in page_range:
            # If its a single page number
            if isinstance(x, int):
                self.pages.append(x)
            # If its an iterable of page numbers
            else:
                self.pages.extend(x)

        renderer_len = len(self.renderer)
        for x in self.pages:
            if x >= renderer_len:
                raise IndexError("Given page range out of renderer range")

    def __len__(self) -> int:
        return len(self.pages)

    def render(self, page, size) -> Pixmap:
        return self.renderer.render(self.pages[page], size)

    def render_preview(self, page) -> Pixmap:
        return self.renderer.render_preview(self.pages[page])

    def get_text(self, page) -> str:
        return self.renderer.get_text(self.pages[page])