import pytest
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from unittest.mock import patch, MagicMock
from skillscraper.core import combos, library, collection, targets
from skillscraper.models.skill import Skill
from skillscraper.core.paths import get_combos_dir


@pytest.fixture
def sample_combo_data():
    return {
        "name": "Dev Combo",
        "description": "Core dev skills",
        "sub_combos": {
            "python-core": {
                "description": "Python basics",
                "skills": ["python-1", "python-2"],
            }
        },
    }


def test_create_and_get_combo(clean_storage, sample_combo_data):
    name = "dev-combo"
    combos.create_combo(
        name=name,
        description=sample_combo_data["description"],
        skills_dict=sample_combo_data["sub_combos"],
    )

    assert name in combos.list_combos()

    combo = combos.get_combo(name)
    assert combo is not None
    assert combo["name"] == "dev-combo"


def test_delete_combo(clean_storage, sample_combo_data):
    name = "delete-me"
    combos.create_combo(name, "desc", {})
    assert name in combos.list_combos()

    success = combos.delete_combo(name)
    assert success is True
    assert name not in combos.list_combos()


def test_install_combo(clean_storage, sample_combo_data):
    name = "install-combo"
    combos.create_combo(name, "desc", sample_combo_data["sub_combos"])

    # Mock library, collection and targets
    with (
        patch("skillscraper.core.library.get_skill_by_id") as mock_get_skill,
        patch("skillscraper.core.collection.download_skill") as mock_download,
        patch("skillscraper.core.targets.install_skill") as mock_install,
    ):
        # Mock skill
        skill = Skill(
            id="python-1", name="P1", description="...", category="...", repo="..."
        )
        mock_get_skill.return_value = skill
        mock_download.return_value = True
        mock_install.return_value = ["target1"]

        results = combos.install_combo(name)

        # We have 2 skills in python-core
        assert len(results) == 2
        assert results[0]["status"] == "success"
        assert "target1" in results[0]["targets"]


def test_install_combo_not_found():
    with pytest.raises(FileNotFoundError):
        combos.install_combo("non-existent")
