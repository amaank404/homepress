ratios = {
    "A4": 2**0.5,  # Also applicable for other series
    "Letter": 11/8.5,
    "Legal": 14/8.5,
    "Ledger": 17/11
}

# inches
real_width = {
    "A4": 8.3,
    "Letter": 8.5,
    "Legal": 8.5,
    "Ledger": 11
}

def get_ratio_width(name: str):
    return (ratios[name], real_width[name])

def get_half_ratio(ratio: float):
    """
    get ratio for half page
    """
    return 2/ratio

def get_pixels_from_ppi(ratio, width: float, ppi: float = 72):
    h = ratio*width*ppi
    w = width*ppi
    return (w, h)

def clip(page, box):
    # If page height is dimensionally greater than box height,
    # clip wrt to height
    if page[1]/page[0] >= box[1]/box[0]:
        new_h = box[1]
        new_w = (page[0]/page[1]) * box[1]
    else: # clip to width
        new_w = box[0]
        new_h = (page[1]/page[0]) * box[0]
    return (new_w, new_h)