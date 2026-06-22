import os
import json
from openai import OpenAI
from ..core.config import settings

def generate_review(pr_diff: str, findings: list, context_chunks: list, user_openai_api_key: str = None):
    """Use an LLM to generate a review based on the diff, static findings, and RAG context."""
    
    # Use user's personal key if available, otherwise fallback to system key
    api_key = user_openai_api_key or settings.OPENAI_API_KEY
    client = OpenAI(api_key=api_key) if api_key else None
    
    if not client:
        print("OPENAI_API_KEY not set. Mocking AI Review.")
        enriched_findings = []
        for f in findings:
            f_copy = dict(f)
            f_copy["suggested_fix"] = f"**[Mock AI Review]** Detected `{f['description']}`. In the context of your codebase, this should be addressed immediately."
            enriched_findings.append(f_copy)
        return enriched_findings

    system_prompt = (
        "You are BugMind AI, an elite Senior Staff Software Engineer and Security Specialist. "
        "Your code reviews are legendary for their insight, precision, and actionable advice. "
        "You always consider the broader codebase context."
    )
    
    prompt = f"""
    Please review the following Pull Request data.
    
    # Static Analysis Findings
    {json.dumps(findings, indent=2)}
    
    # Relevant Code Context (RAG)
    {chr(10).join(context_chunks)}
    
    # PR Diff
    {pr_diff}
    
    Task: For each finding in the Static Analysis Findings list, provide a highly detailed `suggested_fix`.
    The `suggested_fix` MUST use GitHub flavored markdown, include code snippets if applicable, and explain *why* the fix works based on the RAG context.
    
    You must return a JSON object with a single key "findings" which contains the updated list of finding objects.
    Example output format:
    {{
      "findings": [
        {{
          "id": "...",
          "file": "...",
          "line": 10,
          "description": "...",
          "severity": "...",
          "suggested_fix": "Markdown formatted explanation and fix..."
        }}
      ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0.2
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "findings" in parsed:
            return parsed["findings"]
        return findings
    except Exception as e:
        print(f"LLM Generation failed: {e}")
        return findings
