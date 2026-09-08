"""Run the job-alert pipeline."""

import logging

from src.config import (
    ROOT,
    load_companies,
    load_profile,
)
from src.matching import matches
from src.models import Job
from src.registry import get_scraper
from src.storage import JobStore

logger = logging.getLogger(__name__)


def run(show_all: bool = False) -> list[Job]:

    profile = load_profile()

    snapshot = JobStore(ROOT / "data" / "snapshot.json")
    match_store = JobStore(ROOT / "data" / "matches.json")

    prev = snapshot.load()

    total_jobs: list[Job] = []
    matching_jobs: list[Job] = []

    companies = load_companies()
    for company in companies:
        try:
            scraper = get_scraper(company.ats)(company)
            total_open_jobs = scraper.run()
            match_open_jobs = [job for job in total_open_jobs if matches(job, profile)]
            total_jobs.extend(total_open_jobs)
            matching_jobs.extend(match_open_jobs)
            logger.info(
                f"{company.name}: {len(total_open_jobs)} jobs found. {len(match_open_jobs)} matches your profile."
            )
        except Exception as e:
            logger.error(e, exc_info=True)
            continue

    reported = matching_jobs if show_all else [job for job in matching_jobs if job.key not in prev]

    match_store.save(matching_jobs)
    snapshot.save(total_jobs)

    return reported
