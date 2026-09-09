"""
Generic Greenhouse scraper.

Works for ANY company on Greenhouse - set `ats: greenhouse` and the board `slug`
(the last path segment of boards-api.greenhouse.io/v1/boards/<slug>/jobs) in companies.yaml.

Public job-board API (no key needed):
    GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs

    -> {"jobs": [ {...}, ... ]}
"""

from src.models import (
    Company,
    Job,
)
from src.registry import register
from src.scrapers.base import BaseScraper


@register("greenhouse")
class GreenhouseScraper(BaseScraper):
    def __init__(self, company: Company) -> None:
        super().__init__()
        if not company.slug:
            raise ValueError(f"{company.name}: greenhouse needs a 'slug'")
        self.company = company

    @property
    def job_board_url(self) -> str:
        return f"https://boards-api.greenhouse.io/v1/boards/{self.company.slug}/jobs"

    def fetch(self) -> list[Job]:
        data = self.get_json(self.job_board_url)
        jobs = []
        for job in data.get("jobs", []):
            job_url = job.get("absolute_url", "")
            title, _, department = job.get("title", "").partition("-")
            jobs.append(
                Job(
                    company=self.company.name,
                    id=str(job.get("id") or job_url),
                    title=title.strip(),
                    url=job_url,
                    location=job.get("location", {}).get("name", ""),
                    department=department.strip(),
                )
            )
        return jobs
