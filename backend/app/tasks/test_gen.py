from .celery_app import celery_app
import time
from openai import OpenAI
from ..core.config import settings
from ..services.rag import retrieve_context
from ..models.domain import Repository, User
from ..db.session import SessionLocal

@celery_app.task(name="generate_tests")
def generate_tests(repo_id: str, pr_number: str):
    print(f"Generating tests for Repo {repo_id}, PR {pr_number}")
    
    # Simulate fetching diff and determining language
    diff = "def get_user(user_id): pass" 
    context = retrieve_context(repo_id, diff)
    context_text = "\n".join(context) if context else ""
    
    # Get user token
    db = SessionLocal()
    api_key = settings.OPENAI_API_KEY
    try:
        repo_record = db.query(Repository).filter(Repository.github_repo_id == repo_id).first()
        if repo_record and repo_record.user_id:
            user_record = db.query(User).filter(User.id == repo_record.user_id).first()
            if user_record and user_record.openai_api_key:
                api_key = user_record.openai_api_key
    finally:
        db.close()
        
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
