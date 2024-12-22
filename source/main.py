from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from source.core.config import settings 
from .api.base import router as base_router
from .auth.router import router as auth_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="source/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="source/templates")

app.include_router(base_router)
app.include_router(auth_router)