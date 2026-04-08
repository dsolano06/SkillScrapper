from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Repo:
    id: str
    skills_path: str
    type: str
    url: Optional[str] = None
    path: Optional[str] = None
    index_path: Optional[str] = None
    enabled: bool = True
    priority: int = 1

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
