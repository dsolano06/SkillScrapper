import httpx
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List
from skillscraper.core.paths import get_collection_dir
from skillscraper.models.skill import Skill
from skillscraper.core import library


def _get_raw_url(skill: Skill) -> str:
    """Resolves the raw GitHub URL for the skill's SKILL.md."""
    # Default for the main antigravity repo
    if skill.repo == "antigravity" or "antigravity-awesome-skills" in skill.repo:
        base_url = (
            "https://raw.githubusercontent.com/sickn33/antigravity-awesome-skills/main"
        )
        # The skills are usually in a subfolder or at root.
        # Based on the structure, they are in folders named after the skill id.
        return f"{base_url}/{skill.id}/SKILL.md"

    # If repo is a full URL, try to convert to raw
    if "github.com" in skill.repo:
        return skill.repo.replace("github.com", "raw.githubusercontent.com").replace(
            "/blob/", "/"
        )

    return f"{skill.repo}/{skill.id}/SKILL.md"


def download_skill(skill: Skill) -> bool:
    """
    Downloads the skill assets from the repository to the local collection.
    """
    collection_path = get_collection_dir() / skill.id
    collection_path.mkdir(parents=True, exist_ok=True)

    url = _get_raw_url(skill)

    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()

            # Save SKILL.md
            skill_md_path = collection_path / "SKILL.md"
            skill_md_path.write_text(response.text, encoding="utf-8")

            # Save _meta.json
            meta_path = collection_path / "_meta.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(skill.to_dict(), f, indent=4)

        # Update library status
        library.update_skill_status(skill.id, in_collection=True)
        return True
    except Exception as e:
        # In a real app, we would log this. For now, just return False.
        return False


def remove_skill(skill_id: str) -> bool:
    """
    Removes a skill from the local collection.
    """
    collection_path = get_collection_dir() / skill_id
    if collection_path.exists() and collection_path.is_dir():
        shutil.rmtree(collection_path)
        library.update_skill_status(skill_id, in_collection=False)
        return True
    return False


def list_collected_skills() -> List[Skill]:
    """
    Returns a list of skills currently in the collection.
    """
    collection_dir = get_collection_dir()
    if not collection_dir.exists():
        return []

    collected_skills = []
    for skill_dir in collection_dir.iterdir():
        if skill_dir.is_dir():
            meta_path = skill_dir / "_meta.json"
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        collected_skills.append(Skill.from_dict(data))
                    except json.JSONDecodeError:
                        continue
    return collected_skills
