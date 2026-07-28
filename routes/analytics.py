from fastapi import APIRouter

from services.analytics_service import (
    get_total_messages,
    get_sentiment_distribution,
    get_intent_distribution,
    get_unique_customers,
    get_recent_conversations,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/messages")
def total_messages():

    return {
        "total_messages": get_total_messages()
    }


@router.get("/sentiment")
def sentiment_distribution():

    return get_sentiment_distribution()

@router.get("/intents")
def intent_distribution():

    return get_intent_distribution()

@router.get("/users")
def unique_customers():

    return {
        "unique_customers": get_unique_customers()
    }

@router.get("/recent")
def recent_conversations(limit: int = 20):

    return get_recent_conversations(limit)