
import requests
from urllib.parse import urlencode
from services.config import (
    META_APP_ID,
    META_APP_SECRET,
    REDIRECT_URI,
    GRAPH_BASE_URL,
    PAGE_ID,
    ACCESS_TOKEN
)


def get_login_url():
    """
    Getting the login info for meta accounts. 
    """
    params = {
        "client_id": META_APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "public_profile",
        "response_type": "code",
        "state": "demo123",
    }

    return (
        "https://www.facebook.com/v25.0/dialog/oauth?"
        + urlencode(params)
    )


def handle_callback(code: str, state: str):
    """
    Exchange the authorization code for an access token.
    """

    response = requests.get(
        "https://graph.facebook.com/v25.0/oauth/access_token",
        params={
            "client_id": META_APP_ID,
            "client_secret": META_APP_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        },
    )

    return {
        "state": state,
        "facebook_response": response.json(),
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