import os
import shutil
import tomllib
import tomli_w
from pathlib import Path
from typing import Dict, List, Optional
from skillscraper.core.utils import atomic_write_binary
from skillscraper.core.paths import get_targets_file, get_collection_dir


def _load_targets() -> Dict:
    """Loads targets from targets.toml."""
    targets_file = get_targets_file()
    if not targets_file.exists():
        return {"targets": {}}

    try:
        with open(targets_file, "rb") as f:
            return tomllib.load(f)
    except (tomllib.TOMLDecodeError, IOError):
        return {"targets": {}}


def _save_targets(targets: Dict) -> None:
    """Saves targets to targets.toml."""
    targets_file = get_targets_file()

    def write_toml(f):
        tomli_w.dump(targets, f)

    atomic_write_binary(targets_file, write_toml)


def scan_targets() -> List[str]:
    """
    Auto-detects common agent skill directories and registers them.
    Returns a list of newly registered target names.
    """
    home = Path.home()
    cwd = Path.cwd()

    potential_targets = [
        ("claude-global", home / ".claude" / "skills"),
        ("claude-local", cwd / ".claude" / "skills"),
        ("cursor-global", home / ".cursor" / "skills"),
        ("codex-global", home / ".codex" / "skills"),
    ]

    targets_data = _load_targets()
    existing_targets = targets_data.get("targets", {})
    newly_registered = []

    for name, path in potential_targets:
        if name not in existing_targets:
            # Check if the directory exists or if the parent exists and can be created
            # For claude-local, we check if .claude exists in cwd
            if name == "claude-local":
                if (cwd / ".claude").exists():
                    existing_targets[name] = {
                        "path": str(path),
                        "strategy": "symlink",
                        "auto": True,
                    }
                    newly_registered.append(name)
            elif path.exists():
                existing_targets[name] = {
                    "path": str(path),
                    "strategy": "symlink",
                    "auto": True,
                }
                newly_registered.append(name)

    if newly_registered:
        targets_data["targets"] = existing_targets
        _save_targets(targets_data)

    return newly_registered


def list_targets() -> Dict[str, Dict]:
    """Returns all configured targets."""
    return _load_targets().get("targets", {})


def get_installed_skills(target_name: str) -> List[str]:
    """Lists what is actually present in that target folder."""
    targets = list_targets()
    if target_name not in targets:
        return []

    target_path = Path(targets[target_name]["path"]).expanduser()
    if not target_path.exists() or not target_path.is_dir():
        return []

    return [d.name for d in target_path.iterdir() if d.is_dir()]


def install_skill(
    skill_id: str,
    target_name: Optional[str] = None,
    all_targets: bool = False,
    force_copy: bool = False,
) -> List[str]:
    """
    Projects a skill from the collection to agent-specific directories.
    """
    collection_path = get_collection_dir() / skill_id
    if not collection_path.exists():
        raise FileNotFoundError(
            f"Skill '{skill_id}' not found in collection. Please download it first."
        )

    targets = list_targets()
    target_names = (
        targets.keys() if all_targets else ([target_name] if target_name else [])
    )

    if not target_names:
        # In a real app, we'd check config.toml for a default target.
        # For now, if no target specified and not all_targets, we fail or return empty.
        return []

    installed_in = []
    for name in target_names:
        if name not in targets:
            continue

        target_cfg = targets[name]
        target_root = Path(target_cfg["path"]).expanduser()
        target_root.mkdir(parents=True, exist_ok=True)

        dest_path = target_root / skill_id
        strategy = "copy" if force_copy else target_cfg.get("strategy", "symlink")

        if dest_path.exists():
            if dest_path.is_symlink() or dest_path.is_dir():
                # Overwrite existing
                if dest_path.is_dir() and not dest_path.is_symlink():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()

        try:
            if strategy == "symlink":
                dest_path.symlink_to(collection_path)
            else:
                shutil.copytree(collection_path, dest_path)
            installed_in.append(name)
        except (OSError, PermissionError):
            # Windows Fallback: If symlink fails, try copy
            if strategy == "symlink":
                try:
                    shutil.copytree(collection_path, dest_path)
                    installed_in.append(name)
                except Exception:
                    pass  # Fail silently or log
            else:
                pass  # Copy failed

    return installed_in


def uninstall_skill(skill_id: str, target_name: Optional[str] = None) -> List[str]:
    """Removes the link/folder from the target."""
    targets = list_targets()
    target_names = (
        targets.keys()
        if target_name is None
        else ([target_name] if target_name in targets else [])
    )

    uninstalled_from = []
    for name in target_names:
        target_root = Path(targets[name]["path"]).expanduser()
        dest_path = target_root / skill_id

        if dest_path.exists():
            if dest_path.is_dir() and not dest_path.is_symlink():
                shutil.rmtree(dest_path)
            else:
                dest_path.unlink()
            uninstalled_from.append(name)

    return uninstalled_from
