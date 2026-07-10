from __future__ import annotations

import json
import logging
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

TIMEOUT = 300

SEVERITY_MAP = {
    "ERROR": "HIGH",
    "WARNING": "MEDIUM",
    "INFO": "LOW",
    "LOW": "LOW",
    "MEDIUM": "MEDIUM",
    "HIGH": "HIGH",
    "CRITICAL": "CRITICAL",
}


def normalize_severity(value: str | None) -> str:
    if not value:
        return "LOW"

    return SEVERITY_MAP.get(
        str(value).upper(),
        "LOW",
    )


def run_command(command: List[str]) -> Any:
    """
    Execute subprocess safely.
    """

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )

        if not result.stdout.strip():
            return {}

        return json.loads(result.stdout)

    except subprocess.TimeoutExpired:

        logger.exception("Command timeout.")

    except json.JSONDecodeError:

        logger.exception("Invalid JSON output.")

    except Exception:

        logger.exception("Command execution failed.")

    return {}

# =========================================================
# TOOL RUNNERS
# =========================================================

def run_semgrep(repo_path: str) -> Dict[str, Any]:
    """
    Execute Semgrep.
    """

    logger.info("Running Semgrep...")

    return run_command([
        sys.executable,
        "-m",
        "semgrep",
        "--json",
        "--config=p/ci",
        repo_path,
    ])


def run_bandit(repo_path: str) -> Dict[str, Any]:
    """
    Execute Bandit.
    """

    logger.info("Running Bandit...")

    return run_command([
        sys.executable,
        "-m",
        "bandit",
        "-r",
        repo_path,
        "-f",
        "json",
    ])


def run_pylint(repo_path: str) -> List[Dict[str, Any]]:
    """
    Execute Pylint.
    """

    logger.info("Running Pylint...")

    result = run_command([
        sys.executable,
        "-m",
        "pylint",
        repo_path,
        "-f",
        "json",
    ])

    if isinstance(result, list):
        return result

    return []


# =========================================================
# PARALLEL EXECUTION
# =========================================================

def run_static_tools(repo_path: str) -> Dict[str, Any]:
    """
    Run all static analyzers in parallel.
    """

    repo = Path(repo_path)

    if not repo.exists():
        raise FileNotFoundError(f"{repo_path} does not exist.")

    with ThreadPoolExecutor(max_workers=3) as executor:

        semgrep_future = executor.submit(
            run_semgrep,
            repo_path,
        )

        bandit_future = executor.submit(
            run_bandit,
            repo_path,
        )

        pylint_future = executor.submit(
            run_pylint,
            repo_path,
        )

        return {
            "semgrep": semgrep_future.result(),
            "bandit": bandit_future.result(),
            "pylint": pylint_future.result(),
        }

# =========================================================
# PARSE SEMGREP
# =========================================================

def parse_semgrep(results: Dict[str, Any]) -> List[Dict[str, Any]]:

    findings = []

    for item in results.get("results", []):

        findings.append({
            "tool": "semgrep",
            "rule_id": item.get("check_id", ""),
            "category": "Static Analysis",
            "file": item.get("path", ""),
            "line": item.get("start", {}).get("line", 0),
            "severity": normalize_severity(
                item.get("extra", {}).get("severity")
            ),
            "message": item.get("extra", {}).get("message", ""),
            "confidence": item.get("extra", {}).get("confidence", "MEDIUM"),
            "code": item.get("extra", {}).get("lines", ""),
        })

    return findings


# =========================================================
# PARSE BANDIT
# =========================================================

def parse_bandit(results: Dict[str, Any]) -> List[Dict[str, Any]]:

    findings = []

    for item in results.get("results", []):

        findings.append({
            "tool": "bandit",
            "rule_id": item.get("test_id", ""),
            "category": "Security",
            "file": item.get("filename", ""),
            "line": item.get("line_number", 0),
            "severity": normalize_severity(
                item.get("issue_severity")
            ),
            "message": item.get("issue_text", ""),
            "confidence": item.get("issue_confidence", "MEDIUM"),
            "code": item.get("code", ""),
        })

    return findings


# =========================================================
# PARSE PYLINT
# =========================================================

def parse_pylint(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    findings = []

    severity_map = {
        "fatal": "CRITICAL",
        "error": "HIGH",
        "warning": "MEDIUM",
        "convention": "LOW",
        "refactor": "LOW",
        "info": "INFO",
    }

    for item in results:

        findings.append({
            "tool": "pylint",
            "rule_id": item.get("message-id", ""),
            "category": item.get("symbol", "Code Quality"),
            "file": item.get("path", ""),
            "line": item.get("line", 0),
            "severity": severity_map.get(
                item.get("type", "").lower(),
                "LOW",
            ),
            "message": item.get("message", ""),
            "confidence": "HIGH",
            "code": "",
        })

    return findings


# =========================================================
# REMOVE DUPLICATE FINDINGS
# =========================================================

def remove_duplicate_findings(
    findings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    unique = {}

    for finding in findings:

        key = (
            finding.get("tool"),
            finding.get("file"),
            finding.get("line"),
            finding.get("message"),
        )

        unique[key] = finding

    return list(unique.values())

# =========================================================
# AGGREGATE FINDINGS
# =========================================================

def aggregate_findings(repo_path: str) -> List[Dict[str, Any]]:
    """
    Run all static analysis tools and return normalized findings.
    """

    logger.info("=" * 60)
    logger.info("Running Static Analysis")
    logger.info("=" * 60)

    results = run_static_tools(repo_path)

    findings: List[Dict[str, Any]] = []

    findings.extend(
        parse_semgrep(
            results.get("semgrep", {})
        )
    )

    findings.extend(
        parse_bandit(
            results.get("bandit", {})
        )
    )

    findings.extend(
        parse_pylint(
            results.get("pylint", [])
        )
    )

    findings = remove_duplicate_findings(findings)

    findings.sort(
        key=lambda x: (
            {
                "CRITICAL": 5,
                "HIGH": 4,
                "MEDIUM": 3,
                "LOW": 2,
                "INFO": 1,
            }.get(
                x.get("severity", "LOW"),
                1,
            )
        ),
        reverse=True,
    )

    logger.info(
        "Static Analysis Completed. %s issues found.",
        len(findings),
    )

    return findings


# =========================================================
# TOOL SUMMARY
# =========================================================

def get_tool_summary(
    findings: List[Dict[str, Any]]
) -> Dict[str, Any]:

    summary = {
        "total": len(findings),
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
        "tools": {},
    }

    for finding in findings:

        severity = finding.get(
            "severity",
            "LOW",
        ).lower()

        if severity in summary:
            summary[severity] += 1

        tool = finding.get(
            "tool",
            "unknown",
        )

        summary["tools"][tool] = (
            summary["tools"].get(tool, 0) + 1
        )

    return summary


# =========================================================
# FILTER FINDINGS
# =========================================================

def filter_findings(
    findings: List[Dict[str, Any]],
    minimum_severity: str = "LOW",
) -> List[Dict[str, Any]]:

    order = {
        "INFO": 1,
        "LOW": 2,
        "MEDIUM": 3,
        "HIGH": 4,
        "CRITICAL": 5,
    }

    level = order.get(
        minimum_severity.upper(),
        2,
    )

    return [

        item

        for item in findings

        if order.get(
            item.get("severity", "LOW"),
            1,
        ) >= level

    ]


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "aggregate_findings",

    "filter_findings",

    "get_tool_summary",

]