import asyncio
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from src.mcp import slack_tool, github_tool, jira_tool
from src.core import assembler
from src.ai.provider import CohereProvider

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "incidents")


async def main():
    incident = "payments-service-outage"

    print(f"Running ContextOS spike for: {incident}\n")

    # Parallel MCP calls
    slack_raw, github_prs, github_commits, jira_raw = await asyncio.gather(
        slack_tool.fetch_messages(channel=SLACK_CHANNEL),
        github_tool.fetch_prs(repo=GITHUB_REPO),
        github_tool.fetch_commits(repo=GITHUB_REPO),
        jira_tool.fetch_tickets(query=incident),
    )

    print(f"Slack messages:   {len(slack_raw)}")
    print(f"GitHub PRs:       {len(github_prs)}")
    print(f"GitHub commits:   {len(github_commits)}")
    print(f"Jira tickets:     {len(jira_raw)}\n")

    # Assemble context
    context = assembler.assemble(incident, slack_raw, github_prs, github_commits, jira_raw)

    # Compute + print confidence
    sources = []
    if slack_raw:
        sources.append("slack")
    if github_prs or github_commits:
        sources.append("github")
    if jira_raw:
        sources.append("jira")
    confidence, reason = assembler.compute_confidence(sources)
    print(f"Confidence: {confidence} — {reason}\n")

    # Generate output
    if not COHERE_API_KEY:
        print("ERROR: COHERE_API_KEY not set")
        return

    provider = CohereProvider(api_key=COHERE_API_KEY)
    output = provider.generate(incident, context)

    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
