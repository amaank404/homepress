"""
Takes PDF as an input and converts it into another
PDF that is ready for printing. There are several
types of binding available as follows:

1. Single Stack Middle Page Binding
The resulting pdf is to be printed and bound at the middle
of the sheets by either staple pins or other threading methods.
This method is the best for a relatively thin book. For a more
heavy book, please consider Multi Stack Middle Page binding.

If you intend to print single sided, please specify that
in the arguments.
"""

import pypdf
from . import bindermath
from tqdm import tqdm
from typing import Union, Tuple

def single_stack_midpage(inputfile: str, outputfile: Union[str, Tuple[str, str]], flip_even: bool = False, right_to_left: bool = False, single_sided: bool = False, separate_even_odd_output: bool = False, progressbar: bool = True):
    """
    Takes an input PDF file and outputs it. The output parameter is either a single path (a string object) or
    2 paths enclosed within a tuple. the 2 paths case is when you wish to separate even and odd outputs.

    flip_even parameter is a boolean value. By default, False. if set to true the resulting output has even
    pages flipped horizontally. It is recommended to enable this in case you are printing using a printer
    that supports double side printing without needing manual flipping of pages. If you are using a single
    side printer, it is recommended that you leave this off. When printing using a single sided printer,
    print the odd pages first, after that. Flip the pages at the horizontal axis. 

    right_to_left parameter is a boolean value. By default, False. For certain languages and countries it is
    more conventional for the print to be right to left instead of the more popular left to right. Medias like
    manga books or even arabic books are traditionally printed right to left.

    single_sided parameter is a boolean value. By defeault, False. For whatever weird reason you might not
    want a double sided print. In that case use this flag. I recommend you to never touch this. Infact,
    even if you have a single sided printer don't change this parameter. This program was meant to be used
    for all printers even single sided so you dont worry about this parameter. In almost 99% cases you
    can ignore this safely.

    separate_even_odd_output parameter is a boolean value. By default, False. if you need to separate the odd
    pages from even pages, please use this parameter. If you set it to True, the output parameter should
    provide 2 paths, first for odd page pdf and the second for even page pdf.

    progressbar is set to true by default. If you wish to hide progress from terminal output, please set it
    to False.
    """
    if separate_even_odd_output and not isinstance(outputfile, tuple):
        raise TypeError(f"Given output parameter is of wrong type, two paths are required. Given parameter value: {repr(outputfile)}")

    reader = pypdf.PdfReader(inputfile)
    writer = pypdf.PdfWriter()
    totalpages = len(reader.pages)
    
    # Get median page sorted by size
    dimensions = []
    for i, x in enumerate(reader.pages):
        dimensions.append((i, 
            x.cropbox.width *
            x.cropbox.height
        ))
    dimensions.sort(key=lambda x: x[1])
    pid = dimensions[len(dimensions)//2][0]
    del dimensions

    # Get the median page individual dimensions
    medpagedims = reader.pages[pid].cropbox
    perpagedimensions = (medpagedims.height, medpagedims.width*2)


    # Start the output binding process
    if not single_sided:
        pageorder = bindermath.doubleside_singlestack_midpage(totalpages)
        pageorderflattened = []
        for x in pageorder:
            pageorderflattened.extend(x)

        if progressbar:
            iterobj = tqdm(pageorderflattened)
        else:
            iterobj = pageorderflattened

        for (pagetop, pagebottom) in iterobj:
            writer.add_blank_page(perpagedimensions[0], perpagedimensions[1])
            if pagetop < totalpages:
                paget = reader.pages[pagetop]
                paget = paget.rotate(90 if not right_to_left else 270)
                paget.transfer_rotation_to_content()
                writer.pages[-1].merge_translated_page(paget, -medpagedims.bottom, medpagedims.width-medpagedims.left)
            if pagebottom < totalpages:
                pageb = reader.pages[pagebottom]
                pageb = pageb.rotate(90 if not right_to_left else 270)
                pageb.transfer_rotation_to_content()
                writer.pages[-1].merge_translated_page(pageb, -medpagedims.bottom, -medpagedims.left)
        
        if flip_even:
            if progressbar:
                iterobj = tqdm(range(1, len(writer.pages), 2))
            else:
                iterobj = range(1, len(writer.pages), 2)
            for x in iterobj:
                writer.pages[x] = writer.pages[x].rotate(180)
                writer.pages[x].transfer_rotation_to_content()
        if separate_even_odd_output:
            writer_odd = pypdf.PdfWriter()
            writer_even = pypdf.PdfWriter()
            for x, page in enumerate(writer.pages):
                if x % 2 == 0:
                    writer_odd.add_page(page)
                else:
                    writer_even.add_page(page)
            writer_odd.write(outputfile[0])
            writer_even.write(outputfile[1])
        else:
            writer.write(outputfile)
    else:
        pageorderflattened = bindermath.singleside_singlestack_midpage(totalpages)
        
        if progressbar:
            iterobj = tqdm(pageorderflattened)
        else:
            iterobj = pageorderflattened
        
        for (pagetop, pagebottom) in iterobj:
            writer.add_blank_page(perpagedimensions[0], perpagedimensions[1])
            if pagetop < totalpages:
                paget = reader.pages[pagetop]
                paget = paget.rotate(90 if not right_to_left else 270)
                paget.transfer_rotation_to_content()
                writer.pages[-1].merge_translated_page(paget, -medpagedims.bottom, medpagedims.width-medpagedims.left)
            if pagebottom < totalpages:
                pageb = reader.pages[pagebottom]
                pageb = pageb.rotate(90 if not right_to_left else 270)
                pageb.transfer_rotation_to_content()
                writer.pages[-1].merge_translated_page(pageb, -medpagedims.bottom, -medpagedims.left)
        writer.write(outputfile)
