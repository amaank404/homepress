import mimetypes
import sys
from argparse import ArgumentParser

from . import errors, pdfbinder


def run(args: list = None):
    if args is None:
        args = sys.argv[1:]

    parser = ArgumentParser(
        "homepress_cli",
        description="A Command Line interface providing complete and full access to the homepress api",
    )
    parser.add_argument(
        "input_file", help="Input File in any of the supported formats (PDF, )"
    )
    subcommands = parser.add_subparsers(title="Binding Types", dest="_bindtype")

    midpage_parser = subcommands.add_parser(
        "midpage",
        help="Middle page binded books are a stack of sheets ordered in a way that when folded from the middle and binded there produce a perfectly ordered book",
    )
    midpage_parser.add_argument("output", nargs="+", action="append")
    midpage_parser.add_argument(
        "-ss",
        "--single-sided",
        action="store_true",
        help="By defeault, False. For whatever weird reason you might not \
want a double sided print. In that case use this flag. I recommend you to never touch this. Infact, \
even if you have a single sided printer don't change this parameter. This program was meant to be used \
for all printers even single sided so you dont worry about this parameter. In almost 99%% cases you \
can ignore this safely. also, most of these features wont work if you do enable this flag for some weird reason",
    )
    midpage_parser.add_argument(
        "-rtl",
        "--right-to-left",
        action="store_true",
        help="By default, False. For certain languages and countries it is \
more conventional for the print to be right to left instead of the more popular left to right. Medias like \
manga books or even arabic books are traditionally printed right to left.",
    )
    midpage_parser.add_argument(
        "-f",
        "--flip-even",
        action="store_true",
        help="if set to true the resulting output has even \
pages flipped horizontally. It is recommended to enable this in case you are printing using a printer \
that supports double side printing without needing manual flipping of pages. If you are using a single \
side printer, it is recommended that you leave this off. When printing using a single sided printer, \
print the odd pages first, after that. Flip the pages at the horizontal axis.",
    )
    midpage_parser.add_argument(
        "-s",
        "--separate-even-odd",
        action="store_true",
        help="if you need to separate the odd \
pages from even pages, please use this parameter. If you set it to True, the output parameter should \
provide 2 paths, first for odd page pdf and the second for even page pdf.",
    )
    midpage_parser.add_argument(
        "-ipr",
        "--input-page-range",
        action="store",
        default=None,
        type=lambda x: tuple(map(int, x.split(","))),
        help='input_page_range is a tuple value with two integers. By default is set to None, when None, it implies that \
the whole document is to be processed. When 2 integers are provided in a tuple, the first integer is the starting \
index inclusive and the second integer is the end index exclusive. Meaning this works just like slicing/range funcion. \
NEGATIVE INDEXIN WILL RAISE WEIRD ERRORS. DONT DO NEGATIVE INDEXING. \
The format for this argument is: int,int. For example: "-ipr 120,125"',
    )
    midpage_parser.add_argument(
        "-q",
        "--quite",
        action="store_true",
        help="When set to true, nothing is outputted to terminal.",
    )

    midpage_multi_parser = subcommands.add_parser(
        "midpage-multi",
        help="Middle page binded books are a stack of sheets ordered in a way that when folded from the middle and binded there produce a perfectly ordered book. Multi stack binding spits out multiple stacks instead of single stack. This is quite usefull for books with higher number of pages.",
    )
    midpage_multi_parser.add_argument("output", nargs="+", action="append")
    midpage_multi_parser.add_argument(
        "-rtl",
        "--right-to-left",
        action="store_true",
        help="By default, False. For certain languages and countries it is \
more conventional for the print to be right to left instead of the more popular left to right. Medias like \
manga books or even arabic books are traditionally printed right to left.",
    )
    midpage_multi_parser.add_argument(
        "-f",
        "--flip-even",
        action="store_true",
        help="if set to true the resulting output has even \
pages flipped horizontally. It is recommended to enable this in case you are printing using a printer \
that supports double side printing without needing manual flipping of pages. If you are using a single \
side printer, it is recommended that you leave this off. When printing using a single sided printer, \
print the odd pages first, after that. Flip the pages at the horizontal axis.",
    )
    midpage_multi_parser.add_argument(
        "-s",
        "--separate-even-odd",
        action="store_true",
        help="if you need to separate the odd \
pages from even pages, please use this parameter. If you set it to True, the output parameter should \
provide 2 paths, first for odd page pdf and the second for even page pdf.",
    )
    midpage_multi_parser.add_argument(
        "-ss",
        "--stack-size",
        action="store",
        type=int,
        help="stack_size is the size of individual stack. it can't be guarenteed that this will remain this way \
for all the stacks. variation of +1 in the stack size for some pdfs may happen as a result of eliminating last \
small stack. STACK_SIZE must be a multiple of 4. An integer must be provided",
        default=40,
    )
    midpage_multi_parser.add_argument(
        "-sst",
        "--separate-stacks",
        action="store_true",
        help='separate_stacks is a boolean value. By default, False. When this feature is used, the output parameters \
provided should be to a folder instead of files. These folders will contain multiple pdf files going by the \
name: "stack_1.pdf", "stack_2.pdf" etc... The names might also become "stack_001.pdf" in case there are over 1000 stacks. Hence, the numbering \
is always index aligned with the higher place value being relatively left.',
    )
    midpage_multi_parser.add_argument(
        "-q",
        "--quite",
        action="store_true",
        help="When set to true, nothing is outputted to terminal.",
    )

    args = parser.parse_args(args)

    file_mime = mimetypes.guess_type(args.input_file, strict=False)[0]
    if file_mime == "application/pdf":
        if args._bindtype == "midpage":
            args.output = args.output[0]
            pdfbinder.single_stack_midpage(
                inputfile=args.input_file,
                outputfile=(
                    args.output[0]
                    if len(args.output) == 1
                    else (args.output[0], args.output[1])
                ),
                flip_even=args.flip_even,
                right_to_left=args.right_to_left,
                separate_even_odd_output=args.separate_even_odd,
                single_sided=args.single_sided,
                progressbar=not args.quite,
                input_page_range=args.input_page_range,
            )
        elif args._bindtype == "midpage-multi":
            args.output = args.output[0]
            pdfbinder.multi_stack_midpage(
                inputfile=args.input_file,
                outputfile=(
                    args.output[0]
                    if len(args.output) == 1
                    else (args.output[0], args.output[1])
                ),
                flip_even=args.flip_even,
                right_to_left=args.right_to_left,
                separate_even_odd_output=args.separate_even_odd,
                stack_size=args.stack_size,
                separate_stacks=args.separate_stacks,
                progressbar=not args.quite,
            )
        else:
            raise errors.CLIUnknownBindType(
                f"{args._bindtype} not known bind format for PDF inputs"
            )
    else:
        raise errors.UnknownInputFormat(
            f"{args.input_file} ({file_mime}) is an unknown/unsupported file format"
        )
