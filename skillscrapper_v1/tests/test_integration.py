import pytest
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
from skillscraper.core import sync, search, collection, targets, library
from skillscraper.models.repo import Repo
from skillscraper.models.skill import Skill
from skillscraper.core.paths import get_index_file


@pytest.mark.asyncio
async def test_full_workflow(clean_storage):
    # 1. Setup Mock RepoManager for Sync
    with patch("skillscraper.core.sync.RepoManager") as MockRepoManager:
        instance = MockRepoManager.return_value
        repo = Repo(
            id="repo1",
            url="...",
            type="remote",
            priority=1,
            enabled=True,
            skills_path="skills",
        )
        instance.repos = {"repo1": repo}

        skill = Skill(
            id="workflow-skill",
            name="Workflow Skill",
            description="Integration test skill",
            category="Test",
            repo="repo1",
        )
        instance.fetch_skills = AsyncMock(return_value=[skill])

        # Sync
        synced_skills = await sync.sync_library()
        assert len(synced_skills) == 1
        assert synced_skills[0].id == "workflow-skill"

    # 2. Search
    search_results = search.search_skills("Workflow")
    assert len(search_results) == 1
    assert search_results[0][0].id == "workflow-skill"
    found_skill = search_results[0][0]

    # 3. Download
    with patch("httpx.Client.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = "# Workflow Skill Content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        download_success = collection.download_skill(found_skill)
        assert download_success is True

    # 4. Install
    with patch(
        "skillscraper.core.targets._load_targets",
        return_value={
            "targets": {
                "test-target": {
                    "path": "C:/tmp/target_dir",
                    "strategy": "copy",
                    "auto": True,
                }
            }
        },
    ):
        with patch("pathlib.Path.mkdir"), patch("shutil.copytree") as mock_copy:
            installed_in = targets.install_skill(
                "workflow-skill", target_name="test-target"
            )
            assert "test-target" in installed_in
            mock_copy.assert_called()

    # 5. Uninstall
    with patch(
        "skillscraper.core.targets._load_targets",
        return_value={
            "targets": {
                "test-target": {
                    "path": "C:/tmp/target_dir",
                    "strategy": "copy",
                    "auto": True,
                }
            }
        },
    ):
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_dir", return_value=True),
            patch("pathlib.Path.is_symlink", return_value=False),
            patch("shutil.rmtree") as mock_rmtree,
        ):
            uninstalled_from = targets.uninstall_skill(
                "workflow-skill", target_name="test-target"
            )
            assert "test-target" in uninstalled_from
            mock_rmtree.assert_called()
