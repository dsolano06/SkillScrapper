from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class Skill:
    id: str
    name: str
    description: str
    category: str
    repo: str = "unknown"
    version: str = "1.0.0"
    in_collection: bool = False
    collection_path: Optional[str] = None
    downloaded_at: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        # Filter out keys that are not in the dataclass
        filtered_data = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}

        # Ensure required fields are present
        if "category" not in filtered_data:
            filtered_data["category"] = "Uncategorized"

        return cls(**filtered_data)
