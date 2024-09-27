from .renderer_abc import  Renderer

class MultiRenderer(Renderer):
    """
    A renderer to combine multiple different renderers
    """
    def __init__(self, renderers) -> None:
        self.renderers = renderers
        self.lens = list(map(len, renderers))

    def __len__(self) -> int:
        return sum(self.lens)

    def _localise_pageno(self, pageno) -> tuple[Renderer, int]:
        idx = pageno
        for i, x in enumerate(self.lens):
            if (idx - x) < 0:
                return (self.renderers[i], idx)
            idx -= x
        raise IndexError(f"Page out of range: {pageno}/{len(self)}")
    
    def render(self, page, size) -> bytes:
        r, p = self._localise_pageno(page)
        return r.render(p, size)
    
    def render_preview(self, page) -> bytes:
        r, p = self._localise_pageno(page)
        return r.render_preview(p)
    
    def get_text(self, page) -> str:
        r, p = self._localise_pageno(page)
        return r.get_text(p)