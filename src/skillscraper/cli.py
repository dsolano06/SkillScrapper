import asyncio
import os
import typer
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from skillscraper.core import (
    sync as sync_core,
    search as search_core,
    library as lib_core,
    collection as coll_core,
    targets as targets_core,
    combos as combos_core,
    repos as repos_core,
)

from skillscraper.tui.app import SkillScraperApp


app = typer.Typer(help="SkillScraper: Terminal-first skill manager for AI agent skills")
console = Console()


@app.command()
def browse():
    """Open the SkillScraper TUI browser."""
    SkillScraperApp().run()


@app.command()
def sync():
    """Synchronize the local library catalog with remote repositories."""
    console.print("[yellow]Syncing library...[/yellow]")
    try:
        # sync_library is async, so we run it with asyncio.run
        updated_skills = asyncio.run(sync_core.sync_library())
        console.print(f"[green]Done.[/green] {len(updated_skills)} skills updated.")
    except Exception as e:
        console.print(f"[red]Error syncing library: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str, category: Optional[str] = typer.Option(None, help="Filter by category")
):
    """Search for skills in the library."""
    results = search_core.search_skills(query, category)

    if not results:
        console.print(f"[yellow]No skills found matching '{query}'[/yellow]")
        return

    table = Table(title=f"Search results for '{query}'")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Category", style="magenta")
    table.add_column("Score", style="green")

    for skill, score in results:
        table.add_row(skill.id, skill.name, skill.category, f"{score:.1f}")

    console.print(table)


@app.command()
def installed():
    """List all skills installed in each target."""
    targets = targets_core.list_targets()

    if not targets:
        console.print("[yellow]No targets configured.[/yellow]")
        return

    table = Table(title="Installed Skills per Target")
    table.add_column("Target", style="cyan")
    table.add_column("Installed Skills", style="white")

    for name in targets:
        skills = targets_core.get_installed_skills(name)
        skills_list = ", ".join(skills) if skills else "[none]"
        table.add_row(name, skills_list)

    console.print(table)


@app.command()
def collection():
    """List all skills currently in your local collection."""
    skills = coll_core.list_collected_skills()

    if not skills:
        console.print(
            "[yellow]Collection is empty. Download some skills first.[/yellow]"
        )
        return

    table = Table(title="Collected Skills")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Category", style="magenta")

    for skill in skills:
        table.add_row(skill.id, skill.name, skill.category)

    console.print(table)


combo_app = typer.Typer(help="Manage skill combos")


@combo_app.command("list")
def combo_list():
    """List all available combos."""
    combos = combos_core.list_combos()
    if not combos:
        console.print("[yellow]No combos found.[/yellow]")
        return

    console.print("[green]Available combos:[/green]")
    for combo in combos:
        console.print(f"- {combo}")


@combo_app.command("show")
def combo_show(name: str):
    """Display the structure and skills of a specific combo."""
    combo = combos_core.get_combo(name)
    if not combo:
        console.print(f"[red]Combo '{name}' not found.[/red]")
        return

    console.print(
        Panel(
            f"[bold]{combo.get('name')}[/bold]\n{combo.get('description', 'No description')}",
            title="Combo Details",
        )
    )

    sub_combos = combo.get("sub_combos", {})
    if not sub_combos:
        console.print("[yellow]No sub-combos defined.[/yellow]")
        return

    for sc_name, sc_data in sub_combos.items():
        skills = ", ".join(sc_data.get("skills", [])) or "[none]"
        console.print(f"[cyan]{sc_name}[/cyan]: {skills}")


@combo_app.command("install")
def combo_install(
    name: str,
    sub: Optional[str] = typer.Option(
        None, "--sub", help="Comma-separated list of sub-combos"
    ),
    all: bool = typer.Option(True, "--all", help="Install all sub-combos"),
):
    """Install skills from a combo."""
    sub_list = sub.split(",") if sub else None
    if not sub:
        # if --all is False and no --sub, it should probably just not install anything or we can default to all
        # The requirements say --all is a boolean.
        # Logic: If --sub is provided, use it. If not, and --all is True, install all.
        pass

    # If --sub is NOT provided and --all is FALSE, we should probably inform the user.
    if not sub and not all:
        console.print(
            "[yellow]Specify --sub or use --all (default) to install skills.[/yellow]"
        )
        return

    try:
        results = combos_core.install_combo(name, sub_combos=sub_list)

        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = sum(1 for r in results if r["status"] == "error")

        console.print(f"[green]Successfully installed {success_count} skills.[/green]")
        if error_count > 0:
            console.print(f"[red]{error_count} skills failed to install.[/red]")
    except Exception as e:
        console.print(f"[red]Error installing combo: {e}[/red]")
        raise typer.Exit(code=1)


@combo_app.command("create")
def combo_create(name: str):
    """Create a new combo."""
    description = typer.prompt("Enter combo description")
    # Simple prompt for skills: "subname:id1,id2;subname2:id3"
    skills_raw = typer.prompt(
        "Enter sub-combos and skills (e.g., 'dev:skill1,skill2;test:skill3')"
    )

    skills_dict = {}
    try:
        for part in skills_raw.split(";"):
            if not part:
                continue
            sc_name, sc_skills = part.split(":")
            skills_dict[sc_name] = {
                "description": f"Sub-combo {sc_name}",
                "always_active": True,
                "skills": sc_skills.split(","),
            }

        combos_core.create_combo(name, description, skills_dict)
        console.print(f"[green]Combo '{name}' created successfully.[/green]")
    except ValueError:
        console.print("[red]Invalid format. Use 'subname:id1,id2;subname2:id3'.[/red]")


@combo_app.command("edit")
def combo_edit(name: str):
    """Edit a combo in the system editor."""
    path = combos_core.edit_combo(name)
    if not path.exists():
        console.print(f"[red]Combo '{name}' not found.[/red]")
        return

    editor = os.environ.get("EDITOR", "notepad" if os.name == "nt" else "vim")
    os.system(f'{editor} "{path}"')


# ... existing code ...
@combo_app.command("delete")
def combo_delete(name: str):
    """Delete a combo."""
    if combos_core.delete_combo(name):
        console.print(f"[green]Combo '{name}' deleted.[/green]")
    else:
        console.print(f"[red]Combo '{name}' not found.[/red]")


repos_app = typer.Typer(help="Manage skill repositories")


@repos_app.command("list")
def repos_list():
    """List all configured repositories."""
    manager = repos_core.RepoManager()
    repos = manager.repos

    if not repos:
        console.print("[yellow]No repositories configured.[/yellow]")
        return

    table = Table(title="Configured Repositories")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Enabled", style="green")
    table.add_column("Priority", style="yellow")
    table.add_column("Location", style="white")

    for repo_id, repo in repos.items():
        location = repo.url or repo.path or "N/A"
        enabled_str = "[green]Yes[/green]" if repo.enabled else "[red]No[/red]"
        table.add_row(repo_id, repo.type, enabled_str, str(repo.priority), location)

    console.print(table)


@repos_app.command("add")
def repos_add(
    url: str,
    type: str = typer.Option(
        "standard", "--type", "-t", help="Repo type: standard, single-skill, local"
    ),
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Local path for local repos"
    ),
):
    """Add a new skill repository."""
    manager = repos_core.RepoManager()

    # Derive repo_id from url or path
    if type == "local" and path:
        repo_id = Path(path).name
    else:
        repo_id = url.split("/")[-1].split(".git")[0] or url

    repo_data = {
        "skills_path": "skills",
        "type": type,
        "url": url if type != "local" else None,
        "path": path if type == "local" else None,
        "enabled": True,
        "priority": 1,
    }

    manager.add_repo(repo_id, repo_data)
    console.print(f"[green]Repository '{repo_id}' added successfully.[/green]")


@repos_app.command("remove")
def repos_remove(name: str):
    """Remove a repository configuration."""
    manager = repos_core.RepoManager()
    manager.remove_repo(name)
    console.print(f"[green]Repository '{name}' removed.[/green]")


@repos_app.command("enable")
def repos_enable(name: str):
    """Enable a repository."""
    manager = repos_core.RepoManager()
    manager.toggle_repo(name, True)
    console.print(f"[green]Repository '{name}' enabled.[/green]")


@repos_app.command("disable")
def repos_disable(name: str):
    """Disable a repository."""
    manager = repos_core.RepoManager()
    manager.toggle_repo(name, False)
    console.print(f"[green]Repository '{name}' disabled.[/green]")


@repos_app.command("scan")
def repos_scan():
    """Manually trigger a sync of all enabled repositories."""
    console.print("[yellow]Scanning enabled repositories...[/yellow]")
    try:
        updated_skills = asyncio.run(sync_core.sync_library())
        console.print(
            f"[green]Scan complete.[/green] {len(updated_skills)} skills in library."
        )
    except Exception as e:
        console.print(f"[red]Error during scan: {e}[/red]")
        raise typer.Exit(code=1)


app.add_typer(combo_app, name="combo")
app.add_typer(repos_app, name="repos")


if __name__ == "__main__":
    app()
