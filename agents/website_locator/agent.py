from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common.base_agent import BaseAgent, utc_now_iso
from common.artifacts import write_json, artifact_ref
from common.http_client import HttpClient
from common.fixtures import FixtureStore


class WebsiteLocatorAgent(BaseAgent):
    """
    v0 deterministic: reads an HTML fixture (network OFF) and returns
    candidate official website(s) based on simple heuristics.

    Later versions will:
    - derive URLs from courthouse addresses/names
    - query official sources
    - score candidate portals
    """

    agent_name = "website_locator"
    agent_version = "0.1.0"

    def __init__(self, fixtures: Optional[FixtureStore] = None):
        self._fixtures = fixtures

    def _run(
        self,
        payload: Dict[str, Any],
        run_config: Dict[str, Any],
        artifact_dir: Path
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:

        network = run_config.get("network", "OFF")
        http = HttpClient(network=network, fixtures=self._fixtures)

        fixture_key = (payload.get("fixture_keys") or {}).get("homepage_html")
        html = http.get_text(url=payload.get("seed_url", "https://example.invalid"), fixture_key=fixture_key)

        # Very simple heuristic extraction for v0
        # (Use BeautifulSoup later; keep dependency minimal for template.)
        candidates = []
        if "example.gov" in html:
            candidates.append({"url": "https://example.gov/clerk", "confidence": 0.60, "reason": "matched example.gov token"})
        else:
            candidates.append({"url": payload.get("seed_url", ""), "confidence": 0.25, "reason": "fallback seed_url"})

        data = {
            "courthouse_name": payload.get("courthouse_name"),
            "courthouse_address": payload.get("courthouse_address"),
            "seed_url": payload.get("seed_url"),
            "network": network,
            "candidates": candidates,
            "ts": utc_now_iso(),
        }

        out = artifact_dir / "candidate_sites.json"
        write_json(out, data)

        artifacts = [artifact_ref(out, "json", "candidate_sites")]
        audit = [{"action": "derive_sites", "object": "courthouse", "result": "ok", "ts": utc_now_iso()}]

        return data, artifacts, audit
