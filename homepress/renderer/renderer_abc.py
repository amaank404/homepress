from pathlib import Path

from pymupdf import Pixmap

type Size = tuple[float, float]


class Renderer:
    supported_extensions: list[str] = []

    def __init__(self, file: str | Path) -> None:
        pass

    def render(self, page: int, size: Size) -> Pixmap:
        return b""

    def render_preview(self, page: int) -> Pixmap:
        return b""

    def get_text(self, page: int) -> str:
        return ""

    def __len__(self) -> int:
        """
        Page count
        """
        return 0
