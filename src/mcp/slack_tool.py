import logging
import os
from datetime import datetime, timedelta, timezone

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


async def fetch_messages(channel: str, hours_back: int = 4) -> list[dict]:
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        logger.warning("SLACK_BOT_TOKEN not set — skipping Slack fetch")
        return []

    oldest = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).timestamp()
    client = WebClient(token=token)

    try:
        response = client.conversations_history(channel=channel, oldest=str(oldest))
        return [
            {"ts": m["ts"], "user": m.get("user", "unknown"), "text": m.get("text", "")}
            for m in response.get("messages", [])
            if m.get("type") == "message" and not m.get("bot_id")
        ]
    except SlackApiError as e:
        logger.warning("Slack API error: %s", e.response["error"])
        return []
