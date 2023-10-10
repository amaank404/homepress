"""
Contains all the page order and numbering algorithms for binding
"""

from typing import Tuple, List, Union

PageIndexType = int

def doubleside_singlestack_midpage(numpages) -> List[Tuple[Tuple[PageIndexType, PageIndexType], Tuple[PageIndexType, PageIndexType]]]:
    out = []
    if numpages % 4 != 0:  # Ceil it with 4 as whole steps. Make it all a multiple of 4
        numpages += 4-(numpages%4)
    lastpage = numpages-1
    startpage = 0
    while startpage < lastpage:
        out.append(((lastpage, startpage), (startpage+1, lastpage-1)))
        lastpage -= 2
        startpage += 2
    return out

def singleside_singlestack_midpage(numpages) -> List[Tuple[PageIndexType, PageIndexType]]:
    out = []
    if numpages % 2 != 0:  # Ceil it with 2 as whole steps. Make it all a multiple of 2
        numpages += 1
    lastpage = numpages-1
    startpage = 0
    while startpage < lastpage:
        out.append((startpage, lastpage))
        lastpage -= 1
        startpage += 1
    return out
