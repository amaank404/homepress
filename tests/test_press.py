import logging
from pathlib import Path

import data
import pytest

import homepress.renderer
from homepress import Press


@pytest.fixture(
    scope="module",
    params=list(data.dataset.filter_extension_batched(homepress.renderer.formats, 10)),
)
def press_10(request):
    return Press(request.param)


@pytest.fixture(
    scope="module",
    params=list(data.dataset.filter_extension_batched(homepress.renderer.formats, 10)),
)
def press_30(request):
    return Press(request.param)


def test_press_text(press_10: Press):
    assert isinstance(press_10.text(), list)


def test_press_images_png(press_10: Press, tmpdir: Path):
    press_10.images(
        tmpdir, format="png", file_prefix="test_png_image", resolution=(64, 64)
    )


def test_press_images_webp(press_10: Press, tmpdir: Path):
    press_10.images(
        tmpdir, format="webp", file_prefix="test_webp_image", resolution=(64, 64)
    )


def test_merge(press_10: Press, tmpdir: Path):
    press_10.merge(tmpdir / "merge_test.pdf", resolution=(64, 64))


@pytest.mark.parametrize(
    "size,margin,ppi,rtl,flip_even",
    [
        ("A4", [0], 10, False, False),
        ("Legal", [2], 10, True, False),
        ("Ledger", [4, 3], 10, False, True),
        ("Letter", [0, 2, 3], 10, True, True),
        ((1 / 2, 5), [0, 4, 5, 6], 10, False, False),
    ],
)
def test_midpage(press_10: Press, tmpdir: Path, size, margin, ppi, rtl, flip_even):
    press_10.midpage(
        tmpdir / "midpage_test.pdf",
        size=size,
        margin=margin,
        ppi=ppi,
        rtl=rtl,
        flip_even=flip_even,
    )


@pytest.mark.parametrize(
    "size,margin,ppi,rtl,flip_even,separate_stacks,stack_prefix,stack_size",
    [
        ("A4", [0], 10, False, False, False, "stack_", 12),
        ("Legal", [2], 10, True, False, True, "stack_", 12),
        ("Ledger", [4, 3], 10, False, True, True, "st12_", 12),
        ("Letter", [0, 2, 3], 10, True, True, False, "", 16),
        ((1 / 2, 5), [0, 4, 5, 6], 10, False, False, True, "_p", 4),
    ],
)
def test_midpage_multi(
    press_30: Press,
    tmpdir: Path,
    size,
    margin,
    ppi,
    rtl,
    flip_even,
    separate_stacks,
    stack_prefix,
    stack_size,
):
    press_30.midpage_multi(
        tmpdir / "midpage_test.pdf",
        size=size,
        margin=margin,
        ppi=ppi,
        rtl=rtl,
        flip_even=flip_even,
        separate_stacks=separate_stacks,
        stack_prefix=stack_prefix,
        stack_size=stack_size,
    )
