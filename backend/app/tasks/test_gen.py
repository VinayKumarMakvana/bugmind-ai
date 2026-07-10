from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from openai import OpenAI

from ..core.config import settings
from ..db.session import db
from ..services.rag import retrieve_context

logger = logging.getLogger(__name__)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

async def get_user_api_key(repo_id: str) -> Optional[str]:
    """
    Retrieve the user's OpenAI API key from the database based on the repo_id.
    """
    repo_dict = await db.repositories.find_one({"id": repo_id})
    if repo_dict and repo_dict.get("user_id"):
        user_dict = await db.users.find_one({"id": repo_dict["user_id"]})
        if user_dict and user_dict.get("openai_api_key"):
            return user_dict["openai_api_key"]
            
    return settings.OPENAI_API_KEY


# =========================================================
# BACKGROUND TASKS
# =========================================================

def generate_tests(repo_id: str, pr_number: str) -> Dict[str, Any]:
    """
    Generate PyTest unit tests for a specific PR using the AI Copilot.
    Runs asynchronously in the background.
    """
    logger.info("Generating tests for Repo %s, PR %s", repo_id, pr_number)
    
    # Mocking a diff for local testing, since we don't have real PR webhooks in local mode.
    diff = "def get_user(user_id): pass" 
    
    context = retrieve_context(repo_id, diff)
    context_text = "\n".join(context) if context else ""
    
    api_key = asyncio.run(get_user_api_key(repo_id))
        
    client = OpenAI(api_key=api_key) if api_key else None
    
    if not client:
        logger.info("OpenAI API key missing. Mocking test generation.")
        time.sleep(2)
        logger.info("Completed mock test generation.")
        return {
            "status": "success",
            "repo_id": repo_id,
            "pr_number": pr_number,
            "tests": "def test_mock(): pass",
        }
        
    prompt = f"Given the following PR diff and context, generate PyTest unit tests.\n\nDiff:\n{diff}\n\nContext:\n{context_text}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert QA engineer."},
                {"role": "user", "content": prompt}
            ]
        )
        
        tests = response.choices[0].message.content
        logger.info("Completed test generation for PR %s", pr_number)
        
        return {
            "status": "success",
            "repo_id": repo_id,
            "pr_number": pr_number,
            "tests": tests,
        }
        
    except Exception as e:
        logger.error("Test generation failed: %s", e)
        return {
            "status": "error",
            "message": str(e),
        }
