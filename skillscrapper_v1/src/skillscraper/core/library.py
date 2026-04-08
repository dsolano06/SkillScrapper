from typing import List, Optional
import json
from skillscraper.core.paths import get_index_file
from skillscraper.models.skill import Skill
from skillscraper.core.utils import atomic_write


def _load_index() -> List[Skill]:
    index_path = get_index_file()
    if not index_path.exists():
        return []
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Skill.from_dict(skill_data) for skill_data in data]
    except (json.JSONDecodeError, IOError):
        return []


def _save_index(skills: List[Skill]) -> None:
    index_path = get_index_file()

    def write_json(f):
        json.dump([skill.to_dict() for skill in skills], f, indent=4)

    atomic_write(index_path, write_json)


def get_all_skills() -> List[Skill]:
    """Returns a list of all available skills in the library."""
    return _load_index()


def get_skill_by_id(skill_id: str) -> Optional[Skill]:
    """Returns a specific skill or None."""
    skills = _load_index()
    for skill in skills:
        if skill.id == skill_id:
            return skill
    return None


def update_skill_status(skill_id: str, in_collection: bool) -> bool:
    """Updates the in_collection flag and saves the index."""
    skills = _load_index()
    found = False
    for skill in skills:
        if skill.id == skill_id:
            skill.in_collection = in_collection
            found = True
            break

    if found:
        _save_index(skills)

    return found
