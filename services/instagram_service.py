import requests
from urllib.parse import urlencode

from services.config import (
    INSTAGRAM_APP_ID,
    INSTAGRAM_APP_SECRET,
    INSTAGRAM_REDIRECT_URI,
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_USER_ID,
    INSTAGRAM_GRAPH_BASE_URL,
)


# ==================================================
# Instagram Login
# ==================================================

def get_login_url():
    """
    Generate the Instagram Login authorization URL.
    """

    params = {
        "client_id": INSTAGRAM_APP_ID,
        "redirect_uri": INSTAGRAM_REDIRECT_URI,
        "response_type": "code",
        "scope": (
            "instagram_business_basic,"
            "instagram_business_manage_messages,"
            "instagram_business_manage_comments,"
            "instagram_business_content_publish"
        ),
        "state": "instagram_demo",
    }

    return (
        "https://www.instagram.com/oauth/authorize?"
        + urlencode(params)
    )


# ==================================================
# Exchange authorization code
# ==================================================

def exchange_code_for_token(code: str):

    response = requests.post(
        "https://api.instagram.com/oauth/access_token",
        data={
            "client_id": INSTAGRAM_APP_ID,
            "client_secret": INSTAGRAM_APP_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": INSTAGRAM_REDIRECT_URI,
            "code": code,
        },
    )

    print("\n========== INSTAGRAM TOKEN RESPONSE ==========")
    print("Status:", response.status_code)
    print("Body:", response.text)
    print("==============================================\n")

    response.raise_for_status()

    return response.json()


# ==================================================
# Get Instagram account
# ==================================================

def get_account():

    response = requests.get(
        f"{INSTAGRAM_GRAPH_BASE_URL}/me",
        params={
            "fields": "user_id,username,name,account_type",
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        },
    )

    print("\n========== INSTAGRAM ACCOUNT ==========")
    print("Status:", response.status_code)
    print("Body:", response.text)
    print("=======================================\n")

    return response.json()


# ==================================================
# Send Instagram message
# ==================================================

def send_message(recipient_id: str, message: str):

    url = f"{INSTAGRAM_GRAPH_BASE_URL}/{INSTAGRAM_USER_ID}/messages"

    payload = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message
        }
    }

    response = requests.post(
        url,
        json=payload,
        params={
            "access_token": INSTAGRAM_ACCESS_TOKEN
        },
    )

    print("\n========== INSTAGRAM SEND MESSAGE ==========")
    print("URL:", url)
    print("Recipient ID:", recipient_id)
    print("Status:", response.status_code)
    print("Response:", response.text)
    print("============================================\n")

    return response.json()