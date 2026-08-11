
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

    token = os.getenv("PAGE_ACCESS_TOKEN")

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

    if expires_at_timestamp is None:
        print("⚠️ Meta did not provide an expires_at value.")
        return None

    if expires_at_timestamp == 0:
        print(
            "ℹ️ Meta returned expires_at=0. "
            "No explicit token expiry timestamp is available."
        )
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

    update_env(
        "ACCESS_TOKEN",
        long_token,
    )

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
    print({
        "pages_received": len(page_data.get("data", [])),
        "page_name": (
            page_data["data"][0].get("name")
            if page_data.get("data")
            else None
        ),
        "page_id": (
            page_data["data"][0].get("id")
            if page_data.get("data")
            else None
        ),
        "page_token_received": bool(
            page_data.get("data")
            and page_data["data"][0].get("access_token")
        ),
    })

    page = page_data["data"][0]

    page_token = page["access_token"]

    update_env("PAGE_ACCESS_TOKEN", page_token)
    update_env("PAGE_ID", page["id"])

    print("✅ Page Access Token saved to .env")


    return {
        "status": "success",
        "state": state,
        "page_name": page["name"],
        "page_id": page["id"],
        "page_token_received": True,
    }

def refresh_facebook_user_token():
    """
    Refresh the stored Facebook user token and obtain
    a fresh Page access token.
    """

    user_token = os.getenv("ACCESS_TOKEN")

    if not user_token:
        raise RuntimeError(
            "Facebook user access token is not configured in ACCESS_TOKEN."
        )

    print("\n" + "=" * 50)
    print("FACEBOOK TOKEN REFRESH")
    print("=" * 50)

    # --------------------------------------------------
    # Step 1: Exchange current user token
    # --------------------------------------------------

    response = requests.get(
        "https://graph.facebook.com/v25.0/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": META_APP_ID,
            "client_secret": META_APP_SECRET,
            "fb_exchange_token": user_token,
        },
    )

    data = response.json()

    print("Status:", response.status_code)
    print("Token received:", "access_token" in data)
    print("Expires in:", data.get("expires_in"))

    if "access_token" not in data:
        return {
            "status": "error",
            "message": "Failed to refresh Facebook user token.",
            "response": data,
        }

    new_user_token = data["access_token"]

    # --------------------------------------------------
    # Step 2: Save refreshed user token
    # --------------------------------------------------

    update_env(
        "ACCESS_TOKEN",
        new_user_token,
    )

    # --------------------------------------------------
    # Step 3: Check refreshed user-token expiry
    # --------------------------------------------------

    expires_at = get_token_expiry_from_meta(
        new_user_token
    )

    # --------------------------------------------------
    # Step 4: Get fresh Page access token
    # --------------------------------------------------

    pages_response = requests.get(
        "https://graph.facebook.com/v25.0/me/accounts",
        params={
            "access_token": new_user_token,
        },
    )

    page_data = pages_response.json()

    print(
        "Page response status:",
        pages_response.status_code
    )

    if not page_data.get("data"):
        return {
            "status": "error",
            "message": "No Facebook Pages were returned.",
            "response": page_data,
        }

    page = page_data["data"][0]

    page_token = page["access_token"]
    page_id = page["id"]

    # --------------------------------------------------
    # Step 5: Save fresh Page credentials
    # --------------------------------------------------

    update_env(
        "PAGE_ACCESS_TOKEN",
        page_token,
    )

    update_env(
        "PAGE_ID",
        page_id,
    )

    print("✅ Facebook Page access token refreshed.")
    print("Page:", page["name"])
    print("Page ID:", page_id)

    return {
        "status": "success",
        "page_name": page["name"],
        "page_id": page_id,
        "page_token_received": True,
        "user_token_expires_at": expires_at,
    }

def validate_facebook_token():
    """
    Validate the current Facebook Page access token with Meta.
    Returns the token debug information.
    """

    token = os.getenv("PAGE_ACCESS_TOKEN")

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


def get_facebook_token_status():
    """
    Return the current Facebook Page token status
    together with the underlying user token expiry.
    """

    # --------------------------------------------------
    # Step 1: Validate Page access token
    # --------------------------------------------------

    page_token_info = validate_facebook_token()

    if not page_token_info["valid"]:
        return {
            "status": "invalid",
            "page_token_expires_at": page_token_info.get("expires_at"),
            "page_token_days_remaining": None,
            "user_token_expires_at": None,
            "user_token_days_remaining": None,
            "message": (
                "Facebook Page access token is invalid. "
                "Re-authentication is required."
            ),
        }

    # --------------------------------------------------
    # Step 2: Check USER token expiry
    # --------------------------------------------------

    user_token = os.getenv("ACCESS_TOKEN")

    user_token_expires_at = None
    user_token_days_remaining = None

    if user_token:
        user_token_expires_at = get_token_expiry_from_meta(
            user_token
        )

    # --------------------------------------------------
    # Step 3: Calculate user-token days remaining
    # --------------------------------------------------

    if user_token_expires_at:
        expiry = datetime.fromisoformat(
            user_token_expires_at
        )

        if expiry.tzinfo is None:
            expiry = expiry.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(timezone.utc)

        remaining = expiry - now

        user_token_days_remaining = (
            remaining.total_seconds() / 86400
        )

    # --------------------------------------------------
    # Step 4: Page token expiry
    # --------------------------------------------------

    page_token_expires_at = page_token_info.get(
        "expires_at"
    )

    page_token_days_remaining = None

    if page_token_expires_at:
        page_expiry = datetime.fromtimestamp(
            page_token_expires_at,
            tz=timezone.utc,
        )

        page_remaining = (
            page_expiry
            - datetime.now(timezone.utc)
        )

        page_token_days_remaining = (
            page_remaining.total_seconds() / 86400
        )

    # --------------------------------------------------
    # Step 5: Determine overall status
    # --------------------------------------------------

    if (
        user_token_days_remaining is not None
        and user_token_days_remaining <= 0
    ):
        return {
            "status": "expired",
            "page_token_expires_at": (
                page_expiry.isoformat()
                if page_token_expires_at
                else None
            ),
            "page_token_days_remaining": (
                round(page_token_days_remaining, 2)
                if page_token_days_remaining is not None
                else None
            ),
            "user_token_expires_at": user_token_expires_at,
            "user_token_days_remaining": 0,
            "message": (
                "Facebook Page token is currently valid, "
                "but the underlying user token has expired."
            ),
        }

    if (
        user_token_days_remaining is not None
        and user_token_days_remaining <= 7
    ):
        return {
            "status": "critical",
            "page_token_expires_at": (
                page_expiry.isoformat()
                if page_token_expires_at
                else None
            ),
            "page_token_days_remaining": (
                round(page_token_days_remaining, 2)
                if page_token_days_remaining is not None
                else None
            ),
            "user_token_expires_at": user_token_expires_at,
            "user_token_days_remaining": round(
                user_token_days_remaining,
                2,
            ),
            "message": (
                "Facebook user token expires within 7 days. "
                "Token refresh is recommended."
            ),
        }

    if (
        user_token_days_remaining is not None
        and user_token_days_remaining <= 30
    ):
        return {
            "status": "approaching",
            "page_token_expires_at": (
                page_expiry.isoformat()
                if page_token_expires_at
                else None
            ),
            "page_token_days_remaining": (
                round(page_token_days_remaining, 2)
                if page_token_days_remaining is not None
                else None
            ),
            "user_token_expires_at": user_token_expires_at,
            "user_token_days_remaining": round(
                user_token_days_remaining,
                2,
            ),
            "message": (
                "Facebook user token is approaching expiry."
            ),
        }

    return {
        "status": "healthy",
        "page_token_expires_at": (
            page_expiry.isoformat()
            if page_token_expires_at
            else None
        ),
        "page_token_days_remaining": (
            round(page_token_days_remaining, 2)
            if page_token_days_remaining is not None
            else None
        ),
        "user_token_expires_at": user_token_expires_at,
        "user_token_days_remaining": (
            round(user_token_days_remaining, 2)
            if user_token_days_remaining is not None
            else None
        ),
        "message": (
            "Facebook Page access token is valid."
        ),
    }

def ensure_facebook_token_valid():
    """
    Ensure the Facebook Page access token is valid.

    If the Page token is invalid, automatically attempt to
    refresh the underlying Facebook user token and obtain
    a fresh Page access token.
    """

    print("\n" + "=" * 50)
    print("FACEBOOK TOKEN CHECK")
    print("=" * 50)

    # --------------------------------------------------
    # Step 1: Check current Page token
    # --------------------------------------------------
    status = get_facebook_token_status()

    FORCE_REFRESH_TEST = False

    if status["status"] == "healthy" and not FORCE_REFRESH_TEST:
        print("✅ Facebook Page access token is healthy.")
        return get_current_access_token()

    # --------------------------------------------------
    # Step 2: Token is invalid/expired → refresh
    # --------------------------------------------------

    if FORCE_REFRESH_TEST or status["status"] in ("invalid", "expired"):
        print(
            "⚠️ Facebook Page access token is invalid."
        )
        print(
            "🔄 Attempting automatic Facebook token refresh..."
        )

        refresh_result = refresh_facebook_user_token()

        if refresh_result.get("status") != "success":
            print(
                "❌ Automatic Facebook token refresh failed."
            )

            raise RuntimeError(
                "Facebook token refresh failed. "
                "Re-authentication is required."
            )

        # --------------------------------------------------
        # Step 3: Validate the newly obtained Page token
        # --------------------------------------------------

        new_status = get_facebook_token_status()

        if new_status["status"] != "healthy":
            raise RuntimeError(
                "Facebook token refresh completed, "
                "but the new Page access token could not "
                "be validated."
            )

        print(
            "✅ Facebook token automatically refreshed."
        )

        return get_current_access_token()

    # --------------------------------------------------
    # Step 4: Other states
    # --------------------------------------------------

    if status["status"] == "critical":
        print(
            "⚠️ Facebook token is approaching expiry."
        )

    elif status["status"] == "approaching":
        print(
            "⚠️ Facebook token is approaching expiry."
        )

    return get_current_access_token()


def get_me():

    response = requests.get(
        "https://graph.facebook.com/v25.0/me",
        params={
            "fields": "id,name",
            "access_token": ensure_facebook_token_valid(),
        },
    )

    return response.json()

def get_pages():

    response = requests.get(
        "https://graph.facebook.com/v25.0/me/accounts",
        params={
            "access_token": ensure_facebook_token_valid(),
        },
    )

    return response.json()

def get_page():

    response = requests.get(
        f"{GRAPH_BASE_URL}/{get_current_page_id()}",
        params={
            "fields": "id,name",
            "access_token": ensure_facebook_token_valid(),
        },
    )

    return response.json()

def create_post(message: str):

    response = requests.post(
        f"{GRAPH_BASE_URL}/{get_current_page_id()}/feed",
        data={
            "message": message,
            "access_token": ensure_facebook_token_valid(),
        },
    )

    return response.json()


def get_posts():

    response = requests.get(
        f"{GRAPH_BASE_URL}/{get_current_page_id()}/posts",
        params={
            "fields": "id,message,created_time",
            "access_token": ensure_facebook_token_valid(),
        },
    )

    return response.json()

def get_comments(post_id: str):

    response = requests.get(
        f"{GRAPH_BASE_URL}/{post_id}/comments",
        params={
            "fields": "id,message,from,created_time",
            "access_token": ensure_facebook_token_valid(),
        },
    )

    return response.json()

def reply_to_comment(comment_id: str, message: str):

    response = requests.post(
        f"{GRAPH_BASE_URL}/{comment_id}/comments",
        data={
            "message": message,
            "access_token": ensure_facebook_token_valid(),
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
            "access_token": ensure_facebook_token_valid(),
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