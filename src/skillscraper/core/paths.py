from pathlib import Path
from typing import List
import platformdirs

APP_NAME = "skillscraper"


def get_base_dir() -> Path:
    """Returns the root directory for SkillScraper data."""
    return Path(platformdirs.user_data_dir(APP_NAME))


def get_library_dir() -> Path:
    """Returns the directory where skills are stored."""
    return get_base_dir() / "library"


def get_collection_dir() -> Path:
    """Returns the directory for user collections."""
    return get_base_dir() / "collection"


def get_repos_dir() -> Path:
    """Returns the directory for temporary repository clones."""
    return get_base_dir() / "repos"


def get_combos_dir() -> Path:
    """Returns the directory for skill combinations."""
    return get_base_dir() / "combos"


def get_index_file() -> Path:
    """Returns the path to the library index file."""
    return get_library_dir() / "index.json"


def get_config_file() -> Path:
    """Returns the path to the main configuration file."""
    return get_base_dir() / "config.toml"


def get_targets_file() -> Path:
    """Returns the path to the targets configuration file."""
    return get_base_dir() / "targets.toml"


def init_storage() -> None:
    """Ensures all required SkillScraper directories exist on the filesystem."""
    dirs_to_create: List[Path] = [
        get_library_dir(),
        get_collection_dir(),
        get_repos_dir(),
        get_combos_dir(),
    ]
    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)
