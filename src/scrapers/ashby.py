"""
Generic Ashby scraper.

Works for ANY company on Ashby - set `ats: ashby` and the board `slug`
(the last path segment of jobs.ashbyhq.com/<slug>) in companies.yaml.

Public job-board API (no key needed):
    GET https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true

    -> {"jobs": [ {...}, ... ]}
"""

from src.models import (
    Company,
    Job,
)
from src.registry import register
from src.scrapers.base import BaseScraper


@register("ashby")
class AshbyScraper(BaseScraper):
    def __init__(self, company: Company) -> None:
        super().__init__()
        if not company.slug:
            raise ValueError(f"{company.name}: ashby needs a 'slug'")
        self.company = company

    @property
    def job_board_url(self) -> str:
        return f"https://api.ashbyhq.com/posting-api/job-board/{self.company.slug}?includeCompensation=true"

    def fetch(self) -> list[Job]:
        data = self.get_json(self.job_board_url)
        jobs = []
        for job in data.get("jobs", []):
            if job.get("isListed") is False:
                continue
            job_url = job.get("jobUrl") or job.get("applyUrl") or ""
            jobs.append(
                Job(
                    company=self.company.name,
                    id=str(job.get("id") or job_url),
                    title=(job.get("title", "")).strip(),
                    url=job_url,
                    location=job.get("location", ""),
                    department=(job.get("department", "") or job.get("team", "")),
                )
            )
        return jobs
