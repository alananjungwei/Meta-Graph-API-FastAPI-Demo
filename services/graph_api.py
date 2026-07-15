import os

from dotenv import load_dotenv

load_dotenv()


def get_app_info():
    """
    Returns basic information about the application.
    """

    app_id = os.getenv("META_APP_ID")

    return {
        "app_id": app_id,
        "status": "Environment loaded successfully!",
        "message": "Ready to connect to Meta Graph API 🚀"
    }