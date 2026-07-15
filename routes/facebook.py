from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from services.facebook_service import (
    get_login_url,
    handle_callback,
)

router = APIRouter(
    prefix="/facebook",
    tags=["Facebook"],
)


@router.get("/login")
def login():

    return RedirectResponse(
        url=get_login_url()
    )


@router.get("/callback")
def callback(
    code: str = Query(None),
    state: str = Query(None),
):

    return handle_callback(code, state)