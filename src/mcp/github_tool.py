import logging
import os
from datetime import datetime, timedelta, timezone

from github import Github, GithubException

logger = logging.getLogger(__name__)


def _client():
    return Github(os.getenv("GITHUB_TOKEN"))


async def fetch_prs(repo: str, hours_back: int = 4) -> list[dict]:
    if not os.getenv("GITHUB_TOKEN"):
        logger.warning("GITHUB_TOKEN not set — skipping GitHub PR fetch")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    try:
        r = _client().get_repo(repo)
        prs = []
        for pr in r.get_pulls(state="closed", sort="updated", direction="desc"):
            if pr.merged_at and pr.merged_at >= cutoff:
                prs.append({
                    "title": pr.title,
                    "url": pr.html_url,
                    "author": pr.user.login,
                    "merged_at": pr.merged_at.isoformat(),
                })
            elif pr.updated_at < cutoff:
                break
        return prs
    except GithubException as e:
        logger.warning("GitHub API error: %s", e)
        return []


async def fetch_commits(repo: str, hours_back: int = 4) -> list[dict]:
    if not os.getenv("GITHUB_TOKEN"):
        logger.warning("GITHUB_TOKEN not set — skipping GitHub commit fetch")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    try:
        r = _client().get_repo(repo)
        return [
            {
                "sha": c.sha[:7],
                "message": c.commit.message.splitlines()[0],
                "author": c.commit.author.name,
                "date": c.commit.author.date.isoformat(),
                "url": c.html_url,
            }
            for c in r.get_commits(since=cutoff)
        ]
    except GithubException as e:
        logger.warning("GitHub API error: %s", e)
        return []
