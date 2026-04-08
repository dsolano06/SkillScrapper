from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Label, Static
from skillscraper.models.skill import Skill


class SkillItem(ListItem):
    """A single skill entry in the list with indicators."""

    def __init__(self, skill: Skill, **kwargs):
        super().__init__(**kwargs)
        self.skill = skill

    def compose(self) -> ComposeResult:
        # Collected status indicator
        collected_indicator = "✓" if self.skill.in_collection else " "
        # Update indicator (simplified as a dot for now, logic for 'outdated' usually involves version check)
        # Since we don't have a full version check logic yet, we'll assume a placeholder for the dot
        update_dot = "●" if getattr(self.skill, "update_available", False) else ""

        yield Label(
            f"{collected_indicator} {self.skill.name} ({self.skill.id}) {update_dot}"
        )


class SkillList(ListView):
    """A list of skills in the selected category."""

    def __init__(self, skills: list[Skill] = None, **kwargs):
        super().__init__(**kwargs)
        self.skills = skills or []

    def update_skills(self, skills: list[Skill]):
        self.skills = skills
        self.clear()
        for skill in skills:
            self.append(SkillItem(skill))
