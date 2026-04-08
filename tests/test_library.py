import pytest
import json
from skillscraper.core import library
from skillscraper.models.skill import Skill
from skillscraper.core.paths import get_index_file


@pytest.fixture
def sample_skills():
    return [
        Skill(
            id="skill-1",
            name="Skill One",
            description="Desc 1",
            category="Cat 1",
            repo="repo-1",
        ),
        Skill(
            id="skill-2",
            name="Skill Two",
            description="Desc 2",
            category="Cat 2",
            repo="repo-2",
        ),
    ]


def test_get_all_skills_empty(clean_storage):
    assert library.get_all_skills() == []


def test_get_all_skills_with_data(clean_storage, sample_skills):
    # Setup index file
    index_path = get_index_file()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump([s.to_dict() for s in sample_skills], f)

    skills = library.get_all_skills()
    assert len(skills) == 2
    assert skills[0].id == "skill-1"
    assert skills[1].id == "skill-2"


def test_get_skill_by_id(clean_storage, sample_skills):
    index_path = get_index_file()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump([s.to_dict() for s in sample_skills], f)

    skill = library.get_skill_by_id("skill-1")
    assert skill is not None
    assert skill.name == "Skill One"

    skill_none = library.get_skill_by_id("non-existent")
    assert skill_none is None


def test_update_skill_status(clean_storage, sample_skills):
    index_path = get_index_file()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump([s.to_dict() for s in sample_skills], f)

    # Update status
    success = library.update_skill_status("skill-1", in_collection=True)
    assert success is True

    # Verify
    skill = library.get_skill_by_id("skill-1")
    assert skill.in_collection is True

    # Update status again
    library.update_skill_status("skill-1", in_collection=False)
    skill = library.get_skill_by_id("skill-1")
    assert skill.in_collection is False

    # Update non-existent
    success_none = library.update_skill_status("non-existent", in_collection=True)
    assert success_none is False
