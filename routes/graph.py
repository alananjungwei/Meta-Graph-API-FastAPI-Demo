from fastapi import APIRouter

from services.graph_api import get_app_info

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