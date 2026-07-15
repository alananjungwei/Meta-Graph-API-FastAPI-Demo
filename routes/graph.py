from fastapi import APIRouter
from pydantic import BaseModel
class PostRequest(BaseModel):
    message: str


from services.graph_api import get_app_info
from services.facebook_service import (
    get_me,
    get_pages,
    get_page,
    create_post,
    get_posts,
)

router = APIRouter(
    prefix="/graph",
    tags=["Graph API"]
)


@router.get("/")
def graph_home():
    return {
        "message": "Welcome to the Graph API Router!"
    }

@router.get("/app-info")
def app_info():
    return get_app_info()

@router.get("/me")
def me():
    return get_me()

@router.get("/pages")
def pages():
    return get_pages()

@router.get("/page")
def page():
    return get_page()


@router.post("/post")
def post_to_page(request: PostRequest):
    return create_post(request.message)

@router.get("/posts")
def posts():
    return get_posts()