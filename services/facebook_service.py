
import requests
from urllib.parse import urlencode
from services.config import (
    META_APP_ID,
    META_APP_SECRET,
    REDIRECT_URI,
    GRAPH_BASE_URL,
)
from dotenv import load_dotenv

def get_login_url():

    params = {
        "client_id": META_APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "public_profile,email",
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