def calculate_scores(findings):
    quality_score = 100.0
    security_score = 100.0

    for finding in findings:
        # Default to LOW if not provided
        severity = str(finding.get("severity") or "LOW").upper()
        
        # Deduct security score for bandit and security semgrep rules
        if finding.get("tool") == "bandit" or "security" in finding.get("description", "").lower():
            if severity in ["HIGH", "CRITICAL", "ERROR"]:
                security_score -= 15.0
            elif severity in ["MEDIUM", "WARNING"]:
                security_score -= 8.0
            else:
                security_score -= 3.0
                
        # Deduct quality score for all issues
        if severity in ["HIGH", "CRITICAL", "ERROR"]:
            quality_score -= 10.0
        elif severity in ["MEDIUM", "WARNING"]:
            quality_score -= 5.0
        else:
            quality_score -= 2.0

    return max(0.0, quality_score), max(0.0, security_score)
