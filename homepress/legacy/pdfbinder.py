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

2. Multi Stack Middle Page Binding
Similar to Single Stack Middle Page Binding and produces output
in several stacks instead, so that binding can be done in batches
instead of binding the whole book at once. (This is used for binding/printing
thick books sometimes)
"""

import pypdf
from .. import bindermath
from tqdm import tqdm
import os
from typing import Union, Tuple
from copy import deepcopy

def multi_stack_midpage(inputfile: str, outputfile: Union[str, Tuple[str, str]], flip_even: bool = False, right_to_left: bool = False, separate_even_odd_output: bool = False, progressbar: bool = True, separate_stacks: bool = False, stack_size: int = 40):
    """
    Takes an input PDF file and outputs it. The output parameter is either a single path to a file/folder or
    2 paths to files/folders enclosed within a tuple. The 2 paths case is when you wish to separate even and odd
    outputs. The folder is the case when you wish to separate stacks.

    flip_even parameter is a boolean value. By default, False. if set to true the resulting output has even
    pages flipped horizontally. It is recommended to enable this in case you are printing using a printer
    that supports double side printing without needing manual flipping of pages. If you are using a single
    side printer, it is recommended that you leave this off. When printing using a single sided printer,
    print the odd pages first, after that. Flip the pages at the horizontal axis. 

    right_to_left parameter is a boolean value. By default, False. For certain languages and countries it is
    more conventional for the print to be right to left instead of the more popular left to right. Medias like
    manga books or even arabic books are traditionally printed right to left.

    separate_even_odd_output parameter is a boolean value. By default, False. if you need to separate the odd
    pages from even pages, please use this parameter. If you set it to True, the output parameter should
    provide 2 paths, first for odd page pdf and the second for even page pdf.

    progressbar is set to true by default. If you wish to hide progress from terminal output, please set it
    to False.

    separate_stacks is a boolean value. By default, False. When this feature is used, the output parameters
    provided should be to a folder instead of files. These folders will contain multiple pdf files going by the
    name: "stack_1.pdf", "stack_2.pdf" etc... The names might also become "stack_001.pdf" in case there are over 1000 stacks. Hence, the numbering
    is always index aligned with the higher place value being relatively left.

    stack_size is the size of individual stack. it can't be guarenteed that this will remain this way
    for all the stacks. variation of +1 in the stack size for some pdfs may happen as a result of eliminating last
    small stack. STACK_SIZE must be a multiple of 4
    """
    if stack_size % 4 != 0:
        raise ValueError("Stack size must be a multiple of 4. ie stack_size % 4 == 0")
    
    reader = pypdf.PdfReader(inputfile)
    decided_stack_ranges = []
    num_stacks = len(reader.pages)//stack_size
    extra_pages = len(reader.pages)%stack_size
    total_naming_digits = len(str(num_stacks))

    print(f"Total Stacks: {num_stacks}")

    cur_st = 0
    for x in range(num_stacks):
        if extra_pages > 0:
            decided_stack_ranges.append((cur_st, cur_st+stack_size+ 4))
            extra_pages -= 4
            cur_st += stack_size+4
        else:
            decided_stack_ranges.append((cur_st, cur_st+stack_size))
            cur_st += stack_size

    # Precalculate dimensions per page
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
    medpagedims = deepcopy(reader.pages[pid].cropbox)
    perpagedimensions = (medpagedims.height, medpagedims.width*2)
    
    if not separate_stacks:
        if separate_even_odd_output:
            writer_odd = pypdf.PdfWriter()
            writer_even = pypdf.PdfReader()
        else:
            writer = pypdf.PdfWriter()
    else:
        if separate_even_odd_output:
            os.makedirs(outputfile[0], exist_ok=True)
            os.makedirs(outputfile[1], exist_ok=True)
        else:
            os.makedirs(outputfile, exist_ok=True)


    for current_stack, current_stack_range in enumerate(decided_stack_ranges):
        if progressbar:
            print("\nProcessing Stack: ", current_stack+1)
        output = single_stack_midpage(inputfile=reader, outputfile=None, flip_even=flip_even, right_to_left=right_to_left, single_sided=False, separate_even_odd_output=separate_even_odd_output, progressbar=progressbar, input_page_range=current_stack_range, _dinput=True, _doutput=True, _predims=perpagedimensions, _prerectobj=medpagedims)
        if separate_stacks:
            if separate_even_odd_output:
                output[0].write(os.path.join(outputfile[0], f"stack_{str(current_stack+1).rjust(total_naming_digits, '0')}.pdf"))
                output[1].write(os.path.join(outputfile[1], f"stack_{str(current_stack+1).rjust(total_naming_digits, '0')}.pdf"))
            else:
                output.write(os.path.join(outputfile, f"stack_{str(current_stack+1).rjust(total_naming_digits, '0')}.pdf"))
        else:
            if separate_even_odd_output:
                for page in output[0].pages: # Odd
                    writer_odd.add_page(page)
                for page in output[1].pages: # Even
                    writer_even.add_page(page)
            else:
                for page in output.pages:
                    writer.add_page(page)
    
    if not separate_stacks:
        if separate_even_odd_output:
            writer_odd.write(outputfile[0])
            writer_even.write(outputfile[1])
        else:
            writer.write(outputfile)       


def single_stack_midpage(inputfile: str, outputfile: Union[str, Tuple[str, str]], flip_even: bool = False, right_to_left: bool = False, single_sided: bool = False, separate_even_odd_output: bool = False, progressbar: bool = True, input_page_range: Tuple[int, int] = None, _dinput=False, _doutput=False, _predims=None, _prerectobj=None):
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
    can ignore this safely. also, most of these features wont work if you do enable this flag for some weird reason

    separate_even_odd_output parameter is a boolean value. By default, False. if you need to separate the odd
    pages from even pages, please use this parameter. If you set it to True, the output parameter should
    provide 2 paths, first for odd page pdf and the second for even page pdf.

    progressbar is set to true by default. If you wish to hide progress from terminal output, please set it
    to False.

    input_page_range is a tuple value with two integers. By default is set to None, when None, it implies that
    the whole document is to be processed. When 2 integers are provided in a tuple, the first integer is the starting
    index inclusive and the second integer is the end index exclusive. Meaning this works just like slicing/range funcion.
    NEGATIVE INDEXIN WILL RAISE WEIRD ERRORS. DONT DO NEGATIVE INDEXING.

    also for developers: you may use the flags: _dinput/_doutput for direct input output of pypdf objects. _dinput
    takes the reader instance from inputfile parameter directly. _doutput only returns the values, _doutput would
    completely ignore paths provided in the outputfile parameter. _predims,_prerectobj should not be used by external developers.
    do note that this function modifies input pdf object, MODIFIES OBJECT, not source file. 
    """
    if separate_even_odd_output and not isinstance(outputfile, tuple) and not _dinput:
        raise TypeError(f"Given output parameter is of wrong type, two paths are required. Given parameter value: {repr(outputfile)}")

    if not _dinput:
        reader = pypdf.PdfReader(inputfile)
    else:
        reader = inputfile
    writer = pypdf.PdfWriter()
    totalpages = len(reader.pages)
    
    # Get median page sorted by size
    if _predims is None:
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
    else:
        medpagedims = _prerectobj
        perpagedimensions = _predims


    # Start the output binding process
    if not single_sided:
        if input_page_range is None:
            pageorder = bindermath.doubleside_singlestack_midpage(totalpages)
        else:
            number_pages = input_page_range[1] - input_page_range[0]
            pageorder = bindermath.doubleside_singlestack_midpage(number_pages)

        if input_page_range is not None:
            _start = input_page_range[0]
            _end = input_page_range[1]
        pageorderflattened = []
        for x in pageorder:
            if input_page_range is None:
                pageorderflattened.extend(x)
            else:  # Offset the page numbers to meet start
                _p1 = [x[0][0]+_start, x[0][1]+_start]
                _p2 = [x[1][0]+_start, x[1][1]+_start]

                # This weird looking thing below makes sure that the pages are overflowed so that they are not in output if the said page exceeds end limits
                if _p1[0] >= _end:
                    _p1[0] = totalpages
                if _p1[1] >= _end:
                    _p1[1] = totalpages
                if _p2[0] >= _end:
                    _p2[0] = totalpages
                if _p2[1] >= _end:
                    _p2[1] = totalpages

                pageorderflattened.append(_p1)
                pageorderflattened.append(_p2)

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
                iterobj = tqdm(range(len(writer.pages)))
            else:
                iterobj = range(len(writer.pages))

            nw = pypdf.PdfWriter()
            for x in iterobj:
                if x % 2 == 1:
                    page = writer.pages[x].rotate(180)
                    page.transfer_rotation_to_content()
                    nw.add_page(page)
                else:
                    nw.add_page(writer.pages[x])
            writer = nw
        if separate_even_odd_output:
            writer_odd = pypdf.PdfWriter()
            writer_even = pypdf.PdfWriter()
            for x, page in enumerate(writer.pages):
                if x % 2 == 0:
                    writer_odd.add_page(page)
                else:
                    writer_even.add_page(page)
            if _doutput:
                return (writer_odd, writer_even)
            else:
                writer_odd.write(outputfile[0])
                writer_even.write(outputfile[1])
        else:
            if _doutput:
                return writer
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

        if _doutput:
            return writer
        else:
            writer.write(outputfile)
