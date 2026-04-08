import tomllib
import tomli_w
import httpx
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from skillscraper.models.repo import Repo
from skillscraper.models.skill import Skill
from skillscraper.core.paths import get_repos_dir, init_storage
from skillscraper.core.utils import atomic_write_binary


class RepoManager:
    def __init__(self):
        init_storage()
        self.sources_file = get_repos_dir() / "sources.toml"
        self.repos: Dict[str, Repo] = self._load_repos()

    def _load_repos(self) -> Dict[str, Repo]:
        if not self.sources_file.exists():
            return {}

        with open(self.sources_file, "rb") as f:
            data = tomllib.load(f)

        repos = {}
        for repo_id, repo_data in data.get("repos", {}).items():
            repos[repo_id] = Repo.from_dict(repo_data)
        return repos

    def _save_repos(self):
        # Filter out None values as tomli-w doesn't support them
        repos_dict = {}
        for repo_id, repo in self.repos.items():
            repo_dict = repo.to_dict()
            repos_dict[repo_id] = {k: v for k, v in repo_dict.items() if v is not None}

        data = {"repos": repos_dict}

        def write_toml(f):
            tomli_w.dump(data, f)

        atomic_write_binary(self.sources_file, write_toml)

    def add_repo(self, repo_id: str, repo_data: Dict[str, Any]):
        repo_data["id"] = repo_id
        self.repos[repo_id] = Repo(**repo_data)
        self._save_repos()

    def remove_repo(self, repo_id: str):
        if repo_id in self.repos:
            del self.repos[repo_id]
            self._save_repos()

    def toggle_repo(self, repo_id: str, enabled: bool):
        if repo_id in self.repos:
            self.repos[repo_id].enabled = enabled
            self._save_repos()

    async def fetch_skills(self, repo: Repo) -> List[Skill]:
        if repo.type == "local":
            return self._scan_local_repo(repo)

        if repo.type == "single-skill":
            return await self._fetch_single_skill_repo(repo)

        if repo.index_path:
            return await self._fetch_index_repo(repo)

        return await self._scan_remote_repo(repo)

    async def _request_with_retry(
        self, client: httpx.AsyncClient, url: str, retries: int = 3
    ) -> httpx.Response:
        for i in range(retries):
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                if i == retries - 1:
                    raise e
                # Exponential backoff could be added here
        raise httpx.RequestError("Max retries reached")

    async def _fetch_index_repo(self, repo: Repo) -> List[Skill]:
        url = f"{repo.url.rstrip('/')}/{repo.index_path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await self._request_with_retry(client, url)
            data = response.json()

        skills = []
        for item in data:
            item["repo"] = repo.id
            skills.append(Skill.from_dict(item))
        return skills

    async def _fetch_single_skill_repo(self, repo: Repo) -> List[Skill]:
        # Single skill means the root is the skill
        url_base = repo.url.rstrip("/")
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await self._request_with_retry(
                    client, f"{url_base}/metadata.json"
                )
                data = resp.json()
                data["repo"] = repo.id
                return [Skill.from_dict(data)]
            except Exception:
                pass

        # Fallback: try to infer from SKILL.md or just use repo id
        return [
            Skill(
                id=repo.id,
                name=repo.id,
                description="Single skill repo",
                category="Uncategorized",
                repo=repo.id,
            )
        ]

    async def _scan_remote_repo(self, repo: Repo) -> List[Skill]:
        # Clone to temp dir and scan
        repo_dir = get_repos_dir() / repo.id
        if repo_dir.exists():
            shutil.rmtree(repo_dir)

        subprocess.run(
            ["git", "clone", "--depth", "1", repo.url, str(repo_dir)],
            check=True,
            capture_output=True,
        )

        skills = self._scan_directory(repo_dir, repo)

        # We keep the clone for now, or we can delete it.
        # The prompt doesn't specify, but typically we'd clean up or cache.
        return skills

    def _scan_local_repo(self, repo: Repo) -> List[Skill]:
        repo_dir = Path(repo.path)
        if not repo_dir.exists():
            return []
        return self._scan_directory(repo_dir, repo)

    def _scan_directory(self, directory: Path, repo: Repo) -> List[Skill]:
        skills = []
        # Scan for directories containing SKILL.md
        for path in directory.rglob("SKILL.md"):
            skill_dir = path.parent
            skill_id = skill_dir.name

            # Try to find metadata.json in the same dir
            metadata_file = skill_dir / "metadata.json"
            if metadata_file.exists():
                import json

                with open(metadata_file, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        data["repo"] = repo.id
                        skills.append(Skill.from_dict(data))
                        continue
                    except Exception:
                        pass

            # Fallback: create basic Skill from directory name
            skills.append(
                Skill(
                    id=skill_id,
                    name=skill_id,
                    description="Scanned skill",
                    category="Uncategorized",
                    repo=repo.id,
                )
            )

        return skills
