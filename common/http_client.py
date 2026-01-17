from typing import Optional
import httpx
from .fixtures import FixtureStore

class HttpClient:
    """
    HTTP client with a fixtures-backed mode.

    - network OFF: reads from fixtures using fixture_key
    - network ON: fetches live via httpx
    """

    def __init__(self, network: str, fixtures: Optional[FixtureStore] = None):
        self.network = network
        self.fixtures = fixtures

    def get_text(self, url: str, fixture_key: Optional[str] = None, timeout: int = 30) -> str:
        if self.network == "OFF":
            if not self.fixtures or not fixture_key:
                raise RuntimeError("Network OFF requires fixtures + fixture_key.")
            return self.fixtures.read_text(fixture_key)
        r = httpx.get(url, timeout=timeout, follow_redirects=True)
        r.raise_for_status()
        return r.text
