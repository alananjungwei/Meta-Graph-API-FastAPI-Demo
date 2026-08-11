from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from services.facebook_service import (
    get_login_url,
    handle_callback,
    get_facebook_token_status,
    get_me,
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

@router.get("/token-status")
def facebook_token_status():
    return get_facebook_token_status()

@router.get("/me")
def facebook_me():
    return get_me()