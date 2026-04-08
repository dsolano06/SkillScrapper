import pytest
import shutil
from pathlib import Path
from unittest.mock import patch


@pytest.fixture(scope="session")
def temp_storage(tmp_path_factory):
    """Creates a temporary directory for SkillScraper storage."""
    return tmp_path_factory.mktemp("skillscraper_storage")


@pytest.fixture(autouse=True)
def mock_paths(temp_storage, monkeypatch):
    """Mocks platformdirs.user_data_dir to return the temporary storage path."""
    monkeypatch.setattr(
        "platformdirs.user_data_dir", lambda app_name: str(temp_storage)
    )
    # Also ensure we are in a clean state for each test if needed,
    # but temp_storage is session scoped. For individual tests,
    # we might want to clear the directories.


@pytest.fixture
def clean_storage(temp_storage):
    """Clears the storage directories before each test."""
    for item in temp_storage.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    return temp_storage
