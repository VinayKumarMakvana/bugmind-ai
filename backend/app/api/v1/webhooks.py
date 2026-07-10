from __future__ import annotations

import logging
from typing import Dict, Any

from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# WEBHOOK ENDPOINTS
# =========================================================

@router.post("/github")
async def github_webhook(request: Request) -> Dict[str, str]:
    """
    Handle incoming GitHub webhooks for repository events.
    """

    # Extract standard github headers for logging purposes
    event = request.headers.get("X-GitHub-Event", "unknown")
    signature = request.headers.get("X-Hub-Signature-256", "none")

    logger.info(
        "Received GitHub Webhook (Event: %s, Signature: %s)",
        event,
        signature,
    )

    # In local mode we ignore actual syncs since we process local paths.
    # Future implementation will handle PR synchronizations here.
    
    logger.info("Ignoring GitHub webhook in local mode.")

    return {
        "status": "ignored",
        "message": "GitHub webhooks are disabled in local mode.",
    }

