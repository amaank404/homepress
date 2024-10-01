from pathlib import Path

from .layout import pages
from .renderer import get_renderer
from . import progress
import PIL
import pymupdf
import time

class Press():
    def __init__(self, files: list[str, Path], ignore_errors = False) -> None:
        self.renderer = get_renderer(files, ignore_errors)

    def midpage(self, **options):
        """
        options:
        size: str, tuple[float, float] - Page Size (name or ratio (h/w), width in inches)
        margin: tuple[top, outer, bottom, inner], give upto 4 parameters, default: all is 0
        
        rtl: bool - Right to left
        flip_even: bool - Flip even pages horizontally by rotating them 180 degrees
        separate_even_odd: bool - Separate even and odd pages
        """
        p_size = options['size']
        if isinstance(p_size, str):
            p_size = pages.get_ratio_width(p_size)

        new_file = pymupdf.Document()

        p_size = pages.get_pixels_from_ppi(*p_size)

        # TODO

    def merge(self, output, **options) -> None:
        """
        output: str, io_stream - output pdf file path (should contain suffix .pdf)

        options:
        resolution: (w, h) - Max resolution in either dimensions, default: (1600, 1600)
        """
        self.progress_merge(output, **options).sync()

    @progress.runs_with_progress
    def progress_merge(self, output, *, progress: progress.Progress = None, **options) -> progress.Progress:
        options.setdefault("resolution", (1600, 1600))
        resolution = options["resolution"]

        new_file = pymupdf.Document()
        progress.set_total(len(self.renderer))

        for x in range(len(self.renderer)):
            pixmap = self.renderer.render(page=x, size=resolution)

            page = new_file.new_page(width=pixmap.width, height=pixmap.height)
            page.insert_image((0, 0, pixmap.width, pixmap.height), pixmap=pixmap)
            progress.increment_progress()

        new_file.ez_save(output)
    
    def images(self, output, **options):
        """
        output: output_folder

        options:
        file_prefix: str - Defaults to nothing
        resolution: (w, h) - Max resolution in either dimension
        format: str - "png", "jpg", other formats are saved using pil (default: png)
        pil_*: options to pass to PIL saver
        jpg_compression: int - defaulting to 95
        """
        self.progress_images(output, **options).sync()
    
    @progress.runs_with_progress
    def progress_images(self, output, *, progress: progress.Progress = None, **options) -> progress.Progress:
        path = Path(output)
        path.mkdir(exist_ok=True)
        
        file_prefix = options.setdefault("file_prefix", "")
        resolution = options.setdefault("resolution", (1600, 1600))
        format = options.setdefault("format", "png")
        jpg_compression = options.setdefault("jpg_compression", 95)

        # Some python-fu to select pil_ arguments and remove the pil_ prefix
        pil_params = dict(map(lambda x: (x[0].removeprefix("pil_"), x[1]), filter(lambda x: x[0].startswith("pil_"), options.items())))

        progress.set_total(len(self.renderer))

        for x in range(len(self.renderer)):
            pixmap = self.renderer.render(page=x, size=resolution)
            if format in ("png", "jpg"):
                pixmap.save(path / f"{file_prefix}{x+1}.{format}", format, jpg_compression)
            else:
                pixmap.pil_save(path / f"{file_prefix}{x+1}.{format}", format, **pil_params)

            progress.increment_progress()

    def text(self) -> list[str]:
        """
        Extracts text from given files (Some file formats may not support this feature) and
        returns it as a list of strings. the index in the string corresponds to page.
        """
        return self.progress_text().sync()

    @progress.runs_with_progress
    def progress_text(self, *, progress: progress.Progress = None) -> progress.Progress:
        progress.set_total(len(self.renderer))
        all_txt = []

        for x in range(len(self.renderer)):
            txt = self.renderer.get_text(x)
            all_txt.append(txt)
            progress.increment_progress()

        return all_txt
    