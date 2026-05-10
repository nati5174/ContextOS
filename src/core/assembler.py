import logging
from datetime import datetime, timezone

from src.core.schemas import IncidentContext, IncidentEvent

logger = logging.getLogger(__name__)


def compute_confidence(sources_with_data: list[str]) -> tuple[str, str]:
    count = len(sources_with_data)
    if count >= 3:
        return "HIGH", "Data retrieved from all 3 sources: " + ", ".join(sources_with_data)
    elif count == 2:
        return "MED", "Data retrieved from 2 sources: " + ", ".join(sources_with_data)
    else:
        return "LOW", "Data retrieved from 1 source only: " + ", ".join(sources_with_data)


def _normalize_slack(messages: list[dict]) -> list[IncidentEvent]:
    events = []
    for m in messages:
        try:
            events.append(IncidentEvent(
                timestamp=datetime.fromtimestamp(float(m["ts"]), tz=timezone.utc),
                source="slack",
                actor=m.get("user", "unknown"),
                event=m.get("text", ""),
                link="",
            ))
        except Exception as e:
            logger.warning("Skipping slack message: %s", e)
    return events


def _normalize_github(prs: list[dict], commits: list[dict]) -> list[IncidentEvent]:
    events = []
    for pr in prs:
        try:
            events.append(IncidentEvent(
                timestamp=datetime.fromisoformat(pr["merged_at"]),
                source="github",
                actor=pr["author"],
                event=f"PR merged: {pr['title']}",
                link=pr["url"],
            ))
        except Exception as e:
            logger.warning("Skipping PR: %s", e)
    for c in commits:
        try:
            events.append(IncidentEvent(
                timestamp=datetime.fromisoformat(c["date"]),
                source="github",
                actor=c["author"],
                event=f"Commit {c['sha']}: {c['message']}",
                link=c["url"],
            ))
        except Exception as e:
            logger.warning("Skipping commit: %s", e)
    return events


def _normalize_jira(tickets: list[dict]) -> list[IncidentEvent]:
    events = []
    for t in tickets:
        try:
            events.append(IncidentEvent(
                timestamp=datetime.fromisoformat(t["created"]),
                source="jira",
                actor="jira",
                event=f"[{t['key']}] {t['summary']} ({t['status']})",
                link=t["url"],
            ))
        except Exception as e:
            logger.warning("Skipping Jira ticket: %s", e)
    return events


def _dedup(events: list[IncidentEvent]) -> list[IncidentEvent]:
    seen = set()
    out = []
    for e in events:
        key = (e.source, e.actor, e.event)
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


def assemble(
    query: str,
    slack_raw: list[dict],
    github_prs: list[dict],
    github_commits: list[dict],
    jira_raw: list[dict],
) -> IncidentContext:
    sources_with_data = []
    if slack_raw:
        sources_with_data.append("slack")
    if github_prs or github_commits:
        sources_with_data.append("github")
    if jira_raw:
        sources_with_data.append("jira")

    events = (
        _normalize_slack(slack_raw)
        + _normalize_github(github_prs, github_commits)
        + _normalize_jira(jira_raw)
    )

    events = _dedup(events)
    events.sort(key=lambda e: e.timestamp)

    return IncidentContext(
        query=query,
        events=events,
        raw_slack=slack_raw,
        raw_github=github_prs + github_commits,
        raw_jira=jira_raw,
    )
