import time
import asyncio
from openai import OpenAI
from ..core.config import settings
from ..services.rag import retrieve_context
from ..models.domain import Repository, User
from ..db.session import db

async def get_user_api_key(repo_id: str):
    repo_dict = await db.repositories.find_one({"id": repo_id})
    if repo_dict and repo_dict.get("user_id"):
        user_dict = await db.users.find_one({"id": repo_dict["user_id"]})
        if user_dict and user_dict.get("openai_api_key"):
            return user_dict["openai_api_key"]
    return settings.OPENAI_API_KEY

def generate_tests(repo_id: str, pr_number: str):
    print(f"Generating tests for Repo {repo_id}, PR {pr_number}")
    
    diff = "def get_user(user_id): pass" 
    context = retrieve_context(repo_id, diff)
    context_text = "\n".join(context) if context else ""
    
    api_key = asyncio.run(get_user_api_key(repo_id))
        
    client = OpenAI(api_key=api_key) if api_key else None
    
    if not client:
        print("Mocking test generation")
        time.sleep(2)
        print("Completed mock test generation")
        return {"status": "success", "repo_id": repo_id, "pr_number": pr_number, "tests": "def test_mock(): pass"}
        
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
        print(f"Completed test generation for PR {pr_number}")
        return {"status": "success", "repo_id": repo_id, "pr_number": pr_number, "tests": tests}
    except Exception as e:
        print(f"Test generation failed: {e}")
        return {"status": "error"}
