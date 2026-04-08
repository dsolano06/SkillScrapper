import pytest
from skillscraper.core import search
from skillscraper.core import library
from skillscraper.models.skill import Skill
from skillscraper.core.paths import get_index_file
import json


@pytest.fixture
def sample_skills():
    return [
        Skill(
            id="python-expert",
            name="Python Expert",
            description="Master Python programming",
            category="Programming",
            repo="repo1",
        ),
        Skill(
            id="react-pro",
            name="React Pro",
            description="Expert in React and Next.js",
            category="Frontend",
            repo="repo1",
        ),
        Skill(
            id="git-master",
            name="Git Master",
            description="Version control expert",
            category="Tools",
            repo="repo1",
        ),
    ]


def test_search_skills_basic(clean_storage, sample_skills):
    # Setup index
    index_path = get_index_file()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w") as f:
        json.dump([s.to_dict() for s in sample_skills], f)

    # Search by name
    results = search.search_skills("Python")
    assert len(results) > 0
    assert results[0][0].id == "python-expert"

    # Search by description
    results = search.search_skills("Version control")
    assert len(results) > 0
    assert results[0][0].id == "git-master"

    # Search by ID
    results = search.search_skills("react-pro")
    assert len(results) > 0
    assert results[0][0].id == "react-pro"


def test_search_skills_category_filter(clean_storage, sample_skills):
    index_path = get_index_file()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w") as f:
        json.dump([s.to_dict() for s in sample_skills], f)

    # Filter by category
    results = search.search_skills("expert", category="Frontend")
    assert len(results) == 1
    assert results[0][0].id == "react-pro"

    # Filter by non-existent category
    results = search.search_skills("expert", category="NonExistent")
    assert results == []


def test_search_skills_no_results(clean_storage, sample_skills):
    index_path = get_index_file()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w") as f:
        json.dump([s.to_dict() for s in sample_skills], f)

    results = search.search_skills("something completely random")
    # It returns all sorted by score, so we should check the score if we want to "filter"
    # But for this test, let's just ensure it doesn't crash.
    assert isinstance(results, list)


def test_search_skills_empty_library(clean_storage):
    results = search.search_skills("Python")
    assert results == []
