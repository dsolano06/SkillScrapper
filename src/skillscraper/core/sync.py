import json
import httpx
from pathlib import Path
from typing import List, Dict, Any
from skillscraper.models.skill import Skill
from skillscraper.core.paths import get_index_file, init_storage
from skillscraper.core.repos import RepoManager
from skillscraper.core.utils import atomic_write


async def sync_library() -> List[Skill]:
    """
    Synchronizes the local library catalog with configured repositories.
    """
    init_storage()
    index_path = get_index_file()
    repo_manager = RepoManager()

    # Load existing local data to preserve 'in_collection' status
    local_skills: Dict[str, Skill] = {}
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                local_data = json.load(f)
                for item in local_data:
                    skill = Skill.from_dict(item)
                    local_skills[skill.id] = skill
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    # Map to keep track of the best skill for each ID based on priority
    # { skill_id: (priority, Skill) }
    best_skills: Dict[str, tuple[int, Skill]] = {}

    for repo_id, repo in repo_manager.repos.items():
        if not repo.enabled:
            continue

        try:
            skills = await repo_manager.fetch_skills(repo)
            for skill in skills:
                # Lower priority number wins
                if (
                    skill.id not in best_skills
                    or repo.priority < best_skills[skill.id][0]
                ):
                    best_skills[skill.id] = (repo.priority, skill)
        except Exception as e:
            # Log error and continue with other repos
            print(f"Error syncing repo {repo_id}: {e}")
            continue

    # Finalize skills and preserve local status
    updated_skills: List[Skill] = []
    for skill_id, (_, skill) in best_skills.items():
        if skill_id in local_skills:
            local = local_skills[skill_id]
            skill.in_collection = local.in_collection
            skill.collection_path = local.collection_path
            skill.downloaded_at = local.downloaded_at

        updated_skills.append(skill)

    # Write final result to library/index.json
    def write_json(f):
        json.dump([s.to_dict() for s in updated_skills], f, indent=2)

    atomic_write(index_path, write_json)

    return updated_skills
