from textual.app import ComposeResult
from textual.widgets import Label, Button, Input, Checkbox, ListView, ListItem, Static
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.message import Message

from skillscraper.core import combos, library
from typing import Dict, Any, List


class ComboEditor(Screen):
    """Screen for creating and editing skill combos."""

    CSS = """
    ComboEditor {
        align: center middle;
    }
    #editor-container {
        width: 90%;
        height: 90%;
        border: solid gray;
        padding: 1;
    }
    .header-section {
        height: auto;
        margin-bottom: 1;
    }
    .input-field {
        margin-bottom: 1;
    }
    .input-label {
        text-style: bold;
    }
    #main-area {
        height: 1fr;
        layout: horizontal;
    }
    #subcombo-list-panel {
        width: 30%;
        border-right: vline gray;
        padding: 1;
    }
    #skills-selection-panel {
        width: 70%;
        padding: 1;
    }
    #footer-section {
        height: auto;
        margin-top: 1;
        align: right middle;
    }
    .footer-button {
        margin-left: 1;
    }
    """

    def __init__(self, combo_name: str):
        super().__init__()
        self.combo_name = combo_name
        self.combo_data = combos.get_combo(combo_name) or {
            "name": combo_name,
            "description": "",
            "version": "1.0.0",
            "author": "User",
            "created": "",
            "sub_combos": {},
        }
        self.current_subcombo = None

    def compose(self) -> ComposeResult:
        with Vertical(id="editor-container"):
            # Header section
            with Vertical(classes="header-section"):
                yield Label("Combo Name", classes="input-label")
                yield Input(
                    value=self.combo_data.get("name", ""),
                    id="name-input",
                    classes="input-field",
                )
                yield Label("Description", classes="input-label")
                yield Input(
                    value=self.combo_data.get("description", ""),
                    id="desc-input",
                    classes="input-field",
                )

            # Main area
            with Horizontal(id="main-area"):
                with Vertical(id="subcombo-list-panel"):
                    yield Label("Sub-combos", text_style="bold")
                    yield ListView(id="subcombo-list")

                with Vertical(id="skills-selection-panel"):
                    yield Label(
                        "Skills for Sub-combo", id="skills-header", text_style="bold"
                    )
                    yield Vertical(id="skills-checkbox-list")

            # Footer section
            with Horizontal(id="footer-section"):
                yield Button("Add Sub-combo", id="btn-add-sub", classes="footer-button")
                yield Button(
                    "Remove Sub-combo", id="btn-remove-sub", classes="footer-button"
                )
                yield Button(
                    "Save", id="btn-save", classes="footer-button", variant="success"
                )

    def on_mount(self) -> None:
        self.update_subcombo_list()

    def update_subcombo_list(self) -> None:
        subcombo_list = self.query_one("#subcombo-list", ListView)
        subcombo_list.clear()

        sub_combos = self.combo_data.get("sub_combos", {})
        for name in sub_combos.keys():
            subcombo_list.append(ListItem(Label(name), id=f"sub-{name}"))

    # Overriding the correct handler for ListView selection
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id == "subcombo-list":
            item = event.item
            if item:
                subcombo_name = item.id.replace("sub-", "")
                self.current_subcombo = subcombo_name
                self.update_skills_list(subcombo_name)

    def update_skills_list(self, subcombo_name: str) -> None:
        header = self.query_one("#skills-header", Label)
        header.update(f"Skills for {subcombo_name}")

        skills_container = self.query_one("#skills-checkbox-list", Vertical)
        skills_container.clear()

        all_skills = library.get_all_skills()
        subcombo_skills = (
            self.combo_data.get("sub_combos", {})
            .get(subcombo_name, {})
            .get("skills", [])
        )

        for skill in all_skills:
            is_checked = skill.id in subcombo_skills
            skills_container.append(
                Checkbox(skill.name, value=is_checked, id=f"skill-{skill.id}")
            )

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if not self.current_subcombo:
            return

        skill_id = event.checkbox.id.replace("skill-", "")
        subcombos = self.combo_data.get("sub_combos", {})
        if self.current_subcombo not in subcombos:
            subcombos[self.current_subcombo] = {"skills": []}

        skills = subcombos[self.current_subcombo].get("skills", [])
        if event.value:
            if skill_id not in skills:
                skills.append(skill_id)
        else:
            if skill_id in skills:
                skills.remove(skill_id)

        subcombos[self.current_subcombo]["skills"] = skills
        self.combo_data["sub_combos"] = subcombos

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id

        if btn_id == "btn-add-sub":
            # Simple prompt for new sub-combo name (in a real app, maybe a modal)
            # For now, let's just add a generic one and let the user potentially rename it?
            # Actually, let's just add "New Sub-combo" and let the user see it.
            # To be better, we should probably have an input field for the name.
            # Since I can't easily add a modal here, I'll just add one with a timestamp.
            import datetime

            new_name = f"sub_{datetime.datetime.now().strftime('%H%M%S')}"
            subcombos = self.combo_data.get("sub_combos", {})
            subcombos[new_name] = {"description": "", "skills": []}
            self.combo_data["sub_combos"] = subcombos
            self.update_subcombo_list()

        elif btn_id == "btn-remove-sub":
            if not self.current_subcombo:
                return
            subcombos = self.combo_data.get("sub_combos", {})
            if self.current_subcombo in subcombos:
                del subcombos[self.current_subcombo]
                self.combo_data["sub_combos"] = subcombos
                self.current_subcombo = None
                self.update_subcombo_list()
                self.query_one("#skills-checkbox-list", Vertical).clear()
                self.query_one("#skills-header", Label).update("Skills for Sub-combo")

        elif btn_id == "btn-save":
            # Update metadata from inputs
            self.combo_data["name"] = self.query_one("#name-input", Input).value
            self.combo_data["description"] = self.query_one("#desc-input", Input).value

            combos.save_combo(self.combo_name, self.combo_data)
            self.notify("Combo saved successfully!", title="Saved")
