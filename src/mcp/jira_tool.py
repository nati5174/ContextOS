import logging
import os

from atlassian import Jira

logger = logging.getLogger(__name__)


async def fetch_tickets(query: str, hours_back: int = 4) -> list[dict]:
    url = os.getenv("JIRA_URL")
    user = os.getenv("JIRA_USER")
    token = os.getenv("JIRA_API_TOKEN")

    if not all([url, user, token]):
        logger.warning("Jira credentials not set — skipping Jira fetch")
        return []

    jql = f'text ~ "{query}" AND created >= -{hours_back}h ORDER BY created DESC'

    try:
        jira = Jira(url=url, username=user, password=token, cloud=True)
        issues = jira.jql(jql).get("issues", [])
        return [
            {
                "key": i["key"],
                "summary": i["fields"]["summary"],
                "status": i["fields"]["status"]["name"],
                "created": i["fields"]["created"],
                "url": f"{url}/browse/{i['key']}",
            }
            for i in issues
        ]
    except Exception as e:
        logger.warning("Jira error: %s", e)
        return []
