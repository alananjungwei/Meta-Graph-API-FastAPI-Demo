from fastapi import APIRouter, HTTPException, Query, Request
import requests 
from fastapi.responses import RedirectResponse

from services.config import (
    VERIFY_TOKEN,
    INSTAGRAM_USER_ID,
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_GRAPH_BASE_URL,
)

from services.instagram_service import (
    get_login_url,
    exchange_code_for_token,
    get_account,
    send_message,
)

router = APIRouter(
    prefix="/instagram",
    tags=["Instagram"],
)


# ==================================================
# Instagram Login
# ==================================================

@router.get("/login")
def login():

    return RedirectResponse(
        url=get_login_url()
    )

@router.post("/subscribe")
def subscribe_webhook():

    url = (
        f"{INSTAGRAM_GRAPH_BASE_URL}/"
        f"{INSTAGRAM_USER_ID}/subscribed_apps"
    )

    params = {
        "subscribed_fields": "messages",
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }

    response = requests.post(
        url,
        params=params,
    )

    print("\n" + "=" * 80)
    print("INSTAGRAM WEBHOOK SUBSCRIPTION")
    print("=" * 80)
    print("URL:", url)
    print("Status:", response.status_code)
    print("Response:", response.text)
    print("=" * 80)

    return {
        "status_code": response.status_code,
        "response": response.json(),
    }
# ==================================================
# Instagram OAuth Callback
# ==================================================

@router.get("/callback")
def callback(
    code: str = Query(None),
    state: str = Query(None),
):

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code",
        )

    token_data = exchange_code_for_token(code)

    return {
        "status": "success",
        "token_received": "access_token" in token_data,
        "token_data": token_data,
    }


# ==================================================
# Test Instagram Account
# ==================================================

@router.get("/me")
def me():

    return get_account()





# ==================================================
# Instagram Webhook Verification
# ==================================================

@router.get("/webhook")
def verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):

    from services.config import VERIFY_TOKEN

    if (
        hub_mode == "subscribe"
        and hub_verify_token == VERIFY_TOKEN
    ):
        return int(hub_challenge)

    raise HTTPException(
        status_code=403,
        detail="Verification failed",
    )


# ==================================================
# Instagram Webhook
# ==================================================

@router.post("/webhook")
async def webhook(request: Request):

    body = await request.json()

    print("\n" + "=" * 80)
    print("INSTAGRAM WEBHOOK")
    print(body)
    print("=" * 80)

    if body.get("object") != "instagram":
        return {"status": "ignored"}

    for entry in body.get("entry", []):

        for event in entry.get("messaging", []):

            # Ignore events that are not messages
            if "message" not in event:
                continue

            # Ignore messages sent by our own Instagram account
            if event["message"].get("is_echo"):
                continue

            sender_id = event["sender"]["id"]
            text = event["message"].get("text", "")

            # Ignore messages without text
            if not text:
                continue

            print("Sender:", sender_id)
            print("Message:", text)

            # ------------------------------------------
            # TEMPORARY TEST RESPONSE
            # ------------------------------------------

            send_message(
                recipient_id=sender_id,
                message="Hello! Instagram V2 is working 🤖",
            )

    return {"status": "ok"}