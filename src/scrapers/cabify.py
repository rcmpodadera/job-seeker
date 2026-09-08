"""
Custom scraper for Cabify, whose careers site is bespoke server-rendered HTML rather than a standard ATS.

Jobs live as <a href=".../job/{id}"> links, with the text formatted as:

    "<title> <department> <location>"

We split that by anchoring on the END of the string: first peel off a known office (location), then a known department,
and whatever remains is the title.

Anchoring on the end avoids matching a department word that also appears inside the title.
"""

import re

from bs4 import BeautifulSoup

from src.models import (
    Company,
    Job,
)
from src.registry import register
from src.scrapers.base import BaseScraper


@register("cabify")
class CabifyScraper(BaseScraper):
    BASE_URL: str = "https://cabify.careers"
    JOBS_URL: str = "https://cabify.careers/es/jobs?search=&office=&department="
    JOB_RE: re.Pattern[str] = re.compile(r"/job/(\d+)")
    OFFICES: list[str] = [
        "Barcelona",
        "Bogotá",
        "Buenos Aires",
        "Ciudad de México",
        "Cordoba",
        "Lima",
        "Madrid",
        "Mendoza",
        "Montevideo",
        "Quito",
        "Santiago de Chile",
        "Sevilla",
        "Valencia",
        "Chile",
    ]
    DEPARTMENTS: list[str] = [
        "Advertising & Integrations",
        "B2B",
        "Brand, Media & Creative",
        "Cabify Logistics",
        "Communications and Public Affairs",
        "Customer Experience & Operations",
        "Diversity & EX",
        "Diversity",
        "Engineering",
        "Finance",
        "Fleet",
        "Gateways & Fraud",
        "Global Internal Projects",
        "Growth",
        "Information Technology",
        "Legal",
        "Management - Leadership",
        "Management - Other",
        "Marketing",
        "Office Management",
        "Own Fleet Operations",
        "People",
        "Product",
        "Public Affairs",
        "Public Relations",
        "Sustainability",
        "Technology",
    ]

    def __init__(self, company: Company) -> None:
        super().__init__()
        self.company = company

    def job_url(self, href: str) -> str:
        return href if href.startswith("http") else f"{self.BASE_URL}{href}"

    def _strip_suffix(self, text: str, options: list[str]) -> tuple[str, str]:
        """Strip a known suffix from the text if it matches any of the options."""
        for option in options:
            if text.endswith(option):
                return (
                    text[: -len(option)].strip(" -,"),
                    option,
                )
        return text, ""

    def _split(self, text: str) -> tuple[str, str, str]:
        """Split a job label into title, department, and location."""
        offices = sorted(self.OFFICES, key=len, reverse=True)
        departments = sorted(self.DEPARTMENTS, key=len, reverse=True)
        rest, location = self._strip_suffix(text, offices)
        rest, department = self._strip_suffix(rest, departments)
        return rest.strip(), department, location

    def fetch(self) -> list[Job]:
        html = self.get_html(self.JOBS_URL)
        soup = BeautifulSoup(html, "html.parser")

        jobs = []

        for link in soup.select('a[href*="/job/"]'):
            href = link.get("href", "")
            match = self.JOB_RE.search(href)
            if not match:
                continue
            job_id = match.group(1)
            text = " ".join(link.get_text(" ", strip=True).split())
            title, department, location = self._split(text)
            jobs.append(
                Job(
                    company=self.company.name,
                    id=job_id,
                    title=title or text,
                    url=self.job_url(href),
                    location=location,
                    department=department,
                )
            )

        return jobs
