from argparse import ArgumentParser
import sys
import mimetypes

from . import errors
from . import pdfbinder

def run(args: list = None):
    if args is None:
        args = sys.argv[1:]
    
    parser = ArgumentParser("homepress_cli", description="A Command Line interface providing complete and full access to the homepress api")
    parser.add_argument("input_file", help="Input File in any of the supported formats (PDF, )")
    subcommands = parser.add_subparsers(title="Binding Types", dest="_bindtype")
    
    midpage_parser = subcommands.add_parser("midpage", help="Middle page binded books are a stack of sheets ordered in a way that when folded from the middle and binded there produce a perfectly ordered book")
    midpage_parser.add_argument("output", nargs="+", action="append")
    midpage_parser.add_argument("-ss", "--single-sided", action="store_true", help="By defeault, False. For whatever weird reason you might not \
want a double sided print. In that case use this flag. I recommend you to never touch this. Infact, \
even if you have a single sided printer don't change this parameter. This program was meant to be used \
for all printers even single sided so you dont worry about this parameter. In almost 99%% cases you \
can ignore this safely.")
    midpage_parser.add_argument("-rtl", "--right-to-left", action="store_true", help="By default, False. For certain languages and countries it is \
more conventional for the print to be right to left instead of the more popular left to right. Medias like \
manga books or even arabic books are traditionally printed right to left.")
    midpage_parser.add_argument('-f', "--flip-even", action="store_true", help="if set to true the resulting output has even \
pages flipped horizontally. It is recommended to enable this in case you are printing using a printer \
that supports double side printing without needing manual flipping of pages. If you are using a single \
side printer, it is recommended that you leave this off. When printing using a single sided printer, \
print the odd pages first, after that. Flip the pages at the horizontal axis.")
    midpage_parser.add_argument("-s", "--separate-even-odd", action="store_true", help="if you need to separate the odd \
pages from even pages, please use this parameter. If you set it to True, the output parameter should \
provide 2 paths, first for odd page pdf and the second for even page pdf.")
    midpage_parser.add_argument('-q', '--quite', action="store_true", help="When set to true, nothing is outputted to terminal.")

    args = parser.parse_args(args)

    file_mime = mimetypes.guess_type(args.input_file, strict=False)[0]
    if file_mime == "application/pdf":
        if args._bindtype == "midpage":
            args.output = args.output[0]
            pdfbinder.single_stack_midpage(
                inputfile=args.input_file,
                outputfile=args.output[0] if len(args.output) == 1 else (args.output[0], args.output[1]),
                flip_even=args.flip_even,
                right_to_left=args.right_to_left,
                separate_even_odd_output=args.separate_even_odd,
                single_sided=args.single_sided,
                progressbar=not args.quite,
            )

        else:
            raise errors.CLIUnknownBindType(f"{args._bindtype} not known bind format for PDF inputs")
    else:
        raise errors.UnknownInputFormat(f"{args.input_file} ({file_mime}) is an unknown/unsupported file format")

