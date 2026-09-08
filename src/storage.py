"""Persistence for job data using JSON on disk."""

import json
from pathlib import Path

from src.config import ROOT
from src.models import Job


class JobStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or ROOT / "data" / "jobs.json"

    def load(self) -> dict[str, dict]:
        """Return previously saved jobs."""
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text())

    def save(self, jobs: list[Job]) -> None:
        """Save the jobs from this run."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            job.key: {
                "company": job.company,
                "title": job.title,
                "location": job.location,
                "url": job.url,
                "department": job.department,
            }
            for job in jobs
        }
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
