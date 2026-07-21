
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# -----------------------------
# Meta App Credentials
# -----------------------------
META_APP_ID = os.getenv("META_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")

# -----------------------------
# OAuth / Tokens
# -----------------------------
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# -----------------------------
# Current Test Facebook Page
# -----------------------------
PAGE_ID = os.getenv("PAGE_ID")

# -----------------------------
# URLs
# -----------------------------
BASE_URL = os.getenv("BASE_URL")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# -----------------------------
# Graph API
# -----------------------------
GRAPH_API_VERSION = os.getenv(
    "GRAPH_API_VERSION",
    "v25.0",
)
GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"