import json
import logging
import os
from typing import Protocol

import cohere

from src.core.schemas import IncidentContext, InvestigateOutput

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert incident response AI. You will be given details about an ongoing or recent incident
including Slack messages, GitHub PRs/commits, and Jira tickets.

Your job is to analyze all the evidence and return a JSON object that EXACTLY matches this schema:
{
  "root_cause": {
    "summary": "string",
    "confidence": "HIGH" | "MED" | "LOW",
    "confidence_reason": "string"
  },
  "timeline": [
    {
      "timestamp": "ISO8601 string",
      "source": "slack" | "github" | "jira",
      "actor": "string",
      "event": "string",
      "link": "string"
    }
  ],
  "evidence": {
    "slack_threads": ["string"],
    "github_prs": ["string"],
    "jira_tickets": ["string"]
  },
  "postmortem_draft": {
    "title": "string",
    "summary": "string",
    "contributing_factors": ["string"],
    "action_items": [
      {
        "owner": "string",
        "action": "string",
        "priority": "P1" | "P2" | "P3"
      }
    ]
  }
}

Return ONLY valid JSON. No markdown. No explanation. No code fences.
"""


class AIProvider(Protocol):
    def generate(self, prompt: str, context: IncidentContext) -> InvestigateOutput:
        ...


class CohereProvider:
    def __init__(self, api_key: str):
        self.client = cohere.Client(api_key)

    def generate(self, prompt: str, context: IncidentContext) -> InvestigateOutput:
        context_text = self._build_context_text(context)
        user_message = f"Incident query: {prompt}\n\n{context_text}"

        response = self.client.chat(
            model="command-r-plus",
            preamble=SYSTEM_PROMPT,
            message=user_message,
        )

        raw = response.text.strip()

        try:
            data = json.loads(raw)
            return InvestigateOutput(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Failed to parse Cohere response: %s", e)
            logger.debug("Raw response: %s", raw)
            raise

    def _build_context_text(self, context: IncidentContext) -> str:
        lines = [f"Total events: {len(context.events)}\n"]

        if context.raw_slack:
            lines.append("=== SLACK MESSAGES ===")
            for m in context.raw_slack:
                lines.append(f"[{m.get('ts')}] {m.get('user')}: {m.get('text')}")

        if context.raw_github:
            lines.append("\n=== GITHUB ACTIVITY ===")
            for g in context.raw_github:
                if "title" in g:
                    lines.append(f"PR: {g['title']} by {g.get('author')} at {g.get('merged_at')} — {g.get('url')}")
                else:
                    lines.append(f"Commit {g.get('sha')}: {g.get('message')} by {g.get('author')} at {g.get('date')} — {g.get('url')}")

        if context.raw_jira:
            lines.append("\n=== JIRA TICKETS ===")
            for t in context.raw_jira:
                lines.append(f"[{t['key']}] {t['summary']} ({t['status']}) — {t.get('url')}")

        return "\n".join(lines)

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("embed() is reserved for v2")

    def rerank(self, query: str, documents: list[str]) -> list[dict]:
        raise NotImplementedError("rerank() is reserved for v2")
