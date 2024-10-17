import json
import sys
import textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import Sized, SupportsIndex

from . import Press, __homepage__, __version__, layout, renderer


def get_formats() -> str:
    CHUNK_SIZE = 10
    ret = ""
    formats = list(renderer.formats)
    formats.sort()
    for x in range(0, len(formats), CHUNK_SIZE):
        ret += " ".join(formats[x : x + CHUNK_SIZE]) + "\n"
    return ret[:-1]


def page_size(v: str) -> str | tuple[float, float]:
    if v in layout.pages.RATIOS:
        return v

    t = tuple(map(float, v.split(",")))
    if len(t) == 2:
        return t

    raise TypeError(
        f"Given argument is not a correct value for size, `{v}` was provided"
    )


def resolution(v: str) -> tuple[float, float]:
    t = tuple(map(float, v.split(",")))
    if len(t) == 2:
        return t
    raise TypeError(
        f"Given resolution should provide two values, `{v}` is not a valid resolution specifier"
    )


def page_ranges(v: str) -> list[int | SupportsIndex]:
    pages = []
    a = v.split(",")
    for x in a:
        try:
            pages.append(int(x))
        except:
            pages.append(range(*map(int, x.split("-"))))
    return pages


def minlen1input(v: Sized) -> Sized:
    if len(v) >= 1:
        return v
    raise TypeError("Atleast one input file is required")


def pil_arg(v: str) -> tuple[str, int | float | dict | list | str]:
    k, v = v.split("=", 1)
    try:
        v = int(v)
        return k, v
    except:
        pass

    try:
        v = float(v)
        return k, v
    except:
        pass

    try:
        v = json.loads(v.replace("'", '"'))
        return k, v
    except:
        pass

    return k, v


def app(args=None) -> None:
    if not args:
        args = sys.argv[1:]

    parser = ArgumentParser(
        "homepress",
        description=f"""
Homepress (v{__version__})

Homepress is a printing-targeted utility that works with multiple input
formats and can perform various different changes on such inputs. This
can range anywhere from printing small booklets to printing large books.
For more information, please check out the project's homepage at

    {__homepage__}

Following input file formats are supported:
{textwrap.indent(get_formats(), '    ')}

The input files are rendered into image files and thus, this program is memory
intensive.
""",
        formatter_class=RawDescriptionHelpFormatter,
        epilog="Hope you have a great day!",
    )

    # Root parser options
    parser.add_argument(
        "-v", "--version", version="Homepress v" + __version__, action="version"
    )

    grp = parser.add_mutually_exclusive_group()
    grp.add_argument(
        "--formats", help="prints a list of available formats", action="store_true"
    )
    grp.add_argument(
        "--page-sizes",
        help="prints a list of available named page sizes",
        action="store_true",
    )

    # Subparsers at root level
    subparser = parser.add_subparsers(dest="_root_command", metavar="root_commands")
    subparser_press = subparser.add_parser("press", help="the default press")
    subparser_press.add_argument(
        "-i",
        "--input",
        help="add multiple input files by repeating this parameter, may also be a folder containing files, run `homepress --help` for a list of supported input file formats",
        action="append",
        default=[],
    )
    subparser_press.add_argument(
        "--ignore-errors",
        help="ignores errors if any while reading the input files",
        action="store_true",
    )
    subparser_press.add_argument(
        "-p",
        "--pages",
        help="page range to take from the input, is a comma separated list defining page ranges example: 1,4,6-10,12  by default takes all the pages",
        default=None,
        type=page_ranges,
    )

    # Subparsers at `press`
    press_subparsers = subparser_press.add_subparsers(
        dest="_press_command", required=True, metavar="press_commands"
    )

    def midpage_common_options(parser: ArgumentParser):
        parser.add_argument(
            "-s",
            "--size",
            help=f"output document page size, defaults to 'A4', valid values can be {', '.join(layout.pages.RATIOS)} or a comma separated value defining 'w/h_ratio,width_in_inches'",
            type=page_size,
            default="A4",
        )
        parser.add_argument(
            "-m",
            "--margin",
            help=f"page margins defined by comma separated values in the format top,[outer,[bottom,[inner]]] where values within square brackets may be omitted. defaults to 0",
            default=[0],
            type=lambda x: tuple(map(float, x.split(","))),
        )
        parser.add_argument(
            "-p",
            "--ppi",
            help="pixel density defined as pixels per inch, defaults to 200",
            default=200,
            type=float,
        )
        parser.add_argument(
            "-r",
            "--rtl",
            help="output media's page direction is set to right to left with this option",
            action="store_true",
        )
        parser.add_argument(
            "-f",
            "--flip-even",
            help="flip even pages horizontally by rotating them 180 degrees",
            action="store_true",
        )

    # parser `press midpage`
    midpage_parser = press_subparsers.add_parser(
        "midpage",
        help="middle page binded books are a stack of sheets ordered in a way that when folded from the middle and binded there produce a perfectly ordered book",
    )
    midpage_parser.add_argument("output", help="path to output pdf file")
    midpage_common_options(midpage_parser)

    # parser `press midpage-multi`
    midpage_multi_parser = press_subparsers.add_parser(
        "midpage-multi",
        help="similar to midpage binding, except, the input is split into several stacks (suitable for binding large documents)",
    )
    midpage_multi_parser.add_argument(
        "output",
        help="path to output pdf file or a path to folder containing individual stack files if --separate_stacks is passed",
    )
    midpage_common_options(midpage_multi_parser)
    midpage_multi_parser.add_argument(
        "--separate-stacks",
        help="separate the stacks of the said document into separate pdf files stored in the `output` folder",
        action="store_true",
    )
    midpage_multi_parser.add_argument(
        "-sp",
        "--stack-prefix",
        help="use the said stack_prefix for the file names, by default `stack_`, this is followed by stack number",
        default="stack_",
    )
    midpage_multi_parser.add_argument(
        "-ss",
        "--stack-size",
        help="number of pages per stack, this may be increased by 1 to eliminate an ending smaller stack, defaults to 40",
        default=40,
    )

    # parser `press merge`
    merge_parser = press_subparsers.add_parser(
        "merge", help="renders and merges the input file to a pdf document"
    )
    merge_parser.add_argument("output", help="path to output pdf file")
    merge_parser.add_argument(
        "-r",
        "--resolution",
        help="resolution is a comma separated value resolution_x,resolution_y defining maximum resolution in pixels for their respective axis, defaults to 1600 in both directitons",
        type=resolution,
        default=(1600, 1600),
    )

    # parser `press images`
    image_parser = press_subparsers.add_parser(
        "images",
        help="renders and outputs the image files into a folder consisting of the images specified by format",
    )
    image_parser.add_argument("output", help="path to output folder")
    image_parser.add_argument(
        "-r",
        "--resolution",
        help="resolution is a comma separated value resolution_x,resolution_y defining maximum resolution in pixels for their respective axis, defaults to 1600 in both directitons",
        type=resolution,
        default=(1600, 1600),
    )
    image_parser.add_argument(
        "-f",
        "--file-prefix",
        help="file name prefix for the image files. defaults to nothing",
        default="",
    )
    image_parser.add_argument(
        "-fmt",
        "--format",
        help="image file format to use to save the image, 'png' is stored using pymupdf, other file formats are stored using PIL (Pillow), defaults to png",
        default="png",
    )
    image_parser.add_argument(
        "-p",
        "--pil",
        help="options to pass to pil saver, formatted as key=value, value is autoconverted to integer or float if the value is parsable as such",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        type=pil_arg,
    )

    # parser `press text`
    text_pareser = press_subparsers.add_parser(
        "text",
        help="extracts all the text from inputs supporting it and saves it to a text file",
    )
    text_pareser.add_argument(
        "output", help="path to a text file to store the text output"
    )

    args = parser.parse_args(args)
    if args.formats:
        print(" ".join(renderer.formats))
        return 0
    elif args.page_sizes:
        print(" ".join(layout.pages.RATIOS.keys()))
        return 0

    match args._root_command:
        case "press":
            minlen1input(args.input)
            press = Press(args.input, args.ignore_errors, args.pages)
            match args._press_command:
                case "midpage-multi":
                    press.progress_midpage_multi(
                        args.output,
                        size=args.size,
                        margin=args.margin,
                        ppi=args.ppi,
                        rtl=args.rtl,
                        flip_even=args.flip_even,
                        separate_stacks=args.separate_stacks,
                        stack_prefix=args.stack_prefix,
                        stack_size=args.stack_size,
                    ).sync_with_progress_bar()
                case "midpage":
                    press.progress_midpage(
                        args.output,
                        size=args.size,
                        margin=args.margin,
                        ppi=args.ppi,
                        rtl=args.rtl,
                        flip_even=args.flip_even,
                    ).sync_with_progress_bar()
                case "merge":
                    press.progress_merge(
                        args.output,
                        resolution=args.resolution,
                    ).sync_with_progress_bar()
                case "images":
                    press.progress_images(
                        args.output,
                        resolution=args.resolution,
                        file_prefix=args.file_prefix,
                        format=args.format,
                        **dict(args.pil),
                    ).sync_with_progress_bar()
                case "text":
                    text: list[str] = press.progress_text().sync_with_progress_bar()
                    text = "\n\n".join(text)
                    with open(args.output, "w") as fp:
                        fp.write(text)
                case _:
                    raise TypeError(f"Unknown press command")
        case _:
            parser.print_help()
            return 1
    return 0
