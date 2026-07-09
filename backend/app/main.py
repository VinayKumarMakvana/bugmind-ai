from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.v1 import auth, webhooks, repos, chat

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allowing all origins to fix 'Failed to fetch' CORS errors
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])
app.include_router(webhooks.router, prefix=settings.API_V1_STR + "/webhooks", tags=["webhooks"])
app.include_router(repos.router, prefix=settings.API_V1_STR + "/repos", tags=["repos"])
app.include_router(chat.router, prefix=settings.API_V1_STR + "/chat", tags=["chat"])



# Add new stream router
from .api.v1 import stream
app.include_router(stream.router, prefix=settings.API_V1_STR + "/stream", tags=["stream"])

@app.on_event("startup")
async def startup_event():
    import asyncio
    from .core.events import event_manager
    event_manager.set_loop(asyncio.get_running_loop())

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
