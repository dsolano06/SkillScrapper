from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from ruamel.yaml import YAML

from skillscraper.core.paths import get_combos_dir
from skillscraper.core import library, collection, targets

yaml = YAML()
yaml.preserve_quotes = True


def save_combo(name: str, combo_data: Dict[str, Any]) -> Path:
    """Saves combo data to combos/<name>.yaml, preserving metadata if present."""
    combos_dir = get_combos_dir()
    combos_dir.mkdir(parents=True, exist_ok=True)

    combo_file = combos_dir / f"{name}.yaml"

    with open(combo_file, "w", encoding="utf-8") as f:
        yaml.dump(combo_data, f)

    return combo_file


def create_combo(
    name: str, description: str, skills_dict: Dict[str, Dict[str, Any]]
) -> Path:
    """
    Saves a new combo to combos/<name>.yaml.
    skills_dict: { "sub_combo_name": { "description": "...", "always_active": bool, "skills": [ids] } }
    """
    combos_dir = get_combos_dir()
    combos_dir.mkdir(parents=True, exist_ok=True)

    combo_file = combos_dir / f"{name}.yaml"

    combo_data = {
        "name": name,
        "description": description,
        "version": "1.0.0",
        "author": "User",
        "created": datetime.now().isoformat(),
        "sub_combos": skills_dict,
    }

    with open(combo_file, "w", encoding="utf-8") as f:
        yaml.dump(combo_data, f)

    return combo_file


def list_combos() -> List[str]:
    """Returns all .yaml files in the combos/ directory."""
    combos_dir = get_combos_dir()
    if not combos_dir.exists():
        return []
    return [f.stem for f in combos_dir.glob("*.yaml")]


def get_combo(name: str) -> Optional[Dict]:
    """Loads a specific combo file and parses it."""
    combo_file = get_combos_dir() / f"{name}.yaml"
    if not combo_file.exists():
        return None

    with open(combo_file, "r", encoding="utf-8") as f:
        return yaml.load(f)


def delete_combo(name: str) -> bool:
    """Removes the YAML file."""
    combo_file = get_combos_dir() / f"{name}.yaml"
    if combo_file.exists():
        combo_file.unlink()
        return True
    return False


def edit_combo(name: str) -> Path:
    """Returns the path to the combo file for editing."""
    return get_combos_dir() / f"{name}.yaml"


def install_combo(
    name: str, sub_combos: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Installs the skills associated with the combo/sub-combos.
    Returns a list of installation results.
    """
    combo = get_combo(name)
    if not combo:
        raise FileNotFoundError(f"Combo '{name}' not found.")

    all_sub_combos = combo.get("sub_combos", {})

    # Determine which sub-combos to install
    selected_sub_combos = {}
    if sub_combos:
        for sc_name in sub_combos:
            if sc_name in all_sub_combos:
                selected_sub_combos[sc_name] = all_sub_combos[sc_name]
    else:
        selected_sub_combos = all_sub_combos

    results = []
    for sc_name, sc_data in selected_sub_combos.items():
        skills_to_install = sc_data.get("skills", [])
        for skill_id in skills_to_install:
            skill = library.get_skill_by_id(skill_id)
            if not skill:
                results.append(
                    {
                        "skill_id": skill_id,
                        "status": "error",
                        "message": "Skill not found in library",
                    }
                )
                continue

            # 1. Ensure downloaded
            if not collection.download_skill(skill):
                results.append(
                    {
                        "skill_id": skill_id,
                        "status": "error",
                        "message": "Download failed",
                    }
                )
                continue

            # 2. Install to all targets
            installed_targets = targets.install_skill(skill_id, all_targets=True)
            results.append(
                {
                    "skill_id": skill_id,
                    "status": "success",
                    "targets": installed_targets,
                }
            )

    return results
