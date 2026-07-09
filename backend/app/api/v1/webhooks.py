from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/github")
async def github_webhook(request: Request):
    return {"status": "ignored", "message": "GitHub webhooks are disabled in local mode."}

