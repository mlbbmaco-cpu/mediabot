import os

from dotenv import load_dotenv


# ======================================
# LOAD ENVIRONMENT VARIABLES
# ======================================

load_dotenv()


# ======================================
# HELPER
# ======================================

def get_env(name, default=""):
    """
    Get an environment variable safely.
    Removes leading/trailing whitespace.
    """
    return os.getenv(
        name,
        default,
    ).strip()


def get_int_env(name, default=0):
    """
    Get an integer environment variable safely.
    """
    value = get_env(
        name,
        str(default),
    )

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"{name} must be a number. "
            f"Current value: {value!r}"
        )


# ======================================
# TELEGRAM
# ======================================

TOKEN = get_env(
    "BOT_TOKEN"
)

if not TOKEN:
    raise ValueError(
        "BOT_TOKEN is not configured."
    )


OWNER_ID = get_int_env(
    "OWNER_ID"
)


# ======================================
# TELEGRAM STORAGE CHANNELS
# ======================================

# Existing private/admin storage channel
CHANNEL_ID = get_int_env(
    "CHANNEL_ID"
)


# Public /start send storage channel
UPLOAD_CHANNEL_ID = get_int_env(
    "UPLOAD_CHANNEL_ID",
    -1003918597694,
)


# Channel where posts are published
POST_CHANNEL_ID = get_int_env(
    "POST_CHANNEL_ID",
    -1004401856873,
)


# ======================================
# BOT
# ======================================

BOT_USERNAME = get_env(
    "BOT_USERNAME",
    "walawwa_downloadBot",
).lstrip("@")


# ======================================
# FIREBASE DATABASE
# ======================================

FIREBASE_DATABASE_URL = get_env(
    "FIREBASE_DATABASE_URL"
)


if not FIREBASE_DATABASE_URL:
    raise ValueError(
        "FIREBASE_DATABASE_URL is not configured."
    )


# ======================================
# FIREBASE SERVICE ACCOUNT
# ======================================

# Path to the Firebase service-account
# JSON file mounted by Northflank.
#
# Example:
#
# /app/secrets/firebase-service-account.json
#
# Do NOT put the JSON contents here.

FIREBASE_SERVICE_ACCOUNT = get_env(
    "FIREBASE_SERVICE_ACCOUNT",
    "firebase-service-account.json",
)


# ======================================
# WEB
# ======================================

WEB_URL = get_env(
    "WEB_URL",
    "https://walwwa.web.app",
).rstrip("/")


# ======================================
# TIMEZONE
# ======================================

SCHEDULE_TIMEZONE = get_env(
    "SCHEDULE_TIMEZONE",
    "Asia/Colombo",
)


# ======================================
# CONTENT / POST EXPIRY
# ======================================

# Files sent to users expire after 48 hours.
CONTENT_DELETE_AFTER_HOURS = get_int_env(
    "CONTENT_DELETE_AFTER_HOURS",
    48,
)


# Public channel posts expire after 48 hours.
POST_DELETE_AFTER_HOURS = get_int_env(
    "POST_DELETE_AFTER_HOURS",
    48,
)


# Convert hours to seconds for asyncio.sleep()
CONTENT_DELETE_AFTER_SECONDS = (
    CONTENT_DELETE_AFTER_HOURS * 60 * 60
)

POST_DELETE_AFTER_SECONDS = (
    POST_DELETE_AFTER_HOURS * 60 * 60
)


# Caption automatically added to every post.
POST_EXPIRY_TEXT = (
    '" පැය 48 කින් පසු වීඩියෝ ඩිලීට් වනු ඇත "'
)


# ======================================
# VIP
# ======================================

VIP_ENABLED = (
    get_env(
        "VIP_ENABLED",
        "false",
    ).lower()
    == "true"
)


VIP_TAG = get_env(
    "VIP_TAG",
    "💎 VIP CONTENT",
)


# ======================================
# STARTUP CONFIG CHECK
# ======================================

print(
    "================================"
)

print(
    "CONFIG LOADED"
)

print(
    f"BOT_USERNAME: @{BOT_USERNAME}"
)

print(
    f"OWNER_ID: {OWNER_ID}"
)

print(
    f"CHANNEL_ID: {CHANNEL_ID}"
)

print(
    f"UPLOAD_CHANNEL_ID: "
    f"{UPLOAD_CHANNEL_ID}"
)

print(
    f"POST_CHANNEL_ID: "
    f"{POST_CHANNEL_ID}"
)

print(
    f"WEB_URL: {WEB_URL}"
)

print(
    f"FIREBASE_DATABASE_URL: "
    f"{FIREBASE_DATABASE_URL}"
)

print(
    f"FIREBASE_SERVICE_ACCOUNT: "
    f"{FIREBASE_SERVICE_ACCOUNT}"
)

print(
    f"SCHEDULE_TIMEZONE: "
    f"{SCHEDULE_TIMEZONE}"
)

print(
    f"CONTENT_DELETE_AFTER_HOURS: "
    f"{CONTENT_DELETE_AFTER_HOURS}"
)

print(
    f"POST_DELETE_AFTER_HOURS: "
    f"{POST_DELETE_AFTER_HOURS}"
)

print(
    f"VIP_ENABLED: "
    f"{VIP_ENABLED}"
)

print(
    "BOT_TOKEN: configured"
)

print(
    "================================"
)
