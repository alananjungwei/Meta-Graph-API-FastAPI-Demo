
import requests
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from services.config import (
    META_APP_ID,
    META_APP_SECRET,
    FACEBOOK_REDIRECT_URI,
    GRAPH_BASE_URL,
    CONFIG_ID
)


def get_login_url():
    """
    Getting the login info for meta accounts. 
    """
    params = {
        "client_id": META_APP_ID,
        "config_id": CONFIG_ID,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
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

    # Keep the current Python process in sync with .env
    os.environ[key] = value

def get_current_access_token():
    """
    Return the current Facebook Page access token.

    The token may be updated during the Facebook login flow,
    so we read it from the current process environment instead
    of using the value imported when the module started.
    """

    token = os.getenv("ACCESS_TOKEN")

    if not token:
        raise RuntimeError(
            "Facebook Page access token is not configured."
        )

    return token

def get_current_page_id():
    """
    Return the current Facebook Page ID.

    The Page ID may be updated during the Facebook login flow,
    so read it from the current process environment.
    """

    page_id = os.getenv("PAGE_ID")

    if not page_id:
        raise RuntimeError(
            "Facebook Page ID is not configured."
        )

    return page_id

def get_token_expiry_from_meta(access_token: str):
    """
    Ask Meta's Debug Token endpoint for the token's
    actual expiration timestamp.
    """

    app_access_token = f"{META_APP_ID}|{META_APP_SECRET}"

    response = requests.get(
        "https://graph.facebook.com/v25.0/debug_token",
        params={
            "input_token": access_token,
            "access_token": app_access_token,
        },
    )

    debug_data = response.json()

    print("========== DEBUG FACEBOOK TOKEN ==========")
    print({
        "is_valid": debug_data.get("data", {}).get("is_valid"),
        "app_id": debug_data.get("data", {}).get("app_id"),
        "expires_at": debug_data.get("data", {}).get("expires_at"),
        "data_access_expires_at": debug_data.get("data", {}).get("data_access_expires_at"),
    })

    if response.status_code != 200:
        print("⚠️ Failed to debug Facebook access token.")
        return None

    data = debug_data.get("data", {})
    expires_at_timestamp = data.get("expires_at")

    if not expires_at_timestamp:
        print("⚠️ Meta did not provide an expires_at value.")
        return None

    expires_at = datetime.fromtimestamp(
        expires_at_timestamp,
        tz=timezone.utc,
    ).isoformat()

    print("Facebook user token expires at:", expires_at)

    update_env(
        "USER_TOKEN_EXPIRES_AT",
        expires_at,
    )

    return expires_at

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
            "redirect_uri": FACEBOOK_REDIRECT_URI,
            "code": code,
        },
    )

    short_data = response.json()

    print("========== SHORT-LIVED TOKEN ==========")
    print({
        "token_received": "access_token" in short_data,
        "expires_in": short_data.get("expires_in"),
    })

    if "access_token" not in short_data:
        return {
            "error": "Failed to obtain short-lived token.",
            "response": short_data,
        }

    short_token = short_data["access_token"]

    print("Short-lived token acquired!")

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
    print({
        "token_received": "access_token" in long_data,
        "expires_in": long_data.get("expires_in"),
        "token_type": long_data.get("token_type"),
    })

    if "access_token" not in long_data:
        return {
            "error": "Failed to obtain long-lived token.",
            "response": long_data,
        }

    long_token = long_data["access_token"]

    # Meta may not return expires_in in the token exchange response.
    # Ask the Debug Token endpoint for the actual expiration timestamp.

    expires_at = get_token_expiry_from_meta(long_token)

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

def validate_facebook_token():
    """
    Validate the current Facebook Page access token with Meta.
    Returns the token debug information.
    """

    token = os.getenv("ACCESS_TOKEN")

    if not token:
        return {
            "valid": False,
            "message": "No Facebook Page access token is configured."
        }

    app_access_token = f"{META_APP_ID}|{META_APP_SECRET}"

    response = requests.get(
        "https://graph.facebook.com/v25.0/debug_token",
        params={
            "input_token": token,
            "access_token": app_access_token,
        },
    )

    try:
        data = response.json()
    except Exception:
        return {
            "valid": False,
            "message": "Invalid response from Meta."
        }

    debug_data = data.get("data", {})

    return {
        "valid": debug_data.get("is_valid", False),
        "app_id": debug_data.get("app_id"),
        "type": debug_data.get("type"),
        "expires_at": debug_data.get("expires_at"),
        "data_access_expires_at": debug_data.get(
            "data_access_expires_at"
        ),
    }

#def get_facebook_token_expiry():
#    """
#    Read the Facebook access token expiration timestamp
#    from the .env file.
#    """
#
#    expires_at = os.getenv("ACCESS_TOKEN_EXPIRES_AT")
#
#    if not expires_at:
#        print(
#            "⚠️ Facebook token expiry unknown. "
#            "Re-authentication may be required."
#        )
#        return None
#
#    try:
#        expiry = datetime.fromisoformat(expires_at)
#
#        # Make sure the datetime is timezone-aware
#        if expiry.tzinfo is None:
#            expiry = expiry.replace(tzinfo=timezone.utc)
#
#        return expiry
#
#    except ValueError:
#        print(
#            "⚠️ Invalid Facebook token expiry timestamp."
#        )
#        return None


def get_facebook_token_status():
    """
    Return the current Facebook Page access token status.
    """

    token_info = validate_facebook_token()

    if not token_info["valid"]:
        return {
            "status": "invalid",
            "expires_at": token_info.get("expires_at"),
            "days_remaining": None,
            "message": "Facebook Page access token is invalid. Re-authentication is required.",
        }

    expires_at = token_info.get("expires_at")

    # Meta may not provide an explicit expiry timestamp
    if not expires_at:
        return {
            "status": "healthy",
            "expires_at": None,
            "days_remaining": None,
            "message": "Facebook Page access token is valid. Meta did not provide an explicit expiry date.",
        }

    expiry = datetime.fromtimestamp(
        expires_at,
        tz=timezone.utc,
    )

    now = datetime.now(timezone.utc)
    remaining = expiry - now
    days_remaining = remaining.total_seconds() / 86400

    if remaining <= timedelta(0):
        return {
            "status": "expired",
            "expires_at": expiry.isoformat(),
            "days_remaining": 0,
            "message": "Facebook Page access token has expired.",
        }

    if remaining <= timedelta(days=7):
        return {
            "status": "critical",
            "expires_at": expiry.isoformat(),
            "days_remaining": round(days_remaining, 2),
            "message": "Facebook Page access token expires within 7 days.",
        }

    if remaining <= timedelta(days=30):
        return {
            "status": "approaching",
            "expires_at": expiry.isoformat(),
            "days_remaining": round(days_remaining, 2),
            "message": "Facebook Page access token is approaching expiry.",
        }

    return {
        "status": "healthy",
        "expires_at": expiry.isoformat(),
        "days_remaining": round(days_remaining, 2),
        "message": "Facebook Page access token is healthy.",
    }


def ensure_facebook_token_valid():
    """
    Check whether the Facebook Page access token is still valid.

    This function does NOT silently re-authenticate.
    If the token is invalid, the user must go through
    the Facebook login flow again.
    """

    status = get_facebook_token_status()

    if status["status"] == "invalid":
        print(
            "❌ Facebook Page access token is invalid. "
            "Re-authentication required."
        )

    elif status["status"] == "healthy":
        print(
            "✅ Facebook Page access token is healthy."
        )

    elif status["status"] == "approaching":
        print(
            "⚠️ Facebook Page access token approaching expiry."
        )

    elif status["status"] == "critical":
        print(
            "🚨 Facebook Page access token expires soon. "
            "Re-authentication recommended."
        )

    elif status["status"] == "expired":
        print(
            "❌ Facebook Page access token has expired. "
            "Re-authentication required."
        )

    return get_current_access_token()


def get_me():

    response = requests.get(
        "https://graph.facebook.com/v25.0/me",
        params={
            "fields": "id,name",
            "access_token": get_current_access_token(),
        },
    )

    return response.json()

def get_pages():

    response = requests.get(
        "https://graph.facebook.com/v25.0/me/accounts",
        params={
            "access_token": get_current_access_token(),
        },
    )

    return response.json()

def get_page():

    response = requests.get(
        f"{GRAPH_BASE_URL}/{get_current_page_id()}",
        params={
            "fields": "id,name",
            "access_token": get_current_access_token(),
        },
    )

    return response.json()

def create_post(message: str):

    response = requests.post(
        f"{GRAPH_BASE_URL}/{get_current_page_id()}/feed",
        data={
            "message": message,
            "access_token": get_current_access_token(),
        },
    )

    return response.json()


def get_posts():

    response = requests.get(
        f"{GRAPH_BASE_URL}/{get_current_page_id()}/posts",
        params={
            "fields": "id,message,created_time",
            "access_token": get_current_access_token(),
        },
    )

    return response.json()

def get_comments(post_id: str):

    response = requests.get(
        f"{GRAPH_BASE_URL}/{post_id}/comments",
        params={
            "fields": "id,message,from,created_time",
            "access_token": get_current_access_token(),
        },
    )

    return response.json()

def reply_to_comment(comment_id: str, message: str):

    response = requests.post(
        f"{GRAPH_BASE_URL}/{comment_id}/comments",
        data={
            "message": message,
            "access_token": get_current_access_token(),
        },
    )

    return response.json()

def send_message(recipient_id: str, message: str):
    """
    Send a Facebook Messenger or Instagram DM reply
    using Meta's unified messaging endpoint.
    """

    url = f"{GRAPH_BASE_URL}/{get_current_page_id()}/messages"

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
        params={
            "access_token": get_current_access_token(),
        },
        json=payload,
    )

    # -----------------------------
    # Debug output
    # -----------------------------
    print("\n" + "=" * 80)
    print("META SEND MESSAGE DEBUG")
    print("=" * 80)
    print(f"URL          : {url}")
    print(f"Recipient ID : {recipient_id}")
    print(f"Message      : {message}")
    print(f"Status Code  : {response.status_code}")

    try:
        body = response.json()
    except Exception:
        body = response.text

    print("Response:")
    print(body)
    print("=" * 80 + "\n")

    return body