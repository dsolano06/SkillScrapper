import os
import json
from pathlib import Path
from skillscraper.core.paths import init_storage, get_index_file, get_collection_dir
from skillscraper.models.skill import Skill
from skillscraper.core import library, collection, search


def test_core_mvp():
    # Setup
    init_storage()
    index_path = get_index_file()

    # Create a mock index.json
    mock_skills = [
        Skill(
            id="test-skill-1",
            name="Test Skill One",
            description="This is a test skill one",
            category="test",
        ),
        Skill(
            id="test-skill-2",
            name="Test Skill Two",
            description="Another test skill",
            category="test",
        ),
        Skill(
            id="real-skill",
            name="Real Skill",
            description="A real skill",
            category="real",
            repo="antigravity",
        ),
    ]
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump([s.to_dict() for s in mock_skills], f, indent=4)

    print("--- Testing Search ---")
    results = search.search_skills("Test One")
    print(f"Search results: {len(results)}")
    assert len(results) > 0
    assert results[0][0].id == "test-skill-1"
    print("Search test passed!")

    print("\n--- Testing Download ---")
    # Use a skill that we can actually "download" (mocking the network or using a real one)
    # For this test, we can mock the network or just check if the files are created.
    # Since download_skill uses httpx, it will try to fetch from GitHub.
    # To avoid network dependency in a basic unit test, we might want to mock httpx.
    # But let's try with a real one from antigravity if it exists, or just mock it.

    # Let's mock httpx.Client.get for this test
    import httpx
    from unittest.mock import patch, MagicMock

    with patch("httpx.Client.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = "# Mock Skill Content"
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response

        skill = library.get_skill_by_id("real-skill")
        success = collection.download_skill(skill)
        print(f"Download success: {success}")
        assert success is True

        # Check if files exist
        coll_path = get_collection_dir() / "real-skill"
        assert (coll_path / "SKILL.md").exists()
        assert (coll_path / "_meta.json").exists()

        # Check if library flag updated
        updated_skill = library.get_skill_by_id("real-skill")
        assert updated_skill.in_collection is True
        print("Download test passed!")

    print("\n--- Testing Remove ---")
    success = collection.remove_skill("real-skill")
    print(f"Remove success: {success}")
    assert success is True

    # Check if files deleted
    coll_path = get_collection_dir() / "real-skill"
    assert not coll_path.exists()

    # Check if library flag updated
    updated_skill = library.get_skill_by_id("real-skill")
    assert updated_skill.in_collection is False
    print("Remove test passed!")

    print("\nAll MVP core tests passed!")


if __name__ == "__main__":
    test_core_mvp()
