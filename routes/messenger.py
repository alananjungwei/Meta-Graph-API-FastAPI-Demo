from fastapi import APIRouter, HTTPException, Query, Request 
from services.config import VERIFY_TOKEN
from services.facebook_service import send_message
from services.ai_service import generate_reply

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

    if body.get("object") == "page":

        for entry in body["entry"]:

            for event in entry["messaging"]:

                # Ignore events that aren't messages
                if "message" not in event:
                    continue

                # Ignore messages sent by the Page itself
                if event["message"].get("is_echo"):
                    continue

                # Ignore non-text messages (images, stickers, etc.)
                text = event["message"].get("text")
                if not text:
                    continue

                sender_id = event["sender"]["id"]

                print(f"Sender: {sender_id}")
                print(f"Message: {text}")

                # Generate AI reply
                try:
                    reply = generate_reply(text)
                except Exception as e:
                    print(f"OpenAI Error: {e}")
                    reply = "Sorry, something went wrong while generating a reply."

                # Safety guard: never send an empty message
                if not reply or not reply.strip():
                    reply = "Sorry, I couldn't generate a response."

                print(f"AI Reply: {repr(reply)}")

                result = send_message(
                    sender_id,
                    reply
                )

                print(result)

    return {"status": "ok"}