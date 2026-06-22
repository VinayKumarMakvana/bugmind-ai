import subprocess
import json
import os
import sys

def run_semgrep(repo_path: str):
    """Run semgrep on the repository and return JSON results."""
    try:
        # We use --config=p/ci to use default CI rules
        result = subprocess.run(
            [sys.executable, "-m", "semgrep", "--json", "--config=p/ci", repo_path],
            capture_output=True,
            text=True
        )
        if result.stdout:
            return json.loads(result.stdout)
        return {"results": []}
    except Exception as e:
        print(f"Semgrep failed: {e}")
        return {"results": []}

def run_bandit(repo_path: str):
    """Run bandit on the repository and return JSON results."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", repo_path, "-f", "json"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            return json.loads(result.stdout)
        return {"results": []}
    except Exception as e:
        print(f"Bandit failed: {e}")
        return {"results": []}

def run_pylint(repo_path: str):
    """Run pylint and return JSON results."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pylint", repo_path, "-f", "json"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            # Pylint outputs a list directly
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Pylint failed: {e}")
        return []

def aggregate_findings(repo_path: str):
    """Run static analysis tools and aggregate findings."""
    print(f"Running static analysis on {repo_path}")
    
    semgrep_results = run_semgrep(repo_path)
    bandit_results = run_bandit(repo_path)
    pylint_results = run_pylint(repo_path)
    
    findings = []
    
    # Parse Semgrep
    for res in semgrep_results.get("results", []):
        findings.append({
            "tool": "semgrep",
            "file_path": res.get("path"),
            "line_number": res.get("start", {}).get("line"),
            "severity": res.get("extra", {}).get("severity"),
            "description": res.get("extra", {}).get("message"),
        })
        
    # Parse Bandit
    for res in bandit_results.get("results", []):
        findings.append({
            "tool": "bandit",
            "file_path": res.get("filename"),
            "line_number": res.get("line_number"),
            "severity": res.get("issue_severity"),
            "description": res.get("issue_text"),
        })
        
    # Parse Pylint
    for res in pylint_results:
        # Pylint type mapping
        msg_type = res.get("type", "warning")
        sev = "LOW"
        if msg_type in ["error", "fatal"]:
            sev = "HIGH"
        elif msg_type == "warning":
            sev = "MEDIUM"
            
        findings.append({
            "tool": "pylint",
            "file_path": res.get("path"),
            "line_number": res.get("line"),
            "severity": sev,
            "description": f"[{res.get('message-id')}] {res.get('message')}",
        })
        
    return findings
