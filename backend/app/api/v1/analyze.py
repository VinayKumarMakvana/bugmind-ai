import os
import tempfile
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ...api.deps import get_current_user
from ...models.domain import User
from ...services.static_analysis import aggregate_findings
from ...services.ai_reviewer import generate_review

router = APIRouter()

class AnalyzeRequest(BaseModel):
    code_content: str
    file_name: str

@router.post("")
@router.post("/")
async def analyze_snippet(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, request.file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(request.code_content)
        
        findings = aggregate_findings(temp_dir)
        
        formatted_findings = []
        for f in findings:
            formatted_findings.append({
                "id": str(len(formatted_findings)),
                "file": request.file_name,
                "line": f.get("line_number", 0),
                "description": f.get("description", ""),
                "severity": str(f.get("severity", "LOW")),
            })
            
        reviewed_findings = generate_review(request.code_content, formatted_findings, [], current_user.openai_api_key)
        
        bugs = []
        for rf in reviewed_findings:
            title = rf.get("description", "Issue")
            if "\n" in title:
                title = title.split("\n")[0]
            if len(title) > 60:
                title = title[:57] + "..."
                
            severity_mapped = rf.get("severity", "LOW").lower()
            if severity_mapped not in ["low", "medium", "high", "critical"]:
                severity_mapped = "medium"
                
            bugs.append({
                "severity": severity_mapped,
                "title": title,
                "description": rf.get("suggested_fix", f"**AI Review Failed**\n\nThe AI reviewer could not generate a fix for this issue (Check OpenAI API Key on your server).\n\n**Raw Error:**\n`{rf.get('description', '')}`")
            })
            
        summary = "Analysis completed. No issues found." if not bugs else f"Analysis completed. Found {len(bugs)} issues."
        
        return {
            "summary": summary,
            "bugs": bugs
        }
