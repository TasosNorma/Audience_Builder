from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi import Depends
from source.auth.dependencies import get_current_user
from source.database.models import User


router = APIRouter()
templates = Jinja2Templates(directory="source/templates")

class UrlForm(BaseModel):
    url: str = ""

@router.get("/home", response_class=HTMLResponse)
async def home(request: Request,current_user: User = Depends(get_current_user) ):
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "form": UrlForm(),
            "result": None,
            "user":current_user
        }
    )