"""
A tiny registry that maps an ATS name to its scraper class.

Scrapers register themselves with the @register("<ats>") decorator, so adding a new platform never requires editing it.
"""

from collections.abc import Callable

from src.models import Company
from src.scrapers.base import BaseScraper

ScraperClass = Callable[[Company], BaseScraper]

_REGISTRY: dict[str, ScraperClass] = {}


def register(ats: str) -> Callable[[ScraperClass], ScraperClass]:
    def decorator(scraper: ScraperClass) -> ScraperClass:
        key = ats.lower()
        if key in _REGISTRY:
            raise ValueError(f"Scraper for ATS '{ats}' is already registered.")
        _REGISTRY[key] = scraper
        return scraper

    return decorator


def get_scraper(ats: str) -> ScraperClass:
    key = ats.lower()
    try:
        return _REGISTRY[key]
    except KeyError as e:
        known = ", ".join(sorted(_REGISTRY))
        raise ValueError(f"No scraper registered for ATS '{ats}'. Known: {known}") from e


def known_ats() -> list[str]:
    return sorted(_REGISTRY)
