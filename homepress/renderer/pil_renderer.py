from .renderer_abc import Renderer
from ..pages import clip
import PIL.Image
from PIL.Image import Image
from pathlib import Path
from pymupdf import Pixmap, csRGB

PIL.Image.init()

def _pil_to_pixmap(im: Image) -> Pixmap:
    w, h = im.size
    white_bg = PIL.Image.new("RGBA", im.size, "WHITE")
    white_bg.alpha_composite(im)
    im = white_bg.tobytes()
    return Pixmap(csRGB, w, h, im, True)

class PILRenderer(Renderer):
    supported_extensions = [k.strip('.') for k, v in PIL.Image.EXTENSION.items() if v in PIL.Image.OPEN]
    def __init__(self, file) -> None:
        self.file = Path(file)

    def __len__(self) -> int:
        return 1

    def render(self, page, size) -> bytes:
        im = PIL.Image.open(self.file).convert("RGBA")

        clipped_size = clip(im.size, size)
        if clipped_size[0]*clipped_size[1] < im.width*im.height:  # If the clipped size is less than the render size
            im = im.resize((int(clipped_size[0]), int(clipped_size[1])))
        
        return _pil_to_pixmap(im)
    
    def render_preview(self, page) -> bytes:
        return self.render(page, size=(1600, 1600))
    