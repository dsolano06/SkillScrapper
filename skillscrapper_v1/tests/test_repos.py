import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from skillscraper.core.repos import RepoManager
from skillscraper.models.repo import Repo
from skillscraper.core.paths import get_repos_dir


@pytest.mark.asyncio
async def test_repo_manager_crud(clean_storage):
    manager = RepoManager()
    repo_id = "test-repo"
    repo_data = {
        "skills_path": "skills",
        "type": "local",
        "path": str(clean_storage / "local_repo"),
        "priority": 1,
    }

    manager.add_repo(repo_id, repo_data)
    assert repo_id in manager.repos
    assert manager.repos[repo_id].type == "local"

    manager.toggle_repo(repo_id, False)
    assert manager.repos[repo_id].enabled is False

    manager.remove_repo(repo_id)
    assert repo_id not in manager.repos


@pytest.mark.asyncio
async def test_local_repo_scanning(clean_storage):
    local_repo_dir = clean_storage / "local_repo"
    local_repo_dir.mkdir()

    skill1_dir = local_repo_dir / "skill1"
    skill1_dir.mkdir()
    (skill1_dir / "SKILL.md").write_text("Skill 1 content")

    skill2_dir = local_repo_dir / "skill2"
    skill2_dir.mkdir()
    (skill2_dir / "SKILL.md").write_text("Skill 2 content")
    (skill2_dir / "metadata.json").write_text(
        '{"id": "skill2", "name": "Skill 2 Name", "description": "Skill 2 Desc"}'
    )

    manager = RepoManager()
    repo = Repo(
        id="local", skills_path="skills", type="local", path=str(local_repo_dir)
    )

    skills = await manager.fetch_skills(repo)

    assert len(skills) == 2
    skill_ids = [s.id for s in skills]
    assert "skill1" in skill_ids
    assert "skill2" in skill_ids

    skill2 = next(s for s in skills if s.id == "skill2")
    assert skill2.name == "Skill 2 Name"


@pytest.mark.asyncio
async def test_remote_index_fetching(clean_storage):
    manager = RepoManager()
    repo = Repo(
        id="remote",
        skills_path="skills",
        type="standard",
        url="https://example.com/repo",
        index_path="index.json",
    )

    mock_data = [
        {"id": "rem1", "name": "Remote 1", "description": "Desc 1"},
        {"id": "rem2", "name": "Remote 2", "description": "Desc 2"},
    ]

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        skills = await manager.fetch_skills(repo)

    assert len(skills) == 2
    assert skills[0].id == "rem1"
    assert skills[0].repo == "remote"
