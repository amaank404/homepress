from homepress.renderer import Renderer


class TestRenderer(Renderer):
    supported_extensions = []

    def __init__(
        self,
        len=1,
        render_res="RES",
        render_preview_res="RESPREV",
        get_text_res="The quick brown fox jumps tonsss",
    ):
        self.len = len
        self.render_res = render_res
        self.get_text_res = get_text_res
        self.render_preview_res = render_preview_res

    def __len__(self):
        return self.len

    def render(self, page, res):
        return self.render_res

    def render_preview(self, page):
        return self.render_preview_res

    def get_text(self, page):
        return self.get_text_res
