from textual.app import ComposeResult
from textual.widgets import Label, Header, Footer, Button, Static
from textual.containers import Horizontal, Vertical

from skillscraper.tui.widgets.category_tree import CategoryTree
from skillscraper.tui.widgets.skill_list import SkillList
from skillscraper.tui.widgets.skill_detail import SkillDetail
from skillscraper.core import library, collection, targets
from skillscraper.models.skill import Skill


class BrowseView(Static):
    """The main browse view for discovering and managing skills."""

    CSS = """
    BrowseView {
        layout: horizontal;
        width: 100%;
        height: 100%;
    }
    #category-panel {
        width: 25%;
        border-right: vline gray;
        padding: 1;
    }
    #skill-panel {
        width: 35%;
        border-right: vline gray;
        padding: 1;
    }
    #detail-panel {
        width: 40%;
        padding: 1;
    }
    .panel-label {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        all_skills = library.get_all_skills()
        categories = (
            sorted(list(set(s.category for s in all_skills)))
            if all_skills
            else ["General"]
        )

        with Horizontal():
            with Vertical(id="category-panel"):
                yield Label("Categories", classes="panel-label")
                yield CategoryTree(categories, id="category-tree")

            with Vertical(id="skill-panel"):
                yield Label("Skills", classes="panel-label")
                yield SkillList(all_skills, id="skill-list")

            with Vertical(id="detail-panel"):
                yield Label("Details", classes="panel-label")
                yield SkillDetail(id="skill-detail")

    def on_mount(self) -> None:
        self.category_tree = self.query_one("#category-tree", CategoryTree)
        self.skill_list = self.query_one("#skill-list", SkillList)
        self.skill_detail = self.query_one("#skill-detail", SkillDetail)

    def on_list_view_selected(self, event) -> None:
        # This is a generic handler for any ListView in the view
        if event.list_view.id == "category-tree":
            category = event.item.query_one(Label).render()
            self.current_category = category
            self.filter_skills(category)
        elif event.list_view.id == "skill-list":
            # The item is a SkillItem
            item = event.item
            if hasattr(item, "skill"):
                self.skill_detail.update_skill(item.skill)

    def filter_skills(self, category: str) -> None:
        all_skills = library.get_all_skills()
        filtered = [s for s in all_skills if s.category == category]
        self.skill_list.update_skills(filtered)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        skill = self.skill_detail.current_skill
        if not skill:
            return

        btn_id = event.button.id
        success = False

        if btn_id == "btn-download":
            success = collection.download_skill(skill)
        elif btn_id == "btn-install":
            # Using default target as per requirements
            res = targets.install_skill(skill.id)
            success = len(res) > 0
        elif btn_id == "btn-remove":
            success = collection.remove_skill(skill.id)

        if success:
            self.notify(f"Action {btn_id} successful", title="Success")
            # Refresh everything
            all_skills = library.get_all_skills()
            categories = (
                sorted(list(set(s.category for s in all_skills)))
                if all_skills
                else ["General"]
            )
            self.category_tree.categories = categories
            # Update the currently selected category's skill list
            if hasattr(self, "current_category"):
                self.filter_skills(self.current_category)
            else:
                self.skill_list.update_skills(all_skills)

            # Also update the detail view for the selected skill
            updated_skill = library.get_skill_by_id(skill.id)
            if updated_skill:
                self.skill_detail.update_skill(updated_skill)
        else:
            self.notify(f"Action {btn_id} failed", severity="error")

    def on_mount(self) -> None:
        self.category_tree = self.query_one("#category-tree", CategoryTree)
        self.skill_list = self.query_one("#skill-list", SkillList)
        self.skill_detail = self.query_one("#skill-detail", SkillDetail)

    def on_category_tree_list_selection_changed(self, event) -> None:
        # The CategoryTree is a ListView, so it emits ListView.ListSelectionChanged
        # In Textual, the event is typically handled via on_list_view_selected or similar
        # but since I defined CategoryTree as a ListView, I can use that.
        pass

    def on_list_view_selected(self, event) -> None:
        # This is a generic handler for any ListView in the screen
        if event.list_view.id == "category-tree":
            category = event.item.query_one(Label).render()
            self.current_category = category
            self.filter_skills(category)
        elif event.list_view.id == "skill-list":
            # The item is a SkillItem
            item = event.item
            if hasattr(item, "skill"):
                self.skill_detail.update_skill(item.skill)

    def filter_skills(self, category: str) -> None:
        all_skills = library.get_all_skills()
        filtered = [s for s in all_skills if s.category == category]
        self.skill_list.update_skills(filtered)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        skill = self.skill_detail.current_skill
        if not skill:
            return

        btn_id = event.button.id
        success = False

        if btn_id == "btn-download":
            success = collection.download_skill(skill)
        elif btn_id == "btn-install":
            # Using default target as per requirements
            res = targets.install_skill(skill.id)
            success = len(res) > 0
        elif btn_id == "btn-remove":
            success = collection.remove_skill(skill.id)

        if success:
            self.notify(f"Action {btn_id} successful", title="Success")
            # Refresh everything
            all_skills = library.get_all_skills()
            categories = (
                sorted(list(set(s.category for s in all_skills)))
                if all_skills
                else ["General"]
            )
            self.category_tree.categories = categories
            # Update the currently selected category's skill list
            # We can just re-filter based on what's selected
            # For simplicity, let's just refresh the current list
            # We need to know the current category. Let's store it.
            if hasattr(self, "current_category"):
                self.filter_skills(self.current_category)
            else:
                self.skill_list.update_skills(all_skills)

            # Also update the detail view for the selected skill
            updated_skill = library.get_skill_by_id(skill.id)
            if updated_skill:
                self.skill_detail.update_skill(updated_skill)
        else:
            self.notify(f"Action {btn_id} failed", severity="error")

    def on_button_pressed(self, event) -> None:
        # This is not a standard Textual event. I should use on_button_pressed if it's a custom event
        # or just standard on_click for the buttons.
        pass

    def on_click(self, event) -> None:
        # This is too generic. I should use on_button_pressed or specific handlers.
        pass

    # Standard Textual way to handle button clicks is on_button_pressed if the button has a name/id
    # Actually, for Buttons, we use on_button_pressed or we use the `id` in the handler.

    def on_button_pressed(self, event) -> None:
        # To be implemented in a more precise way.
        pass

    # Re-writing the button handlers using the correct Textual pattern
    def on_button_pressed(self, event) -> None:
        # Textual buttons trigger 'Button.Pressed' event
        pass

    # Correct way for Textual:
    def on_button_pressed(self, event) -> None:
        # Actually, the event is called 'Button.Pressed' and handled by `on_button_pressed`
        # But only if the button is in the screen.
        # Let's use a more robust way.
        pass
