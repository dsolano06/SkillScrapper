from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical, Container
from textual.binding import Binding
from rapidfuzz import process, fuzz


class CommandItem(ListItem):
    def __init__(self, command_name: str, description: str, callback):
        super().__init__()
        self.command_name = command_name
        self.description = description
        self.callback = callback

    def compose(self) -> ComposeResult:
        yield Label(f"[b]{self.command_name}[/b] - {self.description}")


class CommandPalette(ModalScreen):
    """A modal screen for executing slash commands with fuzzy filtering."""

    CSS = """
    CommandPalette {
        align: center middle;
    }

    #palette-container {
        width: 60;
        height: auto;
        max-height: 20;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }

    #command-input {
        margin-bottom: 1;
    }

    #command-list {
        height: 10;
        border: none;
    }
    """

    def __init__(self, commands: dict, execute_callback):
        super().__init__()
        self.commands = commands  # name: (description, callback)
        self.execute_callback = execute_callback

    def compose(self) -> ComposeResult:
        with Container(id="palette-container"):
            yield Input(
                placeholder="Type a command... (e.g. /sync)", id="command-input"
            )
            yield ListView(id="command-list")
        return

    def on_mount(self) -> None:
        self.query_one("#command-input").focus()
        self.update_list("")

    def on_input_changed(self, event: Input.Changed) -> None:
        # Remove leading slash for filtering
        query = event.value.lstrip("/")
        self.update_list(query)

    def update_list(self, query: str) -> None:
        list_view = self.query_one("#command-list", ListView)
        list_view.clear()

        if not query:
            # Show all commands
            for name, (desc, callback) in self.commands.items():
                list_view.append(CommandItem(name, desc, callback))
        else:
            # Fuzzy filter
            names = list(self.commands.keys())
            # Use rapidfuzz to get best matches
            matches = process.extract(query, names, scorer=fuzz.WRatio, limit=10)
            for name, score, _ in matches:
                desc, callback = self.commands[name]
                list_view.append(CommandItem(name, desc, callback))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, CommandItem):
            # Execute the command
            self.execute_callback(item.command_name, item.callback, item.command_name)
            self.app.pop_screen()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        full_command = event.value.lstrip("/")

        # Handle help request: /command ?
        if " ?" in full_command:
            cmd_name = full_command.replace(" ?", "").strip()
            if cmd_name in self.commands:
                desc = self.commands[cmd_name][0]
                self.execute_callback("help", lambda: f"Help for {cmd_name}: {desc}")
                self.app.pop_screen()
                return

        # Try to execute the exact command
        parts = full_command.split()
        if not parts:
            return

        main_cmd = parts[0]
        if main_cmd in self.commands:
            desc, callback = self.commands[main_cmd]
            self.execute_callback(main_cmd, callback, full_command)
            self.app.pop_screen()
        else:
            # If not found, we can just let it be or show error
            pass

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()
