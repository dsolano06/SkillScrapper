import pytest
import json
import tomllib
from pathlib import Path
from unittest.mock import MagicMock, patch
import httpx

from skillscraper.core.library import get_all_skills, _save_index
from skillscraper.core.targets import _load_targets, _save_targets, install_skill
from skillscraper.core.sync import sync_library
from skillscraper.core.paths import get_index_file, get_targets_file
from skillscraper.models.skill import Skill


def test_malformed_index_json(tmp_path, monkeypatch):
    index_file = tmp_path / "index.json"
    index_file.write_text("invalid json{", encoding="utf-8")

    monkeypatch.setattr("skillscraper.core.library.get_index_file", lambda: index_file)

    # Should return empty list instead of crashing
    assert get_all_skills() == []


def test_malformed_targets_toml(tmp_path, monkeypatch):
    targets_file = tmp_path / "targets.toml"
    targets_file.write_text("invalid = [toml", encoding="utf-8")

    monkeypatch.setattr(
        "skillscraper.core.targets.get_targets_file", lambda: targets_file
    )

    # Should return default targets instead of crashing
    assert _load_targets() == {"targets": {}}


def test_missing_meta_json_in_collection(tmp_path, monkeypatch):
    collection_dir = tmp_path / "collection"
    skill_dir = collection_dir / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("Content")
    # No _meta.json

    monkeypatch.setattr(
        "skillscraper.core.collection.get_collection_dir", lambda: collection_dir
    )

    from skillscraper.core.collection import list_collected_skills

    # Should not include skill with missing _meta.json
    assert list_collected_skills() == []


@pytest.mark.asyncio
async def test_sync_network_failure_retry(tmp_path, monkeypatch):
    index_file = tmp_path / "index.json"
    monkeypatch.setattr("skillscraper.core.paths.get_index_file", lambda: index_file)
    monkeypatch.setattr("skillscraper.core.paths.init_storage", lambda: None)

    from skillscraper.core.repos import Repo, RepoManager

    rm = RepoManager()
    rm.repos = {
        "r1": Repo(
            id="r1",
            skills_path="skills.json",
            url="http://repo",
            type="index",
            enabled=True,
            priority=1,
            index_path="index.json",
        )
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = [
            httpx.RequestError("Timeout"),
            MagicMock(
                status_code=200,
                raise_for_status=lambda: None,
                json=lambda: [
                    {"id": "s1", "name": "n1", "description": "d1", "category": "c1"}
                ],
            ),
        ]

        skills = await rm._fetch_index_repo(rm.repos["r1"])
        assert len(skills) == 1
        assert skills[0].id == "s1"
        assert mock_get.call_count == 2


def test_windows_symlink_fallback(tmp_path, monkeypatch):
    collection_dir = tmp_path / "collection"
    skill_id = "test-skill"
    skill_path = collection_dir / skill_id
    skill_path.mkdir(parents=True)

    targets_file = tmp_path / "targets.toml"
    targets_file.write_text(
        '[targets]\nlocal = { path = "C:/targets/local", strategy = "symlink" }',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "skillscraper.core.targets.get_targets_file", lambda: targets_file
    )
    monkeypatch.setattr(
        "skillscraper.core.targets.get_collection_dir", lambda: collection_dir
    )

    with patch("pathlib.Path.symlink_to", side_effect=OSError("Symlink failed")):
        with patch("shutil.copytree") as mock_copy:
            # Mock target path as something that exists or can be created
            with patch("pathlib.Path.mkdir"):
                installed = install_skill(skill_id, target_name="local")
                assert "local" in installed
                mock_copy.assert_called()
