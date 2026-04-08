import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from skillscraper.core import collection
from skillscraper.models.skill import Skill
from skillscraper.core.paths import get_collection_dir


@pytest.fixture
def sample_skill():
    return Skill(
        id="test-skill",
        name="Test Skill",
        description="Test Desc",
        category="Test Cat",
        repo="antigravity",
    )


def test_download_skill_success(clean_storage, sample_skill):
    # Mock httpx.Client.get
    with patch("httpx.Client.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = "# Test Skill Content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        success = collection.download_skill(sample_skill)

        assert success is True

        # Check files
        coll_path = get_collection_dir() / sample_skill.id
        assert coll_path.exists()
        assert (coll_path / "SKILL.md").read_text() == "# Test Skill Content"

        meta_path = coll_path / "_meta.json"
        assert meta_path.exists()
        with open(meta_path, "r") as f:
            data = json.load(f)
            assert data["id"] == sample_skill.id


def test_download_skill_failure(clean_storage, sample_skill):
    with patch("httpx.Client.get") as mock_get:
        mock_get.side_effect = Exception("Network error")

        success = collection.download_skill(sample_skill)
        assert success is False


def test_remove_skill(clean_storage, sample_skill):
    # Setup a downloaded skill
    coll_path = get_collection_dir() / sample_skill.id
    coll_path.mkdir(parents=True)
    (coll_path / "SKILL.md").write_text("content")
    (coll_path / "_meta.json").write_text("{}")

    success = collection.remove_skill(sample_skill.id)
    assert success is True
    assert not coll_path.exists()

    # Remove non-existent
    success_none = collection.remove_skill("non-existent")
    assert success_none is False


def test_list_collected_skills(clean_storage, sample_skill):
    # Setup two downloaded skills
    for s_id in ["skill-1", "skill-2"]:
        skill = Skill(
            id=s_id, name=f"Skill {s_id}", description="...", category="...", repo="..."
        )
        coll_path = get_collection_dir() / s_id
        coll_path.mkdir(parents=True)
        with open(coll_path / "_meta.json", "w") as f:
            json.dump(skill.to_dict(), f)

    collected = collection.list_collected_skills()
    assert len(collected) == 2
    ids = [s.id for s in collected]
    assert "skill-1" in ids
    assert "skill-2" in ids


def test_list_collected_skills_empty(clean_storage):
    assert collection.list_collected_skills() == []
