import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src import constants as cons
from src.models import Job


class BaseScraper:
    """Base class for all scrapers."""

    def __init__(self) -> None:
        self.session = self._make_session()

    def _make_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({"User-Agent": cons.HTTP_USER_AGENT, "Accept": "application/json, text/html"})
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def run(self) -> list[Job]:
        return self.fetch()

    def fetch(self) -> list[Job]:
        """Fetch job listings. Must be implemented by subclasses."""
        raise NotImplementedError

    def get_json(self, url: str, **kwargs) -> dict:
        response = self.session.get(url, timeout=cons.HTTP_REQUEST_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_html(self, url: str, **kwargs) -> str:
        response = self.session.get(url, timeout=cons.HTTP_REQUEST_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response.text

    def impersonate_get(
        self,
        url: str,
        as_json: bool = False,
        **kwargs,
    ):
        """
        Fetch a URL while impersonating a real Chrome TLS/HTTP2 fingerprint.

        Requires curl_cffi. It is imported lazily so scrapers that don't need it don't have to depend on it.
        """
        from curl_cffi import requests as cffi

        response = cffi.get(url, impersonate="chrome", timeout=cons.HTTP_REQUEST_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response.json() if as_json else response.text
