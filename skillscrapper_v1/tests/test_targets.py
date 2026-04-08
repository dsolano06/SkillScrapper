import os
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from skillscraper.core import targets
from skillscraper.models.skill import Skill
from skillscraper.core.paths import get_collection_dir


def test_scan_targets(clean_storage, monkeypatch, tmp_path):
    # Use tmp_path for real directories
    temp_home = tmp_path / "home"
    temp_cwd = tmp_path / "cwd"
    temp_home.mkdir()
    temp_cwd.mkdir()

    # Create a dummy target directory in "home"
    target_dir = temp_home / ".claude" / "skills"
    target_dir.mkdir(parents=True)

    # Mock Path.home and Path.cwd
    monkeypatch.setattr(Path, "home", lambda: temp_home)
    with patch("skillscraper.core.targets.Path.cwd", return_value=temp_cwd):
        newly_registered = targets.scan_targets()
        assert "claude-global" in newly_registered

        current_targets = targets.list_targets()
        assert "claude-global" in current_targets


def test_install_skill_success(clean_storage, monkeypatch):
    targets.list_targets()
    with patch("skillscraper.core.targets._save_targets") as mock_save:
        target_path = Path("C:/tmp/target_dir")
        with patch(
            "skillscraper.core.targets._load_targets",
            return_value={
                "targets": {
                    "test-target": {
                        "path": str(target_path),
                        "strategy": "copy",
                        "auto": True,
                    }
                }
            },
        ):
            skill_id = "test-skill"
            coll_path = get_collection_dir() / skill_id
            coll_path.mkdir(parents=True)
            (coll_path / "SKILL.md").write_text("content")

            with patch("pathlib.Path.mkdir"), patch("shutil.copytree") as mock_copy:
                installed = targets.install_skill(skill_id, target_name="test-target")
                assert "test-target" in installed
                mock_copy.assert_called_once()


def test_install_skill_not_collected(clean_storage):
    with pytest.raises(FileNotFoundError):
        targets.install_skill("non-existent")


def test_uninstall_skill(clean_storage):
    target_path = Path("C:/tmp/target_dir")
    with patch(
        "skillscraper.core.targets._load_targets",
        return_value={
            "targets": {
                "test-target": {
                    "path": str(target_path),
                    "strategy": "copy",
                    "auto": True,
                }
            }
        },
    ):
        skill_id = "test-skill"
        dest_path = target_path / skill_id
        dest_path.mkdir(parents=True)

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.is_dir", return_value=True),
            patch("pathlib.Path.is_symlink", return_value=False),
            patch("shutil.rmtree") as mock_rmtree,
        ):
            uninstalled = targets.uninstall_skill(skill_id, target_name="test-target")
            assert "test-target" in uninstalled
            mock_rmtree.assert_called_once()
