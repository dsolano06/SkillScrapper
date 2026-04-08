from typing import List, Tuple, Optional
from rapidfuzz import process, fuzz
from skillscraper.core.library import get_all_skills
from skillscraper.models.skill import Skill


def search_skills(
    query: str, category: Optional[str] = None
) -> List[Tuple[Skill, float]]:
    """
    Searches for skills across name, description, and ID using fuzzy matching.
    """
    all_skills = get_all_skills()

    # Filter by category if provided
    if category:
        all_skills = [s for s in all_skills if s.category.lower() == category.lower()]

    if not all_skills:
        return []

    # Create a map of search text to skill object
    # This allows us to use rapidfuzz's optimized process.extract
    search_map = {f"{s.id} {s.name} {s.description}".lower(): s for s in all_skills}
    search_texts = list(search_map.keys())

    # Extract top matches
    results = process.extract(
        query.lower(), search_texts, scorer=fuzz.partial_ratio, limit=None
    )

    # Map back to Skill objects
    return [(search_map[text], score) for text, score, _ in results]
