"""
Scraper for the JOIN (join.com) job widget, which serves a clean JSON API:

    GET https://join.com/api/widget/jobs -> {"jobs": [{...}, ...]}
    (or a bare [{...}, ...] list)

The endpoint needs an `access-token` header (a company-scoped JWT from the embedding widget) and browser-context headers
the API validates (notably the sec-fetch-* set). Put the token in companies.yaml; the context headers below replicate a
real browser request and can be overriden per company:

    - name: Join
      ats: join
      headers:
        access-token: "<jwt from the careers page's jobs request>"

Each job maps: title, url, place->location, category->department; the id is the trailing path segment of the job url.
"""

from src.models import (
    Company,
    Job,
)
from src.registry import register
from src.scrapers.base import BaseScraper


@register("join")
class JoinScraper(BaseScraper):
    BASE_URL = "https://join.com/api/widget/jobs"
    BASE_HEADERS = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://join.com/en/careers",
        "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/152.0.0.0 Safari/537.36"
        ),
    }

    def __init__(self, company: Company) -> None:
        super().__init__()
        self.company = company

    @property
    def headers(self) -> dict[str, str]:
        return {**self.BASE_HEADERS, **self.company.extra.get("headers", {})}

    def job_id(self, job_url: str, title: str) -> str:
        if job_url:
            return job_url.rstrip("/").split("/")[-1]
        return title

    def fetch(self) -> list[Job]:
        data = self.get_json(
            self.BASE_URL,
            headers=self.headers,
        )
        postings = data.get("jobs", []) if isinstance(data, dict) else data
        jobs = []
        for posting in postings:
            job_url = posting.get("url", "")
            title = posting.get("title", "").strip()
            jobs.append(
                Job(
                    company=self.company.name,
                    id=self.job_id(job_url, title),
                    title=title,
                    url=job_url,
                    location=posting.get("place", ""),
                    department=posting.get("category", ""),
                )
            )
        return jobs
