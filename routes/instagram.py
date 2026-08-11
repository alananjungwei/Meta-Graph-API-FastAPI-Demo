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
    update_env,
    ensure_instagram_token_valid,
)


from services.rag_service import generate_reply
from services.intent_service import detect_intent
from services.sentiment_service import detect_sentiment
from services.database_service import save_conversation

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
        "access_token": ensure_instagram_token_valid(),
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

    # ----------------------------------------------
    # Exchange authorization code for access token
    # ----------------------------------------------

    token_data = exchange_code_for_token(code)

    # ----------------------------------------------
    # Check token response
    # ----------------------------------------------

    if "access_token" not in token_data:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Failed to obtain Instagram access token",
                "response": token_data,
            },
        )

    instagram_access_token = (
        token_data["access_token"]
    )

    # ----------------------------------------------
    # Save token to .env
    # ----------------------------------------------

    update_env(
        "INSTAGRAM_ACCESS_TOKEN",
        instagram_access_token,
    )

    print(
        "✅ Instagram access token saved to .env"
    )

    # ----------------------------------------------
    # Return success
    # ----------------------------------------------

    return {
        "status": "success",
        "token_received": True,
        "state": state,
        "message": (
            "Instagram connected successfully. "
            "Access token saved."
        ),
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

            # ------------------------------------------
            # Ignore events that are not messages
            # ------------------------------------------

            if "message" not in event:
                continue

            # ------------------------------------------
            # Ignore messages sent by our own account
            # ------------------------------------------

            if event["message"].get("is_echo"):
                continue

            sender_id = event["sender"]["id"]
            text = event["message"].get("text", "")

            # ------------------------------------------
            # Ignore messages without text
            # ------------------------------------------

            if not text:
                continue

            print("Sender:", sender_id)
            print("Message:", text)

            # ------------------------------------------
            # NLP Pipeline
            # ------------------------------------------

            intent = detect_intent(text)
            sentiment = detect_sentiment(text)

            print("========== MESSAGE ANALYSIS ==========")
            print("Intent:", intent)
            print("Sentiment:", sentiment)
            print("======================================")

            # ------------------------------------------
            # Generate AI response
            # ------------------------------------------

            try:

                reply = generate_reply(
                    sender_id=sender_id,
                    text=text,
                    intent=intent,
                    sentiment=sentiment,
                )

            except Exception as e:

                print(f"OpenAI Error: {e}")

                reply = (
                    "Sorry, something went wrong "
                    "while generating a reply."
                )

            if not reply or not reply.strip():

                reply = (
                    "Sorry, I couldn't generate a response."
                )

            print("AI Reply:", repr(reply))

            # ------------------------------------------
            # Send reply to Instagram
            # ------------------------------------------

            try:

                result = send_message(
                    recipient_id=sender_id,
                    message=reply,
                )

                print(result)

            except Exception as e:

                print(f"Instagram Error: {e}")

            # ------------------------------------------
            # Store conversation
            # ------------------------------------------

            save_conversation(
                sender_id=sender_id,
                message=text,
                intent=intent,
                sentiment=sentiment,
                reply=reply,
                platform="instagram",
            )

    return {"status": "ok"}