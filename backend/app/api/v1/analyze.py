from __future__ import annotations

import logging
import os
import tempfile
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...api.deps import get_current_user
from ...models.domain import User
from ...services.ai_reviewer import generate_review
from ...services.static_analysis import aggregate_findings

logger = logging.getLogger(__name__)

# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# MODELS
# =========================================================

class AnalyzeRequest(BaseModel):
    code_content: str
    file_name: str


# =========================================================
# ROUTES
# =========================================================

@router.post("")
@router.post("/")
async def analyze_snippet(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Analyze a standalone code snippet and generate an AI review.
    """

    logger.info("=" * 60)
    logger.info("Snippet Analysis Request: %s", request.file_name)
    logger.info("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:

        file_path = os.path.join(temp_dir, request.file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(request.code_content)

        # 1. Run Static Analysis
        findings = aggregate_findings(temp_dir)

        # 2. Map findings format to AI Reviewer format
        formatted_findings = []
        for index, f in enumerate(findings):
            formatted_findings.append({
                "id": str(index),
                "file": request.file_name,
                "line": f.get("line", 0),
                "description": f.get("message", ""),
                "severity": f.get("severity", "LOW"),
            })

        # 3. Generate AI Review
        review = generate_review(
            pr_diff=request.code_content,
            findings=formatted_findings,
            context_chunks=[],
            user_openai_api_key=current_user.openai_api_key,
        )

        # 4. Map the new AI review schema back to the frontend's expected format
        bugs = []
        for issue in review.get("findings", []):
            title = issue.get("title", "Issue")
            
            bugs.append({
                "severity": issue.get("severity", "MEDIUM").lower(),
                "title": title,
                "description": (
                    f"**Why:** {issue.get('why', '')}\n\n"
                    f"**Fix:** {issue.get('fix', '')}\n\n"
                    f"**Example:**\n```\n{issue.get('example', '')}\n```"
                )
            })
            
        summary = review.get("summary", {})
        summary_text = (
            f"Analysis completed. Found {summary.get('total_issues', 0)} issues "
            f"({summary.get('critical', 0)} critical, {summary.get('high', 0)} high)."
        )

        return {
            "summary": summary_text,
            "bugs": bugs
        }
