import pytest
from pathlib import Path
from skillscraper.core.paths import (
    get_base_dir,
    get_library_dir,
    get_collection_dir,
    get_repos_dir,
    get_combos_dir,
    get_index_file,
    get_config_file,
    get_targets_file,
    init_storage,
)


def test_get_base_dir(mock_paths, temp_storage):
    assert Path(get_base_dir()) == temp_storage


def test_get_library_dir(mock_paths, temp_storage):
    assert get_library_dir() == temp_storage / "library"


def test_get_collection_dir(mock_paths, temp_storage):
    assert get_collection_dir() == temp_storage / "collection"


def test_get_repos_dir(mock_paths, temp_storage):
    assert get_repos_dir() == temp_storage / "repos"


def test_get_combos_dir(mock_paths, temp_storage):
    assert get_combos_dir() == temp_storage / "combos"


def test_get_index_file(mock_paths, temp_storage):
    assert get_index_file() == temp_storage / "library" / "index.json"


def test_get_config_file(mock_paths, temp_storage):
    assert get_config_file() == temp_storage / "config.toml"


def test_get_targets_file(mock_paths, temp_storage):
    assert get_targets_file() == temp_storage / "targets.toml"


def test_init_storage(mock_paths, temp_storage):
    init_storage()
    assert (temp_storage / "library").is_dir()
    assert (temp_storage / "collection").is_dir()
    assert (temp_storage / "repos").is_dir()
    assert (temp_storage / "combos").is_dir()
