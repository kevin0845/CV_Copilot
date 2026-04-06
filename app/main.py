from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(
    title="CV Copilot API",
    version="0.1.0",
    description="FastAPI backend for resume, job description, and fit analysis workflows.",
)

app.include_router(api_router)
