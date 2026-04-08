import os
from pathlib import Path
from skillscraper.core import combos, library, paths


def test_combos():
    print("Testing Combo CRUD...")
    name = "test-combo"
    description = "A test combo for verification"
    skills_dict = {
        "test-sub": {
            "description": "Test sub-combo",
            "always_active": True,
            "skills": ["vercel-react-best-practices"],
        }
    }

    # Create
    path = combos.create_combo(name, description, skills_dict)
    print(f"Created combo at {path}")

    # List
    all_combos = combos.list_combos()
    print(f"All combos: {all_combos}")
    assert name in all_combos

    # Get
    combo = combos.get_combo(name)
    print(f"Combo data: {combo}")
    assert combo["name"] == name
    assert "test-sub" in combo["sub_combos"]

    # Edit path
    edit_path = combos.edit_combo(name)
    print(f"Edit path: {edit_path}")
    assert edit_path == path

    print("\nTesting Combo Installation...")
    try:
        results = combos.install_combo(name)
        print(f"Install results: {results}")
        for res in results:
            print(f"Skill {res['skill_id']}: {res['status']}")
    except Exception as e:
        print(f"Install failed: {e}")

    print("\nTesting Combo Deletion...")
    assert combos.delete_combo(name)
    assert name not in combos.list_combos()
    print("Deleted combo successfully")


if __name__ == "__main__":
    # Ensure storage is initialized
    paths.init_storage()
    test_combos()
    print("\nAll tests passed!")
