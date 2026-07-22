
import requests
from urllib.parse import urlencode
from services.config import (
    META_APP_ID,
    META_APP_SECRET,
    REDIRECT_URI,
    GRAPH_BASE_URL,
    PAGE_ID,
    ACCESS_TOKEN,
    CONFIG_ID
)


def get_login_url():
    """
    Getting the login info for meta accounts. 
    """
    params = {
        "client_id": META_APP_ID,
        "config_id": CONFIG_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "state": "demo123",
    }

    return (
        "https://www.facebook.com/v25.0/dialog/oauth?"
        + urlencode(params)
    )


def update_env(key: str, value: str):
    """
    Update a value inside the .env file.
    """

    with open(".env", "r") as f:
        lines = f.readlines()

    with open(".env", "w") as f:

        found = False

        for line in lines:

            if line.startswith(f"{key}="):
                f.write(f"{key}={value}\n")
                found = True
            else:
                f.write(line)

        if not found:
            f.write(f"{key}={value}\n")


def handle_callback(code: str, state: str):
    """
    Exchange the authorization code for a short-lived token,
    then exchange it for a long-lived token,
    then retrieve the Page access token.
    """

    # --------------------------------------------------
    # Step 1: Exchange authorization code for short-lived token
    # --------------------------------------------------
    response = requests.get(
        "https://graph.facebook.com/v25.0/oauth/access_token",
        params={
            "client_id": META_APP_ID,
            "client_secret": META_APP_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        },
    )

    short_data = response.json()

    print("========== SHORT-LIVED TOKEN ==========")
    print(short_data)

    if "access_token" not in short_data:
        return {
            "error": "Failed to obtain short-lived token.",
            "response": short_data,
        }

    short_token = short_data["access_token"]

    print("Short-lived token acquired!")
    print(short_token[:30])

    # --------------------------------------------------
    # Step 2: Exchange for long-lived token
    # --------------------------------------------------
    print("Exchanging for long-lived token...")

    long_response = requests.get(
        "https://graph.facebook.com/v25.0/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": META_APP_ID,
            "client_secret": META_APP_SECRET,
            "fb_exchange_token": short_token,
        },
    )

    long_data = long_response.json()

    print("========== LONG-LIVED TOKEN ==========")
    print(long_data)

    if "access_token" not in long_data:
        return {
            "error": "Failed to obtain long-lived token.",
            "response": long_data,
        }

    long_token = long_data["access_token"]

    # --------------------------------------------------
    # Step 3: Get Page information
    # --------------------------------------------------
    pages_response = requests.get(
        "https://graph.facebook.com/v25.0/me/accounts",
        params={
            "access_token": long_token,
        },
    )

    page_data = pages_response.json()

    print("========== PAGE INFO ==========")
    print(page_data)

    page = page_data["data"][0]

    page_token = page["access_token"]

    update_env("ACCESS_TOKEN", page_token)
    update_env("PAGE_ID", page["id"])

    print("✅ Page Access Token saved to .env")


    return {
        "status": "success",
        "state": state,
        "page_name": page["name"],
        "page_id": page["id"],
        "page_token_received": True,
    }

def get_me():

    response = requests.get(
        "https://graph.facebook.com/v25.0/me",
        params={
            "fields": "id,name",
            "access_token": ACCESS_TOKEN,
        },
    )

    return response.json()

def get_pages():

    response = requests.get(
        "https://graph.facebook.com/v25.0/me/accounts",
        params={
            "access_token": ACCESS_TOKEN,
        },
    )

    return response.json()

def get_page():

    response = requests.get(
        f"{GRAPH_BASE_URL}/{PAGE_ID}",
        params={
            "fields": "id,name",
            "access_token": ACCESS_TOKEN,
        },
    )

    return response.json()

def create_post(message: str):

    response = requests.post(
        f"{GRAPH_BASE_URL}/{PAGE_ID}/feed",
        data={
            "message": message,
            "access_token": ACCESS_TOKEN,
        },
    )

    return response.json()


def get_posts():

    response = requests.get(
        f"{GRAPH_BASE_URL}/{PAGE_ID}/posts",
        params={
            "fields": "id,message,created_time",
            "access_token": ACCESS_TOKEN,
        },
    )

    return response.json()

def get_comments(post_id: str):

    response = requests.get(
        f"{GRAPH_BASE_URL}/{post_id}/comments",
        params={
            "fields": "id,message,from,created_time",
            "access_token": ACCESS_TOKEN,
        },
    )

    return response.json()

def reply_to_comment(comment_id: str, message: str):

    response = requests.post(
        f"{GRAPH_BASE_URL}/{comment_id}/comments",
        data={
            "message": message,
            "access_token": ACCESS_TOKEN,
        },
    )

    return response.json()

def send_message(recipient_id: str, message: str):

    response = requests.post(
        f"{GRAPH_BASE_URL}/{PAGE_ID}/messages",
        params={
            "access_token": ACCESS_TOKEN,
        },
        json={
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message
            }
        }
    )

    print("Status:", response.status_code)
    print("Headers:", response.headers)
    print("Body:", response.text)
    print(ACCESS_TOKEN[:25])

    return response.json()