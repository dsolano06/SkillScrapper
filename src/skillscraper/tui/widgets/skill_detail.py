from textual.app import ComposeResult
from textual.widgets import Static, Button, Label
from textual.containers import Vertical
from skillscraper.models.skill import Skill


class SkillDetail(Static):
    """A detailed view of a selected skill with action buttons."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_skill = None

    def update_skill(self, skill: Skill):
        self.current_skill = skill
        self.refresh()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Select a skill to see details", id="detail-placeholder")
            yield Static("", id="detail-content")
            yield Button("Download", id="btn-download")
            yield Button("Install", id="btn-install")
            yield Button("Remove", id="btn-remove")

    def render(self) -> str:
        if not self.current_skill:
            return "Select a skill to see details"

        return (
            f"Name: {self.current_skill.name}\n"
            f"ID: {self.current_skill.id}\n"
            f"Category: {self.current_skill.category}\n"
            f"Version: {self.current_skill.version}\n\n"
            f"Description:\n{self.current_skill.description}"
        )
