from pymupdf import Pixmap

class Renderer():
    supported_extensions = []
    def __init__(self, file) -> None:
        pass

    def render(self, page, size) -> Pixmap:
        return b""

    def render_preview(self, page) -> Pixmap:
        return b""
    
    def get_text(self, page) -> str:
        return ""

    def __len__(self) -> int:
        """
        Page count
        """
        return 0
    