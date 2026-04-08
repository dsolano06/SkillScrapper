import os
import shutil
from pathlib import Path
from skillscraper.core import targets, paths


def test_targets():
    # Setup temporary directories for testing
    test_base = Path("test_skillscraper_data")
    test_base.mkdir(exist_ok=True)

    # Monkeypatch paths to use our test directory
    paths.get_base_dir = lambda: test_base
    paths.get_targets_file = lambda: test_base / "targets.toml"
    paths.get_collection_dir = lambda: test_base / "collection"

    # Initialize storage
    paths.init_storage()

    # 1. Test scan_targets (should be mostly empty unless we have the dirs)
    print("Testing scan_targets...")
    new_targets = targets.scan_targets()
    print(f"Newly registered targets: {new_targets}")

    # 2. Manually add a target for testing
    print("\nAdding test target...")
    target_path = test_base / "test_target"
    target_path.mkdir(parents=True, exist_ok=True)

    # We can't easily use _save_targets since it's private,
    # but we can just manipulate the file or use a public method if I had one.
    # Let's add a target by manually writing to the toml since I'm in a test script.
    import tomli_w

    targets_data = {
        "targets": {
            "test-target": {
                "path": str(target_path),
                "strategy": "symlink",
                "auto": False,
            }
        }
    }
    with open(paths.get_targets_file(), "wb") as f:
        tomli_w.dump(targets_data, f)

    # 3. Setup a skill in collection
    print("\nSetting up skill in collection...")
    skill_id = "test-skill"
    skill_dir = paths.get_collection_dir() / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("Test Skill Content")
    (skill_dir / "_meta.json").write_text('{"id": "test-skill"}')

    # 4. Test install_skill
    print("\nInstalling skill...")
    installed = targets.install_skill(skill_id, target_name="test-target")
    print(f"Installed in: {installed}")

    dest_path = target_path / skill_id
    if dest_path.exists():
        print("Success: Skill projected to target!")
        if dest_path.is_symlink():
            print("Strategy used: symlink")
        else:
            print("Strategy used: copy")
    else:
        print("Error: Skill not projected!")

    # 5. Test get_installed_skills
    print("\nChecking installed skills...")
    installed_skills = targets.get_installed_skills("test-target")
    print(f"Installed skills: {installed_skills}")
    assert skill_id in installed_skills

    # 6. Test uninstall_skill
    print("\nUninstalling skill...")
    uninstalled = targets.uninstall_skill(skill_id, target_name="test-target")
    print(f"Uninstalled from: {uninstalled}")
    if not dest_path.exists():
        print("Success: Skill removed from target!")
    else:
        print("Error: Skill still exists in target!")

    # Cleanup
    shutil.rmtree(test_base)
    print("\nCleanup complete.")


if __name__ == "__main__":
    try:
        test_targets()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
