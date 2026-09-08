from enum import StrEnum


class Location(StrEnum):
    REMOTE = "remote"


HTTP_USER_AGENT = "personal-job-alert/1.0"
HTTP_REQUEST_TIMEOUT = 20.0

LOG_FORMAT = "%(levelname)s: %(message)s"
