import requests

BASE_URL = "http://127.0.0.1:8000"


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