"""Load the two user-facing config files into typed objects."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from src.models import Company

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Profile:
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)


def load_companies(path: Path | None = None) -> list[Company]:
    path = path or ROOT / "companies.yaml"
    raw = yaml.safe_load(path.read_text()) or []
    return [
        Company(
            name=entry.get("name", ""),
            ats=entry.get("ats", ""),
            slug=entry.get("slug", ""),
            extra=entry.get("extra", {}),
        )
        for entry in raw
    ]


def load_profile(path: Path | None = None) -> Profile:
    path = path or ROOT / "profiles.yaml"
    raw = yaml.safe_load(path.read_text()) or {}
    return Profile(
        include=[str(x) for x in raw.get("include", [])],
        exclude=[str(x) for x in raw.get("exclude", [])],
        locations=[str(x) for x in raw.get("locations", [])],
    )
