import requests


BASE_URL = "http://127.0.0.1:8000"


# ==================================================
# Dashboard Metrics
# ==================================================

def get_total_messages():

    response = requests.get(
        f"{BASE_URL}/analytics/messages"
    )

    return response.json()


def get_unique_customers():

    response = requests.get(
        f"{BASE_URL}/analytics/users"
    )

    return response.json()


def get_sentiment_distribution():

    response = requests.get(
        f"{BASE_URL}/analytics/sentiment"
    )

    return response.json()


def get_intent_distribution():

    response = requests.get(
        f"{BASE_URL}/analytics/intents"
    )

    return response.json()


def get_platform_distribution():

    response = requests.get(
        f"{BASE_URL}/analytics/platforms"
    )

    return response.json()


# ==================================================
# Conversations
# ==================================================

def get_recent_conversations(limit=20):

    response = requests.get(
        f"{BASE_URL}/analytics/recent",
        params={"limit": limit},
    )

    return response.json()