import pytest
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock
from skillscraper.core.sync import sync_library
from skillscraper.core.paths import get_index_file
from skillscraper.models.skill import Skill
from skillscraper.models.repo import Repo


@pytest.mark.asyncio
async def test_sync_library_basic(clean_storage):
    # Mock RepoManager.fetch_skills
    with patch("skillscraper.core.sync.RepoManager") as MockRepoManager:
        instance = MockRepoManager.return_value
        repo1 = Repo(
            id="repo1",
            url="http://repo1",
            type="remote",
            priority=1,
            enabled=True,
            skills_path="skills",
        )
        instance.repos = {"repo1": repo1}

        skill1 = Skill(
            id="skill1",
            name="Skill 1",
            description="Desc 1",
            category="Cat 1",
            repo="repo1",
        )
        instance.fetch_skills = AsyncMock(return_value=[skill1])

        skills = await sync_library()

        assert len(skills) == 1
        assert skills[0].id == "skill1"

        index_path = get_index_file()
        assert index_path.exists()
        with open(index_path, "r") as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["id"] == "skill1"


@pytest.mark.asyncio
async def test_sync_library_priority(clean_storage):
    with patch("skillscraper.core.sync.RepoManager") as MockRepoManager:
        instance = MockRepoManager.return_value
        repo_low = Repo(
            id="repo_low",
            url="...",
            type="remote",
            priority=10,
            enabled=True,
            skills_path="skills",
        )
        repo_high = Repo(
            id="repo_high",
            url="...",
            type="remote",
            priority=1,
            enabled=True,
            skills_path="skills",
        )
        instance.repos = {"low": repo_low, "high": repo_high}

        skill_low = Skill(
            id="shared",
            name="Low Priority",
            description="...",
            category="...",
            repo="repo_low",
        )
        skill_high = Skill(
            id="shared",
            name="High Priority",
            description="...",
            category="...",
            repo="repo_high",
        )

        async def mock_fetch(repo):
            if repo.id == "repo_low":
                return [skill_low]
            if repo.id == "repo_high":
                return [skill_high]
            return []

        instance.fetch_skills = AsyncMock(side_effect=mock_fetch)

        skills = await sync_library()

        assert len(skills) == 1
        assert skills[0].name == "High Priority"


@pytest.mark.asyncio
async def test_sync_library_preserve_status(clean_storage):
    index_path = get_index_file()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    skill_local = Skill(
        id="skill1", name="S1", description="D1", category="C1", repo="repo1"
    )
    skill_local.in_collection = True
    with open(index_path, "w") as f:
        json.dump([skill_local.to_dict()], f)

    with patch("skillscraper.core.sync.RepoManager") as MockRepoManager:
        instance = MockRepoManager.return_value
        repo1 = Repo(
            id="repo1",
            url="...",
            type="remote",
            priority=1,
            enabled=True,
            skills_path="skills",
        )
        instance.repos = {"repo1": repo1}

        skill_remote = Skill(
            id="skill1",
            name="S1 Updated",
            description="D1",
            category="C1",
            repo="repo1",
        )
        instance.fetch_skills = AsyncMock(return_value=[skill_remote])

        skills = await sync_library()

        assert skills[0].in_collection is True
        assert skills[0].name == "S1 Updated"
