RATIOS: dict[str, float] = {
    "A4": 1 / 2**0.5,  # Also applicable for other series
    "Letter": 8.5 / 11,
    "Legal": 8.5 / 14,
    "Ledger": 11 / 17,
}

# inches
REAL_WIDTH: dict[str, float] = {"A4": 8.3, "Letter": 8.5, "Legal": 8.5, "Ledger": 11}


def get_ratio_width(name: str) -> tuple[float, float]:
    return (RATIOS[name], REAL_WIDTH[name])


def get_half_ratio(ratio: float) -> float:
    """
    get ratio for half page
    """
    return 2 / ratio


def get_pixels_from_ppi(
    ratio: float, width: float, ppi: float = 72
) -> tuple[float, float]:
    h = 1 / ratio * width * ppi
    w = width * ppi
    return (w, h)


def clip(page: tuple[float, float], box: tuple[float, float]) -> tuple[float, float]:
    """
    Clip a page to given box
    """
    # If page height is dimensionally greater than box height,
    # clip wrt to height
    if page[1] / page[0] >= box[1] / box[0]:
        new_h = box[1]
        new_w = (page[0] / page[1]) * box[1]
    else:  # clip to width
        new_w = box[0]
        new_h = (page[1] / page[0]) * box[0]
    return (new_w, new_h)
