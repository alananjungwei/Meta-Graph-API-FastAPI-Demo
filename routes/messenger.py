from fastapi import APIRouter, HTTPException, Query, Request

from services.config import VERIFY_TOKEN
from services.facebook_service import send_message
from services.rag_service import generate_reply
from services.intent_service import detect_intent
from services.sentiment_service import detect_sentiment
from services.database_service import save_conversation

router = APIRouter(
    prefix="/messenger",
    tags=["Messenger"],
)


@router.get("/webhook")
def verify(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)

    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def webhook(request: Request):

    body = await request.json()

    print("========== NEW WEBHOOK EVENT ==========")
    print(body)
    print("=======================================")

    if body.get("object") != "page":
        return {"status": "ignored"}

    for entry in body["entry"]:

        for event in entry["messaging"]:

            # ----------------------------------------
            # Ignore unsupported events
            # ----------------------------------------

            if "message" not in event:
                continue

            if event["message"].get("is_echo"):
                continue

            text = event["message"].get("text")
            if not text:
                continue

            sender_id = event["sender"]["id"]

            print(f"Sender: {sender_id}")
            print(f"Message: {text}")

            # ----------------------------------------
            # NLP Pipeline
            # ----------------------------------------

            intent = detect_intent(text)
            sentiment = detect_sentiment(text)

            print("========== MESSAGE ANALYSIS ==========")
            print(f"Intent: {intent}")
            print(f"Sentiment: {sentiment}")
            print("======================================")

            # ----------------------------------------
            # Generate AI response
            # ----------------------------------------

            try:
                reply = generate_reply(
                    sender_id=sender_id,
                    text=text,
                    intent=intent,
                    sentiment=sentiment,
                )

            except Exception as e:
                print(f"OpenAI Error: {e}")
                reply = "Sorry, something went wrong while generating a reply."

            if not reply or not reply.strip():
                reply = "Sorry, I couldn't generate a response."

            print(f"AI Reply: {repr(reply)}")

            # ----------------------------------------
            # Send reply to Messenger
            # ----------------------------------------

            try:
                result = send_message(sender_id, reply)
                print(result)

            except Exception as e:
                print(f"Messenger Error: {e}")

            # ----------------------------------------
            # Store conversation
            # ----------------------------------------

            save_conversation(
                sender_id=sender_id,
                message=text,
                intent=intent,
                sentiment=sentiment,
                reply=reply,
            )

    return {"status": "ok"}