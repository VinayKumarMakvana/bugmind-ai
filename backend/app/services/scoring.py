from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# =========================================================
# SCORE CONFIGURATION
# =========================================================

QUALITY_DEDUCTION = {
    "CRITICAL": 20,
    "HIGH": 12,
    "MEDIUM": 6,
    "LOW": 2,
    "INFO": 1,
}

SECURITY_DEDUCTION = {
    "CRITICAL": 25,
    "HIGH": 15,
    "MEDIUM": 8,
    "LOW": 3,
    "INFO": 1,
}


# =========================================================
# NORMALIZE SEVERITY
# =========================================================

def normalize_severity(severity: str | None) -> str:

    if not severity:
        return "LOW"

    severity = severity.upper()

    if severity == "ERROR":
        return "HIGH"

    if severity == "WARNING":
        return "MEDIUM"

    if severity not in QUALITY_DEDUCTION:
        return "LOW"

    return severity


# =========================================================
# IS SECURITY ISSUE
# =========================================================

def is_security_issue(
    finding: Dict[str, Any]
) -> bool:

    tool = str(
        finding.get("tool", "")
    ).lower()

    category = str(
        finding.get("category", "")
    ).lower()

    message = str(
        finding.get("message", "")
    ).lower()

    if tool == "bandit":
        return True

    if "security" in category:
        return True

    if "security" in message:
        return True

    return False

# =========================================================
# CALCULATE SCORES
# =========================================================

def calculate_scores(
    findings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate quality, security and risk scores.
    """

    quality_score = 100.0
    security_score = 100.0

    summary = {
        "total": len(findings),
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
    }

    for finding in findings:

        severity = normalize_severity(
            finding.get("severity")
        )

        summary[severity.lower()] += 1

        quality_score -= QUALITY_DEDUCTION.get(
            severity,
            1,
        )

        if is_security_issue(finding):

            security_score -= SECURITY_DEDUCTION.get(
                severity,
                1,
            )

    quality_score = max(0.0, quality_score)
    security_score = max(0.0, security_score)

    risk_score = (
        summary["critical"] * 10
        + summary["high"] * 6
        + summary["medium"] * 3
        + summary["low"]
    )

    risk_score = min(risk_score, 100)

    overall_score = round(
        (quality_score + security_score) / 2,
        2,
    )

    if overall_score >= 90:
        grade = "A"

    elif overall_score >= 80:
        grade = "B"

    elif overall_score >= 70:
        grade = "C"

    elif overall_score >= 60:
        grade = "D"

    else:
        grade = "F"

    logger.info(
        "Quality: %.2f | Security: %.2f",
        quality_score,
        security_score,
    )

    return {
        "quality_score": round(
            quality_score,
            2,
        ),
        "security_score": round(
            security_score,
            2,
        ),
        "overall_score": overall_score,
        "risk_score": risk_score,
        "grade": grade,
        "summary": summary,
    }


# =========================================================
# PRINT SCORECARD
# =========================================================

def scorecard(
    findings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Wrapper function for score calculation.
    """

    return calculate_scores(findings)


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "calculate_scores",
    "scorecard",
]