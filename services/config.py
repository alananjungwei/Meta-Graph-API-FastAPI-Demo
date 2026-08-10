
import os
from dotenv import load_dotenv

load_dotenv()

# ==================================================
# Facebook
# ==================================================

META_APP_ID = os.getenv("META_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI")
CONFIG_ID = os.getenv("CONFIG_ID")

# ==================================================
# Instagram
# ==================================================

INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET")

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")

INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI")


# ==================================================
# Webhooks
# ==================================================

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# ==================================================
# OpenAI
# ==================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ==================================================
# Graph API
# ==================================================

GRAPH_API_VERSION = os.getenv(
    "GRAPH_API_VERSION",
    "v25.0",
)

GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# ==================================================
# Instagram Login/API
# ==================================================

INSTAGRAM_GRAPH_BASE_URL = f"https://graph.instagram.com/{GRAPH_API_VERSION}"