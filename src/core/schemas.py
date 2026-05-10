from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class IncidentEvent(BaseModel):
    timestamp: datetime
    source: Literal["slack", "github", "jira"]
    actor: str
    event: str
    link: str = ""


class IncidentContext(BaseModel):
    query: str
    events: list[IncidentEvent]
    raw_slack: list[dict]
    raw_github: list[dict]
    raw_jira: list[dict]


class RootCause(BaseModel):
    summary: str
    confidence: Literal["HIGH", "MED", "LOW"]
    confidence_reason: str


class TimelineEntry(BaseModel):
    timestamp: str
    source: str
    actor: str
    event: str
    link: str = ""


class Evidence(BaseModel):
    slack_threads: list[str]
    github_prs: list[str]
    jira_tickets: list[str]


class ActionItem(BaseModel):
    owner: str
    action: str
    priority: Literal["P1", "P2", "P3"]


class PostmortemDraft(BaseModel):
    title: str
    summary: str
    contributing_factors: list[str]
    action_items: list[ActionItem]


class InvestigateOutput(BaseModel):
    root_cause: RootCause
    timeline: list[TimelineEntry]
    evidence: Evidence
    postmortem_draft: PostmortemDraft
