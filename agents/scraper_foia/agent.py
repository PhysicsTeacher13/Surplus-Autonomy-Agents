from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common.base_agent import BaseAgent, utc_now_iso
from common.artifacts import write_json, artifact_ref, write_text
from common.http_client import HttpClient
from common.fixtures import FixtureStore

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    BeautifulSoup = None


class ScraperFOIAAgent(BaseAgent):
    """
    Web Scraping / FOIA Agent (public records first).
    Colab-safe: supports Network OFF using fixtures, Network ON using live HTTP.

    Outputs:
    - discovered downloadable links (pdf/csv/xlsx/html)
    - extracted rows (very basic v0) when HTML tables exist
    - evidence artifacts (raw html snapshot + parsed json)
    """

    agent_name = "scraper_foia"
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
        seed_url = payload.get("seed_url")
        fixture_key = (payload.get("fixture_keys") or {}).get("html")

        if not seed_url and network == "ON":
            raise ValueError("seed_url required when network=ON")

        http = HttpClient(network=network, fixtures=self._fixtures)
        html = http.get_text(url=seed_url or "https://example.invalid", fixture_key=fixture_key)

        raw_path = artifact_dir / "raw.html"
        write_text(raw_path, html)

        links: List[str] = []
        rows: List[Dict[str, Any]] = []
        parse_note = "bs4 not installed"

        if BeautifulSoup is not None:
            parse_note = "ok"
            soup = BeautifulSoup(html, "lxml") if "lxml" in str(type(BeautifulSoup)) else BeautifulSoup(html, "html.parser")

            for a in soup.find_all("a"):
                href = a.get("href") or ""
                if any(href.lower().endswith(ext) for ext in (".pdf", ".csv", ".xlsx", ".xls")):
                    links.append(href)

            # Very basic: parse first table if present
            table = soup.find("table")
            if table:
                headers = [th.get_text(" ", strip=True) for th in table.find_all("th")]
                for tr in table.find_all("tr"):
                    tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
                    if headers and tds and len(tds) <= len(headers):
                        row = {headers[i]: tds[i] for i in range(len(tds))}
                        rows.append(row)

        data = {
            "seed_url": seed_url,
            "network": network,
            "parse_note": parse_note,
            "download_links": links[:200],
            "table_rows": rows[:500],
            "ts": utc_now_iso(),
        }

        out = artifact_dir / "scrape_result.json"
        write_json(out, data)

        artifacts = [
            artifact_ref(raw_path, "html", "raw_html_snapshot"),
            artifact_ref(out, "json", "scrape_result"),
        ]
        audit = [{"action": "scrape_or_fixture_load", "object": "source_site", "result": "ok", "ts": utc_now_iso()}]
        return data, artifacts, audit
