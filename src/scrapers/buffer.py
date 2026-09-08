"""
Scraper for Buffer's careers page (https://buffer.com/journey).

The page is server-rendered: each open role is an <a href="/journey/{uuid}"> link grouped under a department heading
(e.g. "Engineering"). No API or auth needed - a plain GET returns everything.

Buffer is fully remote, so location is always "Remote".
"""

import re

from bs4 import BeautifulSoup

from src import constants as cons
from src.models import (
    Company,
    Job,
)
from src.registry import register
from src.scrapers.base import BaseScraper


@register("buffer")
class BufferScraper(BaseScraper):
    JOBS_URL: str = "https://buffer.com/journey"
    JOB_RE: re.Pattern[str] = re.compile(
        r"/journey/("
        r"[0-9a-f]{8}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{12}"
        r")"
    )

    def __init__(self, company: Company) -> None:
        super().__init__()
        self.company = company

    def job_url(self, job_id: str) -> str:
        return f"{self.JOBS_URL}/{job_id}"

    def fetch(self) -> list[Job]:
        html = self.get_html(self.JOBS_URL)
        soup = BeautifulSoup(html, "html.parser")

        jobs = []
        seen = set()

        for link in soup.select('a[href*="/journey/"]'):
            href = link.get("href", "")
            match = self.JOB_RE.search(href)
            if not match:
                continue
            job_id = match.group(1)
            if job_id in seen:
                continue
            seen.add(job_id)

            text = " ".join(link.get_text(" ", strip=True).split())
            title = re.sub(
                r"\s*\*?Apply\s*\*?$",
                "",
                text,
            ).strip()

            heading = link.find_previous(["h2", "h3", "h4"])
            department = heading.get_text(strip=True) if heading else ""
            jobs.append(
                Job(
                    company=self.company.name,
                    id=job_id,
                    title=title,
                    url=self.job_url(job_id),
                    location=cons.Location.REMOTE,
                    department=department,
                )
            )

        return jobs
