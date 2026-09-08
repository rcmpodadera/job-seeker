from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Company:
    """One entry from companies.yaml."""

    name: str
    ats: str
    slug: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Job:
    """A single open position, normalised across every source."""

    company: str
    id: str
    title: str
    url: str
    location: str = ""
    department: str = ""

    @property
    def key(self) -> str:
        """Globally unique key used to detect previously seen jobs."""
        return f"{self.company}:{self.id}"

    def as_text(self) -> str:
        """Return searchable job fields as lowercase text."""
        return " ".join([self.title, self.location, self.department]).lower()
