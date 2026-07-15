import os
from dotenv import load_dotenv

load_dotenv()

META_APP_ID = os.getenv("META_APP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

BASE_URL = os.getenv("BASE_URL")
REDIRECT_URI = os.getenv("REDIRECT_URI")

GRAPH_API_VERSION = "v25.0"

GRAPH_BASE_URL = (
    f"https://graph.facebook.com/{GRAPH_API_VERSION}"
)