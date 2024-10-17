from pathlib import Path

import PIL.Image
from PIL.Image import Image
from pymupdf import Pixmap, csRGB

from ..layout.pages import clip
from .renderer_abc import Renderer, Size

PIL.Image.init()


def _pil_to_pixmap(im: Image) -> Pixmap:
    w, h = im.size
    white_bg = PIL.Image.new("RGBA", im.size, "WHITE")
    white_bg.alpha_composite(im)
    im = white_bg.tobytes()
    return Pixmap(csRGB, w, h, im, True)


class PILRenderer(Renderer):
    supported_extensions = [
        k.strip(".") for k, v in PIL.Image.EXTENSION.items() if v in PIL.Image.OPEN
    ]

    def __init__(self, file: Path | str) -> None:
        self.file = Path(file)

    def __len__(self) -> int:
        return 1

    def render(self, page: int, size: Size) -> Pixmap:
        """
        Converts the given input image to a Pixmap based on the size.
        """
        im = PIL.Image.open(self.file).convert("RGBA")

        clipped_size = clip(im.size, size)
        if (
            clipped_size[0] * clipped_size[1] < im.width * im.height
        ):  # If the clipped size is less than the render size
            im = im.resize((int(clipped_size[0]), int(clipped_size[1])))

        return _pil_to_pixmap(im)

    def render_preview(self, page: int) -> Pixmap:
        """
        Scale down the image to a max of 420 in either dimensions and returns the
        pixmap after doing that
        """
        return self.render(page, size=(420, 420))
