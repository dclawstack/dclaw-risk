"""Emerging-risk feed reader.

Default feed: NIST NVD CVE 2.0 JSON API (free, no auth). The reader is
pluggable — call `register_feed(name, fetcher)` to add another source.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx
import structlog

log = structlog.get_logger(__name__)


@dataclass
class EmergingSignal:
    title: str
    source: str
    url: str | None
    summary: str | None
    detected_at: datetime
    impact_score: int


Fetcher = Callable[[int], Awaitable[list[EmergingSignal]]]
_FEEDS: dict[str, Fetcher] = {}


def register_feed(name: str, fetcher: Fetcher) -> None:
    _FEEDS[name] = fetcher


def available_feeds() -> list[str]:
    return sorted(_FEEDS.keys())


async def fetch_signals(
    feed: str = "nvd-cve", limit: int = 10
) -> list[EmergingSignal]:
    fetcher = _FEEDS.get(feed)
    if fetcher is None:
        raise ValueError(f"unknown feed '{feed}'. available: {available_feeds()}")
    return await fetcher(limit)


# -- NVD CVE feed -----------------------------------------------------------

_NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


async def _fetch_nvd_cves(limit: int) -> list[EmergingSignal]:
    """Fetch recent CVEs from the NVD JSON API.

    We pull CVEs published in the last 7 days; NVD limits results per
    request, so we cap at `limit`. CVSS v3.1 base score → 1-5 impact_score.
    """
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=7)
    params = {
        "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "pubEndDate": end.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "resultsPerPage": str(max(1, min(limit, 50))),
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(_NVD_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    signals: list[EmergingSignal] = []
    for item in data.get("vulnerabilities", [])[:limit]:
        cve = item.get("cve", {})
        cve_id = cve.get("id", "CVE-UNKNOWN")
        descriptions = cve.get("descriptions") or []
        summary = next(
            (d.get("value") for d in descriptions if d.get("lang") == "en"),
            "",
        )
        published = cve.get("published")
        try:
            detected_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
        except Exception:
            detected_at = datetime.now(timezone.utc)

        cvss = _extract_cvss(cve.get("metrics") or {})
        impact = _cvss_to_1_5(cvss)
        signals.append(
            EmergingSignal(
                title=cve_id,
                source="nvd-cve",
                url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                summary=summary[:1000],
                detected_at=detected_at,
                impact_score=impact,
            )
        )
    return signals


def _extract_cvss(metrics: dict) -> float | None:
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        entries = metrics.get(key) or []
        if entries:
            data = entries[0].get("cvssData", {})
            score = data.get("baseScore")
            if isinstance(score, (int, float)):
                return float(score)
    return None


def _cvss_to_1_5(score: float | None) -> int:
    if score is None:
        return 3
    if score >= 9.0:
        return 5
    if score >= 7.0:
        return 4
    if score >= 4.0:
        return 3
    if score >= 0.1:
        return 2
    return 1


register_feed("nvd-cve", _fetch_nvd_cves)


# -- Synthetic feed for offline/test environments ---------------------------


async def _fetch_synthetic(limit: int) -> list[EmergingSignal]:
    now = datetime.now(timezone.utc)
    seeds = [
        ("(synthetic) EU AI Act compliance guidance updated", "eu-regulator", 3),
        ("(synthetic) Major cloud provider outage post-mortem", "ops-news", 4),
        ("(synthetic) Zero-day in popular SaaS auth library", "security-advisory", 5),
    ]
    return [
        EmergingSignal(
            title=t,
            source=src,
            url=None,
            summary=f"Placeholder signal {i+1} for development.",
            detected_at=now,
            impact_score=impact,
        )
        for i, (t, src, impact) in enumerate(seeds[:limit])
    ]


register_feed("synthetic", _fetch_synthetic)


def synthetic_signal() -> EmergingSignal:
    """Kept for backwards-compatibility with the seed endpoint."""
    return EmergingSignal(
        title="(synthetic) New EU AI Act guidance published",
        source="placeholder",
        url=None,
        summary="Wire in real feeds; this is a developer placeholder.",
        detected_at=datetime.now(timezone.utc),
        impact_score=3,
    )
