import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")

async def main():
    pass  # Phase 6: wire everything together

if __name__ == "__main__":
    asyncio.run(main())
