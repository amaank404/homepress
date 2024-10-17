import io
import shutil
from pathlib import Path
from typing import Any, BinaryIO, SupportsIndex

import pymupdf

from . import bindermath, progress
from .layout import pages
from .progress import Progress
from .renderer import PageRangeRenderer, Renderer, get_renderer


def _flatten[T](l: list[list[T]]) -> list[T]:
    temp = []
    for x in l:
        temp.extend(x)
    return temp


def _set_defaults_and_check_unknown(
    opts: dict[str, Any], defaults: dict[str, Any], ignore_prefix: tuple[str] = ()
):
    for k, v in defaults.items():
        opts.setdefault(k, v)

    for x in opts:
        skip = False
        for y in ignore_prefix:
            if x.startswith(y):
                skip = True
        if not skip:
            if x not in defaults:
                # Raise error if an unknown option is passed to the function
                raise TypeError(f"Unrecognised options {x}")


class Press:
    """
    A Press object to process input files in several different ways

    ignore_errors: bool - ignore errors while reading the input files
    pages: None -
    """

    def __init__(
        self,
        files: list[str | Path] | Renderer,
        ignore_errors: bool = False,
        pages: list[int | SupportsIndex] = None,
    ) -> None:
        self.renderer = get_renderer(files, ignore_errors)
        if pages is not None:
            self.renderer = PageRangeRenderer(self.renderer, *pages)

    def midpage_multi(self, output: str | Path | BinaryIO, **options) -> None:
        """
        output: str, Path, BinaryIO, folder_path - output pdf file path (should contain suffix .pdf)

        options:
        size: str, tuple[float, float] - Page Size (name or ratio (w/h), width in inches)
        margin: tuple[top, outer, bottom, inner], give upto 4 parameters, default: all is 0
        ppi: int - Pixels per inch (default: 200)

        rtl: bool - Right to left
        flip_even: bool - Flip even pages horizontally by rotating them 180 degrees
        separate_stacks: bool - Separates the stacks into multiple pdf files, (default False)
            if true, provide a folder to the output parameter instead.
        stack_prefix: str - Prefix for stack pdfs, (default "stack_")
        stack_size: int - Size of an individual stack, this can't be guarenteed, A variation
            of +1 may be observed to prevent creation of an unnecessarily small stack,
            stack size must be a multiple of 4 (default: 40)
        """
        self.progress_midpage_multi(output, **options).sync()

    @progress.runs_with_progress
    def progress_midpage_multi(
        self, output: str | Path | BinaryIO, *, progress: Progress = None, **options
    ) -> Progress:
        defaults = {
            "size": "A4",
            "margin": (0, 0, 0, 0),
            "ppi": 200,
            "rtl": False,
            "flip_even": False,
            "separate_stacks": False,
            "stack_prefix": "stack_",
            "stack_size": 40,
        }

        _set_defaults_and_check_unknown(options, defaults)

        if options["separate_stacks"]:
            Path(output).mkdir(parents=True, exist_ok=True)

        # Distribute the pages into stack ranges, also eliminating a last small stack
        decided_stack_ranges = []
        total_pages = len(self.renderer)
        progress.set_total(total_pages)
        progress.set_msg("Calculating stack sizes")
        stack_size = options["stack_size"]

        num_stacks = total_pages // stack_size
        extra_pages = total_pages % stack_size
        total_naming_digits = len(str(num_stacks))

        cur_st = 0
        for _ in range(num_stacks):
            if extra_pages > 0:
                decided_stack_ranges.append((cur_st, cur_st + stack_size + 4))
                extra_pages -= 4
                cur_st += stack_size + 4
            else:
                decided_stack_ranges.append((cur_st, cur_st + stack_size))
                cur_st += stack_size

        prev_progress = 0
        output_streams = (
            []
        )  # Used to save pdf results in memory if the pdf needs to be mergeed at the end

        for current_stack, current_stack_range in enumerate(decided_stack_ranges):
            progress.set_msg(f"Rendering stack {current_stack+1}")
            output_stream = io.BytesIO()
            press = Press(self.renderer, pages=range(*current_stack_range))
            progress_object = press.progress_midpage(
                output_stream,
                size=options["size"],
                margin=options["margin"],
                ppi=options["ppi"],
                rtl=options["rtl"],
                flip_even=options["flip_even"],
            )

            while not progress_object.completed:
                progress_object.check_fail()
                progress.set_progress(prev_progress + progress_object.progress)

            if options["separate_stacks"]:
                output_stream.seek(0)
                with open(
                    Path(output)
                    / (
                        options["stack_prefix"]
                        + str(current_stack + 1).rjust(total_naming_digits, "0")
                        + ".pdf"
                    ),
                    "wb",
                ) as fp:
                    shutil.copyfileobj(output_stream, fp)
                del output_stream  # To free up memory
            else:
                output_streams.append(output_stream)

            prev_progress += progress_object.progress

        if not options["separate_stacks"]:
            progress.set_msg("Merging stacks into one document")
            new_pdf = pymupdf.Document()
            for i, x in enumerate(output_streams):
                x.seek(0)
                new_pdf.insert_pdf(pymupdf.Document(stream=x, filetype="pdf"))
                del output_streams[i]
            new_pdf.ez_save(output)

    def midpage(self, output: str | Path | BinaryIO, **options) -> None:
        """
        output: str, io_stream - output pdf file path (should contain suffix .pdf)

        options:
        size: str, tuple[float, float] - Page Size (name or ratio (w/h), width in inches)
        margin: tuple[top, outer, bottom, inner], give upto 4 parameters, default: all is 0
        ppi: int - Pixels per inch (default: 200)

        rtl: bool - Right to left
        flip_even: bool - Flip even pages horizontally by rotating them 180 degrees
        """
        self.progress_midpage(output, **options).sync()

    @progress.runs_with_progress
    def progress_midpage(
        self, output: str | Path | BinaryIO, *, progress: Progress = None, **options
    ) -> Progress:
        defaults = {
            "size": "A4",
            "margin": (0, 0, 0, 0),
            "ppi": 200,
            "rtl": False,
            "flip_even": False,
        }

        _set_defaults_and_check_unknown(options, defaults)

        # Get binded page order
        page_order = _flatten(
            bindermath.doubleside_singlestack_midpage(len(self.renderer))
        )

        total_pages = len(self.renderer)

        progress.set_total(
            len(self.renderer) + (len(page_order) // 2 if options["flip_even"] else 0)
        )
        progress.set_msg("Rendering input files to midpage binded PDF")

        # Setup margins
        margin = list(options["margin"])
        if len(margin) == 1:  # In case only one argument is provided
            margin.append(margin[0])
        if len(margin) == 2:  # In case 2 arguments are provided
            margin.append(margin[0])
        if len(margin) == 3:  # In case 3 arguments are provided
            margin.append(margin[1])

        # Get the page sizing
        p_size = options["size"]
        if isinstance(p_size, str):
            p_size = pages.get_ratio_width(p_size)

        # Get a page size based on pdf standards involving 72 points per inch
        p_size = pages.get_pixels_from_ppi(*p_size)
        half_page_size = (p_size[1] / 2, p_size[0])

        working_space_half_page = (  # Image rendering size in 72ppi
            half_page_size[0] - margin[1] - margin[3],
            half_page_size[1] - margin[0] - margin[2],
        )

        ppi_scale_factor = options["ppi"] / 72

        working_space_half_page_ppi_scaled = (
            working_space_half_page[0] * ppi_scale_factor,
            working_space_half_page[1] * ppi_scale_factor,
        )

        new_file = pymupdf.Document()

        for top_page, bottom_page in page_order:
            page = new_file.new_page(width=p_size[0], height=p_size[1])

            if top_page < total_pages:

                top_page_pixmap = self.renderer.render(
                    top_page, working_space_half_page_ppi_scaled
                )

                # I have no clue how I wrote this, but it works, so don't mess with this
                size = (top_page_pixmap.w, top_page_pixmap.h)
                clipped_size = pages.clip(size, working_space_half_page)
                position_left = (
                    margin[1] + (working_space_half_page[0] - clipped_size[0]) / 2
                )
                position_bottom = (
                    margin[2] + (working_space_half_page[1] - clipped_size[1]) / 2
                )
                r = (position_bottom, position_left)
                r += (
                    clipped_size[1] + position_bottom,
                    clipped_size[0] + position_left,
                )

                page.insert_image(
                    r, pixmap=top_page_pixmap, rotate=-90 if not options["rtl"] else 90
                )

                progress.increment_progress()

            if bottom_page < total_pages:
                bottom_page_pixmap = self.renderer.render(
                    bottom_page, working_space_half_page_ppi_scaled
                )

                # I have no clue how I wrote this, but it works, so don't mess with this
                size = (bottom_page_pixmap.w, bottom_page_pixmap.h)
                clipped_size = pages.clip(size, working_space_half_page)
                position_left = (
                    half_page_size[0]
                    + margin[3]
                    + (working_space_half_page[0] - clipped_size[0]) / 2
                )
                position_bottom = (
                    margin[2] + (working_space_half_page[1] - clipped_size[1]) / 2
                )
                r = (position_bottom, position_left)
                r += (
                    clipped_size[1] + position_bottom,
                    clipped_size[0] + position_left,
                )

                page.insert_image(
                    r,
                    pixmap=bottom_page_pixmap,
                    rotate=-90 if not options["rtl"] else 90,
                )

                progress.increment_progress()

        if options["flip_even"]:
            progress.set_msg("Flipping even pages")
            for i, x in enumerate(new_file):
                if i % 2 == 1:
                    x.set_rotation(180)
                    progress.increment_progress()

        progress.set_msg("Saving output to PDF")
        new_file.ez_save(output)

    def merge(self, output: str | Path | BinaryIO, **options) -> None:
        """
        output: str, io_stream - output pdf file path (should contain suffix .pdf)

        options:
        resolution: (w, h) - Max resolution in either dimensions, default: (1600, 1600)
        """
        self.progress_merge(output, **options).sync()

    @progress.runs_with_progress
    def progress_merge(
        self, output: str | Path | BinaryIO, *, progress: Progress = None, **options
    ) -> Progress:
        defaults = {"resolution": (1600, 1600)}
        _set_defaults_and_check_unknown(options, defaults)

        resolution = options["resolution"]

        new_file = pymupdf.Document()
        progress.set_total(len(self.renderer))
        progress.set_msg("Rendering and Merging input files to PDF")

        for x in range(len(self.renderer)):
            pixmap = self.renderer.render(page=x, size=resolution)

            page = new_file.new_page(width=pixmap.width, height=pixmap.height)
            page.insert_image((0, 0, pixmap.width, pixmap.height), pixmap=pixmap)
            progress.increment_progress()

        progress.set_msg("Saving output")
        new_file.ez_save(output)

    def images(self, output: str | Path, **options) -> None:
        """
        output: output_folder

        options:
        file_prefix: str - Defaults to nothing
        resolution: (w, h) - Max resolution in either dimension
        format: str - "png", "jpg", other formats are saved using pil (default: png)
        pil_*: options to pass to PIL saver
        """
        self.progress_images(output, **options).sync()

    @progress.runs_with_progress
    def progress_images(
        self, output: str | Path, *, progress: Progress = None, **options
    ) -> Progress:
        path = Path(output)
        path.mkdir(exist_ok=True)

        defaults = {
            "file_prefix": "",
            "resolution": (1600, 1600),
            "format": "png",
        }
        _set_defaults_and_check_unknown(options, defaults, ignore_prefix=("pil_",))

        format = options["format"]
        file_prefix = options["file_prefix"]
        resolution = options["resolution"]

        # Some python-fu to select pil_ arguments and remove the pil_ prefix
        pil_params = dict(
            map(
                lambda x: (x[0].removeprefix("pil_"), x[1]),
                filter(lambda x: x[0].startswith("pil_"), options.items()),
            )
        )

        progress.set_total(len(self.renderer))
        progress.set_msg("Rendering input files to images")

        for x in range(len(self.renderer)):
            pixmap = self.renderer.render(page=x, size=resolution)
            if format in ("png",):
                pixmap.save(path / f"{file_prefix}{x+1}.{format}", format)
            else:
                pixmap.pil_save(
                    path / f"{file_prefix}{x+1}.{format}", format, **pil_params
                )

            progress.increment_progress()

    def text(self) -> list[str]:
        """
        Extracts text from given files (Some file formats may not support this feature) and
        returns it as a list of strings. the index in the returned list corresponds to page.
        """
        return self.progress_text().sync()

    @progress.runs_with_progress
    def progress_text(self, *, progress: Progress = None) -> Progress:
        progress.set_total(len(self.renderer))
        progress.set_msg("Extracting text from given input files")
        all_txt = []

        for x in range(len(self.renderer)):
            txt = self.renderer.get_text(x)
            all_txt.append(txt)
            progress.increment_progress()

        return all_txt
