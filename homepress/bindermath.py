"""
Contains all the page order and numbering algorithms for binding
"""

type PageIndexType = int


def doubleside_singlestack_midpage(
    numpages: int,
) -> list[
    tuple[tuple[PageIndexType, PageIndexType], tuple[PageIndexType, PageIndexType]]
]:
    out = []
    if numpages % 4 != 0:  # Ceil it with 4 as whole steps. Make it all a multiple of 4
        numpages += 4 - (numpages % 4)
    lastpage = numpages - 1
    startpage = 0
    while startpage < lastpage:
        out.append(((lastpage, startpage), (startpage + 1, lastpage - 1)))
        lastpage -= 2
        startpage += 2
    return out
