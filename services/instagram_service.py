import requests, os
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
from services.config import (
    INSTAGRAM_APP_ID,
    INSTAGRAM_APP_SECRET,
    INSTAGRAM_REDIRECT_URI,
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_USER_ID,
    INSTAGRAM_GRAPH_BASE_URL,
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

    # ==================================================
    # Step 1 — Exchange authorization code
    # for short-lived access token
    # ==================================================

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

    print("\n========== INSTAGRAM SHORT TOKEN ==========")
    print("Status:", response.status_code)
    print("Body:", response.text)
    print("===========================================\n")

    response.raise_for_status()

    short_data = response.json()

    if "access_token" not in short_data:
        raise Exception(
            f"Instagram did not return an access token: {short_data}"
        )

    short_token = short_data["access_token"]

    # ==================================================
    # Step 2 — Exchange short-lived token
    # for long-lived token
    # ==================================================

    long_response = requests.get(
        f"{INSTAGRAM_GRAPH_BASE_URL}/access_token",
        params={
            "grant_type": "ig_exchange_token",
            "client_secret": INSTAGRAM_APP_SECRET,
            "access_token": short_token,
        },
    )

    print("\n========== INSTAGRAM LONG TOKEN ==========")
    print("Status:", long_response.status_code)
    print("Body:", long_response.text)
    print("==========================================\n")

    long_response.raise_for_status()

    long_data = long_response.json()

    if "access_token" not in long_data:
        raise Exception(
            f"Instagram did not return a long-lived token: {long_data}"
        )

    long_token = long_data["access_token"]

    expires_in = long_data.get("expires_in")

    expires_at = None

    if expires_in:
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=expires_in)
        ).isoformat()

    # ==================================================
    # Step 3 — Save long-lived token
    # ==================================================

    update_env(
    "INSTAGRAM_ACCESS_TOKEN",
    long_token,
    )

    if expires_at:
        update_env(
            "INSTAGRAM_ACCESS_TOKEN_EXPIRES_AT",
            expires_at,
        )

    print(
        "✅ Long-lived Instagram access token saved to .env"
    )

    # ==================================================
    # Return useful metadata
    # ==================================================

    return {
        "access_token": long_token,
        "token_type": long_data.get("token_type"),
        "expires_in": expires_in,
        "expires_at": expires_at,
        "user_id": long_data.get(
            "user_id",
            short_data.get("user_id"),
        ),
    }

def ensure_instagram_token_valid():

    expires_at = os.getenv(
        "INSTAGRAM_ACCESS_TOKEN_EXPIRES_AT"
    )

    if not expires_at:
        print(
            "⚠️ Instagram token expiry unknown. "
            "Re-authentication may be required."
        )
        return os.getenv("INSTAGRAM_ACCESS_TOKEN")

    expiry = datetime.fromisoformat(expires_at)

    now = datetime.now(timezone.utc)

    remaining = expiry - now

    print(
        f"Instagram token remaining: "
        f"{remaining}"
    )

    # Refresh if less than 7 days remain
    if remaining <= timedelta(days=7):

        print(
            "⚠️ Instagram token approaching expiry. "
            "Refreshing..."
        )

        result = refresh_instagram_access_token()

        return result["access_token"]

    return os.getenv("INSTAGRAM_ACCESS_TOKEN")


def refresh_instagram_access_token():

    current_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not current_token:
        raise Exception(
            "No Instagram access token configured."
        )

    print("\n========== INSTAGRAM TOKEN REFRESH ==========")

    response = requests.get(
        f"{INSTAGRAM_GRAPH_BASE_URL}/refresh_access_token",
        params={
            "grant_type": "ig_refresh_token",
            "access_token": current_token,
        },
    )

    print("Status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    if "access_token" not in data:
        raise Exception(
            f"Instagram refresh did not return a token: {data}"
        )

    new_token = data["access_token"]
    expires_in = data.get("expires_in")

    expires_at = None

    if expires_in:
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=expires_in)
        ).isoformat()

    # Save the new token
    update_env(
        "INSTAGRAM_ACCESS_TOKEN",
        new_token,
    )

    # Save new expiration
    if expires_at:
        update_env(
            "INSTAGRAM_ACCESS_TOKEN_EXPIRES_AT",
            expires_at,
        )

    print("✅ Instagram access token refreshed")
    print("Expires at:", expires_at)
    print("============================================\n")

    return {
        "access_token": new_token,
        "expires_in": expires_in,
        "expires_at": expires_at,
    }

# ==================================================
# Get Instagram account
# ==================================================

def get_account():

    response = requests.get(
        f"{INSTAGRAM_GRAPH_BASE_URL}/me",
        params={
            "fields": "user_id,username,name,account_type",
            "access_token": ensure_instagram_token_valid(),
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
    max_length = 1000

    messages = [
        message[i:i + max_length]
        for i in range(0, len(message), max_length)
    ]

    results = []

    for msg in messages:
        url = f"{INSTAGRAM_GRAPH_BASE_URL}/{INSTAGRAM_USER_ID}/messages"

        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": msg
            }
        }

        response = requests.post(
            url,
            json=payload,
            params={
                "access_token": ensure_instagram_token_valid()
            },
        )

        print("\n========== INSTAGRAM SEND MESSAGE ==========")
        print("Recipient ID:", recipient_id)
        print("Message length:", len(msg))
        print("Status:", response.status_code)
        print("Response:", response.text)
        print("============================================\n")

        results.append(response.json())

    return results