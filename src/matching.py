"""Match jobs against the user's profile."""

from src.config import Profile
from src.models import Job


def matches(job: Job, profile: Profile) -> bool:
    match = True
    text = job.as_text().lower()

    if profile.include and not any(word in text for word in profile.include):
        return not match

    if any(word in text for word in profile.exclude):
        return not match

    if profile.locations and not any(location in text for location in profile.locations):
        return not match

    return match
