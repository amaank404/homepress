from .renderer_abc import Renderer
import pymupdf
from ..pages import clip

class MuPDFRenderer(Renderer):
    supported_extensions = [
        "pdf",
        "epub",
        "cbz",
        "cbr",
        "fb2"
    ]
    def __init__(self, file) -> None:
        self.fp = pymupdf.open(file)

    def render(self, page: int, size: tuple[int, int], *, _render_format=None):
        page = self.fp[page]
        p_size = page.cropbox
        p_size = (p_size.width, p_size.height)
        new_size = clip(p_size, size)  # Final size

        scale_factor = new_size[0]/p_size[0]  # Scale factor

        img = page.get_pixmap(matrix=pymupdf.Matrix(scale_factor, scale_factor), clip=page.cropbox, annots=True)

        return img
    
    def render_preview(self, page: int):
        return self.render(page, (420, 420), _render_format="jpg")  #31 ppi for a4 size
    
    def get_text(self, page) -> str:
        page = self.fp[page]
        txt = page.get_text()
        return txt
    
    def __len__(self):
        return self.fp.page_count