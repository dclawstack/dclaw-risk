"""P1.4 Compliance integration.

When DClaw Compliance is reachable (`COMPLIANCE_BASE_URL` is set and
`COMPLIANCE_MOCK_MODE` is false), we proxy calls there. Otherwise we serve a
deterministic fixture so the rest of the platform can render the unified-view
end-to-end. The fixture clearly tags itself with `"mock": true`.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import settings

# A small but realistic compliance fixture covering common frameworks. Each
# requirement carries the canonical control families it expects. The
# unified-view endpoint joins this against the dclaw-risk controls library so
# you can spot which requirements are uncovered.

_FIXTURE = {
    "frameworks": [
        {
            "id": "iso-27001",
            "name": "ISO/IEC 27001:2022",
            "category": "Information Security",
            "requirements": [
                {
                    "id": "iso27001.A.5.1",
                    "title": "Policies for information security",
                    "expects_control_types": ["preventive"],
                    "tags": ["policy"],
                },
                {
                    "id": "iso27001.A.8.1",
                    "title": "User endpoint devices",
                    "expects_control_types": ["preventive", "detective"],
                    "tags": ["endpoint"],
                },
                {
                    "id": "iso27001.A.8.2",
                    "title": "Privileged access rights",
                    "expects_control_types": ["preventive"],
                    "tags": ["access"],
                },
            ],
        },
        {
            "id": "soc2",
            "name": "SOC 2 Type II",
            "category": "Trust Services Criteria",
            "requirements": [
                {
                    "id": "soc2.CC6.1",
                    "title": "Logical access controls",
                    "expects_control_types": ["preventive", "detective"],
                    "tags": ["access"],
                },
                {
                    "id": "soc2.CC7.2",
                    "title": "System monitoring",
                    "expects_control_types": ["detective"],
                    "tags": ["monitoring"],
                },
                {
                    "id": "soc2.CC8.1",
                    "title": "Change management",
                    "expects_control_types": ["preventive"],
                    "tags": ["change"],
                },
            ],
        },
        {
            "id": "nist-800-53",
            "name": "NIST SP 800-53 Rev 5",
            "category": "Federal Information Security",
            "requirements": [
                {
                    "id": "nist800-53.AC-2",
                    "title": "Account management",
                    "expects_control_types": ["preventive"],
                    "tags": ["access"],
                },
                {
                    "id": "nist800-53.AU-6",
                    "title": "Audit record review",
                    "expects_control_types": ["detective"],
                    "tags": ["monitoring", "audit"],
                },
                {
                    "id": "nist800-53.IR-4",
                    "title": "Incident handling",
                    "expects_control_types": ["corrective"],
                    "tags": ["incident"],
                },
            ],
        },
    ]
}


@dataclass
class ComplianceResult:
    data: dict
    mock: bool
    source: str


async def fetch_compliance_library() -> ComplianceResult:
    """Return frameworks + requirements either from a real Compliance app
    or a deterministic mock fixture.
    """
    if settings.compliance_base_url and not settings.compliance_mock_mode:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{settings.compliance_base_url.rstrip('/')}/api/v1/library"
            )
            resp.raise_for_status()
            return ComplianceResult(
                data=resp.json(),
                mock=False,
                source=settings.compliance_base_url,
            )
    return ComplianceResult(data=_FIXTURE, mock=True, source="fixture")


async def push_local_controls(controls: list[dict]) -> ComplianceResult:
    """Push our local control library to DClaw Compliance.

    In mock mode this is a no-op that echoes the payload back.
    """
    if settings.compliance_base_url and not settings.compliance_mock_mode:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{settings.compliance_base_url.rstrip('/')}/api/v1/controls/import",
                json={"controls": controls},
            )
            resp.raise_for_status()
            return ComplianceResult(
                data=resp.json(), mock=False, source=settings.compliance_base_url
            )
    return ComplianceResult(
        data={"received": len(controls), "mock_acknowledged": True},
        mock=True,
        source="fixture",
    )


def join_with_local(
    library: dict, local_controls: list[dict]
) -> list[dict]:
    """Annotate each compliance requirement with our local controls that fit."""
    grouped_by_type: dict[str, list[dict]] = {}
    for c in local_controls:
        grouped_by_type.setdefault(c.get("control_type", "preventive"), []).append(c)

    rows: list[dict] = []
    for framework in library.get("frameworks", []):
        for req in framework.get("requirements", []):
            matches: list[dict] = []
            for ctype in req.get("expects_control_types", []):
                matches.extend(grouped_by_type.get(ctype, []))
            seen: set[str] = set()
            deduped: list[dict] = []
            for m in matches:
                if m["id"] not in seen:
                    seen.add(m["id"])
                    deduped.append(m)
            rows.append(
                {
                    "framework_id": framework["id"],
                    "framework": framework["name"],
                    "requirement_id": req["id"],
                    "requirement": req["title"],
                    "expects": req.get("expects_control_types", []),
                    "matching_controls": [
                        {
                            "id": m["id"],
                            "name": m["name"],
                            "type": m.get("control_type"),
                            "effectiveness": m.get("effectiveness"),
                        }
                        for m in deduped
                    ],
                    "covered": bool(deduped),
                }
            )
    return rows
