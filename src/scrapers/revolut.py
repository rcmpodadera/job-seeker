"""
Scraper for Revolut's careers site (revolut.com/careers).

Revolut is a Next.js app: the full list of roles isn't in the page HTML. Instead, it is available in:

    /_next/data/<buildId>/en-GB/careers.json  ->  pageProps.positions[]

The <buildId> changes on every deploy, so we read the careers HTML first to get the current buildId, then fetch the
JSON.

Revolut sits behind Cloudflare, which blocks plain requests at the TLS layer, so we use curl_cffi's Chrome
impersonation.

If the HTML fetch is blocked, the build ID can be pinned in companies.yaml:

    - name: Revolut
      ats: revolut
      build_id: "<buildId>"

Each position provides an id, title, team, and locations.

Public URL:

    /careers/position/<slug>-<uuid>/

The slug is derived from the job title.
"""

import re

from src.models import (
    Company,
    Job,
)
from src.registry import register
from src.scrapers.base import BaseScraper


@register("revolut")
class RevolutScraper(BaseScraper):
    BASE_URL: str = "https://www.revolut.com/careers"
    BUILD_ID_RE: re.Pattern[str] = re.compile(r'"buildId":"([^"]+)"')

    def __init__(self, company: Company) -> None:
        super().__init__()
        self.company = company

    def _build_id(self) -> str:
        pinned = self.company.extra.get("build_id")
        if pinned:
            return pinned
        html = self.impersonate_get(self.BASE_URL)
        match = self.BUILD_ID_RE.search(html)
        if not match:
            raise ValueError("Revolut build ID not found in HTML")
        return match.group(1)

    def _slug(self, title: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    def jobs_url(self, build_id: str) -> str:
        return f"https://www.revolut.com/_next/data/{build_id}/en-GB/careers.json"

    def job_url(self, title: str, job_id: str) -> str:
        slug = self._slug(title)
        return f"{self.BASE_URL}/position/{slug}-{job_id}/"

    def fetch(self) -> list[Job]:
        build_id = self._build_id()
        url = self.jobs_url(build_id)
        data = self.impersonate_get(url, as_json=True)
        positions = data.get("pageProps", {}).get("positions", [])

        jobs = []

        for position in positions:
            job_id = position.get("id")
            if not job_id:
                continue
            title = position.get("text", "").strip()
            locations = [location.get("name", "") for location in position.get("locations", []) if location.get("name")]
            location = ", ".join(dict.fromkeys(locations))

            jobs.append(
                Job(
                    company=self.company.name,
                    id=job_id,
                    title=title,
                    url=self.job_url(title, job_id),
                    location=location,
                    department=position.get("team", ""),
                )
            )
        return jobs
