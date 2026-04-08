from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label


class CategoryTree(ListView):
    """A list of skill categories for filtering."""

    def __init__(self, categories: list[str], **kwargs):
        super().__init__(**kwargs)
        self.categories = categories

    def compose(self) -> ComposeResult:
        for cat in self.categories:
            yield ListItem(Label(cat), id=f"cat-{cat}")
