from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, ListView, ListItem, Static, Button
from textual.containers import Horizontal, Vertical, Container
from textual.binding import Binding


class HelpItem(ListItem):
    def __init__(self, command_name: str, details: dict):
        super().__init__()
        self.command_name = command_name
        self.details = details

    def compose(self) -> ComposeResult:
        yield Label(f"[b]{self.command_name}[/b]")


class HelpView(Screen):
    """An interactive help screen for SkillScraper."""

    CSS = """
    HelpView {
        align: center middle;
    }
    #help-container {
        width: 80%;
        height: 80%;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }
    #content-area {
        display: flex;
        height: 1fr;
    }
    #command-list {
        width: 30%;
        border-right: vline gray;
        margin-right: 1;
    }
    #detail-area {
        width: 70%;
        padding: 1;
    }
    .section-title {
        text-style: bold;
        margin-bottom: 1;
        color: $accent;
    }
    .syntax-text {
        color: $secondary;
        margin-bottom: 1;
    }
    .example-text {
        italic True;
        color: $text-muted;
        margin-bottom: 1;
    }
    #back-btn {
        dock: bottom;
        align: right middle;
        margin: 1;
    }
    """

    HELP_DATA = {
        "sync": {
            "syntax": "/sync",
            "description": "Synchronize the local library catalog with remote repositories.",
            "examples": ["/sync"],
        },
        "search": {
            "syntax": "/search <query> [--category <category>]",
            "description": "Search for skills in the library.",
            "examples": ["/search python", "/search ai --category productivity"],
        },
        "installed": {
            "syntax": "/installed",
            "description": "List all skills installed in each target.",
            "examples": ["/installed"],
        },
        "collection": {
            "syntax": "/collection",
            "description": "List all skills currently in your local collection.",
            "examples": ["/collection"],
        },
        "combo list": {
            "syntax": "/combo list",
            "description": "List all available combos.",
            "examples": ["/combo list"],
        },
        "combo show": {
            "syntax": "/combo show <name>",
            "description": "Display the structure and skills of a specific combo.",
            "examples": ["/combo show pm-planning"],
        },
        "combo install": {
            "syntax": "/combo install <name> [--sub <sub_combos>] [--all]",
            "description": "Install skills from a combo.",
            "examples": [
                "/combo install pm-planning",
                "/combo install pm-planning --sub dev",
            ],
        },
        "combo create": {
            "syntax": "/combo create <name>",
            "description": "Create a new combo.",
            "examples": ["/combo create my-stack"],
        },
        "combo edit": {
            "syntax": "/combo edit <name>",
            "description": "Edit a combo in the system editor.",
            "examples": ["/combo edit my-stack"],
        },
        "combo delete": {
            "syntax": "/combo delete <name>",
            "description": "Delete a combo.",
            "examples": ["/combo delete my-stack"],
        },
    }

    QUICK_START = (
        "1. [b]Sync[/b]: Run [i]/sync[/i] to update the skill library.\n"
        "2. [b]Search[/b]: Use [i]/search <query>[/i] to find desired skills.\n"
        "3. [b]Download[/b]: Browse the TUI to download skills to your local collection.\n"
        "4. [b]Install[/b]: Install skills into your agent targets via the TUI or [i]/combo install[/i]."
    )

    def compose(self) -> ComposeResult:
        with Container(id="help-container"):
            yield Label("SkillScraper Help Guide", classes="section-title")

            with Vertical():
                # Quick Start Section
                yield Static(self.QUICK_START, classes="section-title")
                yield Label("\n--- Commands ---", classes="section-title")

                with Horizontal(id="content-area"):
                    yield ListView(id="command-list")
                    with Vertical(id="detail-area"):
                        yield Static(
                            "Select a command to see details.", id="detail-text"
                        )

            yield Button("Back", id="back-btn")

    def on_mount(self) -> None:
        list_view = self.query_one("#command-list", ListView)
        for cmd_name, details in self.HELP_DATA.items():
            list_view.append(HelpItem(cmd_name, details))
        list_view.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, HelpItem):
            self.update_details(item.details)

    def update_details(self, details: dict) -> None:
        detail_text = self.query_one("#detail-text", Static)

        content = f"[b]Syntax:[/b]\n[cyan]{details['syntax']}[/cyan]\n\n"
        content += f"[b]Description:[/b]\n{details['description']}\n\n"
        content += f"[b]Examples:[/b]\n"
        for ex in details["examples"]:
            content += f"[italic gray]{ex}[/italic gray]\n"

        detail_text.update(content)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-btn":
            self.app.pop_screen()
