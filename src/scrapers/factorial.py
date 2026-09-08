"""
Scraper for Factorial's own careers page (careers.factorialhr.com), which is a server-rendered ("Powered by Factorial").

Each open role is a small card, grouped under a location heading, with an "Apply now" link to /job_posting/<slug>-<id>.

No API or auth needed. The card renders as a few text lines:
    title, (department), (work-mode), "Apply now"

We read those lines to pull title + department, and take the location from the nearest heading above the card.

Other Factorial-hosted boards share this layout, so `url` is overridable:

    - name: SomeCo
      ats: factorial
      url: https://careers.someco.com/
"""

import re

from bs4 import BeautifulSoup

from src.models import (
    Company,
    Job,
)
from src.registry import register
from src.scrapers.base import BaseScraper


@register("factorial")
class FactorialScraper(BaseScraper):
    BASE_URL: str = "https://careers.factorialhr.com/"
    JOB_RE: re.Pattern[str] = re.compile(r"/job_posting/.*?(\d+)/?$")
    WORK_MODES: list[str] = ["remote", "onsite", "hybrid"]

    def __init__(self, company: Company) -> None:
        super().__init__()
        self.company = company

    def job_url(self, href: str) -> str:
        return href if href.startswith("http") else f"{self.BASE_URL}{href}"

    def _slug_title(self, href: str) -> str:
        match = re.search(
            r"/job_posting/(.+?)-\d+/?$",
            href,
        )
        return match.group(1).replace("-", " ").title() if match else ""

    def _card_lines(self, anchor) -> list[str]:
        """
        Walk up to the tight job card: the nearest ancestor whose text is a few lines ending in 'Apply now'.
        """
        node = anchor
        for _ in range(6):
            node = node.parent
            if node is None:
                break
            lines = [line.strip() for line in node.get_text("\n").split("\n") if line.strip()]
            if lines and lines[-1].lower().startswith("apply") and 2 <= len(lines) <= 6:
                return lines
        return []

    def fetch(self) -> list[Job]:
        html = self.get_html(self.BASE_URL)
        soup = BeautifulSoup(html, "html.parser")

        jobs = []
        seen = set()

        for link in soup.select('a[href*="/job_posting/"]'):
            href = link.get("href", "")
            match = self.JOB_RE.search(href)
            if not match:
                continue

            job_id = match.group(1)
            if job_id in seen:
                continue
            seen.add(job_id)

            content = [line for line in self._card_lines(link) if not line.lower().startswith("apply")]
            title = content[0] if content else self._slug_title(href)
            department = next(
                (line for line in content[:1] if line.lower() not in self.WORK_MODES),
                "",
            )
            heading = link.find_previous(["h2", "h3"])
            location = heading.get_text(strip=True) if heading else ""
            jobs.append(
                Job(
                    company=self.company.name,
                    id=job_id,
                    title=title,
                    url=self.job_url(href),
                    location=location,
                    department=department,
                )
            )
        return jobs
