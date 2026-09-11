import os

from dotenv import load_dotenv


# ======================================
# LOAD ENVIRONMENT VARIABLES
# ======================================

load_dotenv()


# ======================================
# TELEGRAM
# ======================================

TOKEN = os.getenv("BOT_TOKEN", "").strip()

OWNER_ID = int(
    os.getenv("OWNER_ID", "0")
)


# ======================================
# TELEGRAM STORAGE CHANNELS
# ======================================

# Existing private/admin storage channel
CHANNEL_ID = int(
    os.getenv("CHANNEL_ID", "0")
)


# New public /start send storage channel
UPLOAD_CHANNEL_ID = int(
    os.getenv(
        "UPLOAD_CHANNEL_ID",
        "-1003918597694",
    )
)


# New channel where posts are published
POST_CHANNEL_ID = int(
    os.getenv(
        "POST_CHANNEL_ID",
        "-1004401856873",
    )
)


# ======================================
# BOT
# ======================================

BOT_USERNAME = os.getenv(
    "BOT_USERNAME",
    "walawwa_downloadBot",
).strip().lstrip("@")


# ======================================
# FIREBASE / WEB
# ======================================

# Example after Firebase Hosting setup:
#
# https://your-project-id.web.app
#
# Do NOT put a trailing slash.

WEB_URL = os.getenv(
    "WEB_URL",
    "https://YOUR-PROJECT-ID.web.app",
).strip().rstrip("/")


# ======================================
# FIREBASE
# ======================================

FIREBASE_DATABASE_URL = os.getenv(
    "FIREBASE_DATABASE_URL",
    "",
).strip()


FIREBASE_SERVICE_ACCOUNT = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT",
    "firebase-service-account.json",
).strip()


# ======================================
# SCHEDULER
# ======================================

SCHEDULE_TIMEZONE = os.getenv(
    "SCHEDULE_TIMEZONE",
    "Asia/Colombo",
).strip()
