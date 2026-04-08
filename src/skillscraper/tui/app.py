from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Label, Static
from textual.containers import Container, Vertical
from textual.binding import Binding

from skillscraper.tui.command_palette import CommandPalette
from skillscraper.tui.screens.browse import BrowseView
from skillscraper.tui.screens.combo_editor import ComboEditor
from skillscraper.tui.screens.help import HelpView
from skillscraper.core import sync, search, library, collection, targets, combos


class SkillScraperApp(App):
    """SkillScraper TUI Application."""

    CSS = """
    Screen {
        align: center middle;
    }

    #main-container {
        width: 100%;
        height: 100%;
    }

    #browse-mode {
        align: center middle;
        width: 100%;
        height: 1fr;
    }

    #input-container {
        dock: bottom;
        height: 3;
        width: 100%;
        padding: 0 1;
    }

    #global-input {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+l", "clear", "Clear"),
    ]

    def __init__(self):
        super().__init__()
        # Define command registry
        # name: (description, callback)
        self.commands = {
            "sync": (
                "Synchronize the local library catalog",
                lambda: sync.sync_library(),
            ),
            "search": (
                "Search for skills in the library",
                lambda: "Search requires a query",
            ),
            "installed": ("List all installed skills", lambda: targets.list_targets()),
            "collection": (
                "List all collected skills",
                lambda: collection.list_collected_skills(),
            ),
            "combo": (
                "Manage combos (list, show, install, edit)",
                lambda: "Combo requires a subcommand",
            ),
            "help": (
                "Show help guide",
                lambda: None,
            ),
        }

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with Vertical(id="browse-mode"):
                yield BrowseView()
            with Container(id="input-container"):
                yield Input(placeholder="Type / for commands...", id="global-input")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value
        if value.startswith("/"):
            self.push_screen(CommandPalette(self.commands, self.execute_command))
            self.query_one("#global-input").value = ""
        else:
            # Handle normal input or do nothing
            self.notify(f"You entered: {value}")

    def execute_command(self, name: str, callback, full_command: str):
        """Bridge to execute commands and show notifications."""
        try:
            if name == "help":
                self.push_screen(HelpView())
            elif name == "combo":
                parts = full_command.split()
                if len(parts) < 2:
                    self.notify(
                        "Combo requires a subcommand (list, show, install, edit)",
                        severity="error",
                    )
                    return

                subcmd = parts[1]
                if subcmd == "list":
                    result = combos.list_combos()
                    self.notify(
                        f"Available combos: {', '.join(result)}", title="Combos"
                    )
                elif subcmd == "edit":
                    if len(parts) < 3:
                        self.notify("Edit requires a combo name", severity="error")
                        return
                    combo_name = parts[2]
                    self.push_screen(ComboEditor(combo_name))
                elif subcmd == "show":
                    if len(parts) < 3:
                        self.notify("Show requires a combo name", severity="error")
                        return
                    combo_name = parts[2]
                    combo = combos.get_combo(combo_name)
                    if combo:
                        self.notify(
                            f"Combo: {combo.get('name')} - {combo.get('description')}",
                            title="Combo Details",
                        )
                    else:
                        self.notify(f"Combo '{combo_name}' not found", severity="error")
                elif subcmd == "install":
                    if len(parts) < 3:
                        self.notify("Install requires a combo name", severity="error")
                        return
                    combo_name = parts[2]
                    try:
                        res = combos.install_combo(combo_name)
                        self.notify(
                            f"Installed {len(res)} skills from {combo_name}",
                            title="Success",
                        )
                    except Exception as e:
                        self.notify(f"Install failed: {e}", severity="error")
                else:
                    self.notify(f"Unknown combo subcommand: {subcmd}", severity="error")
            else:
                # Handle sync as async if necessary
                import asyncio

                if asyncio.iscoroutinefunction(callback):
                    # Textual app runs on an event loop
                    asyncio.create_task(callback())
                else:
                    # For simple callbacks that might return info
                    result = callback()
                    # If it's a list or something, just notify success
                    self.notify(f"Executed {name} successfully", title="Success")
        except Exception as e:
            self.notify(f"Error executing {name}: {e}", severity="error")

    def on_mount(self) -> None:
        self.query_one("#global-input").focus()


if __name__ == "__main__":
    app = SkillScraperApp()
    app.run()
