import json
import os
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from config import (
    FIREBASE_DATABASE_URL,
    FIREBASE_SERVICE_ACCOUNT,
)


# ======================================
# FIREBASE INITIALIZATION
# ======================================

def _initialize_firebase():

    if firebase_admin._apps:
        return

    if not FIREBASE_DATABASE_URL:
        raise RuntimeError(
            "FIREBASE_DATABASE_URL is not configured."
        )

    service_account_path = (
        FIREBASE_SERVICE_ACCOUNT
    )

    if not os.path.exists(
        service_account_path
    ):

        raise FileNotFoundError(
            "Firebase service account file not found: "
            f"{service_account_path}"
        )

    credential = credentials.Certificate(
        service_account_path
    )

    firebase_admin.initialize_app(
        credential,
        {
            "databaseURL": FIREBASE_DATABASE_URL,
        },
    )


_initialize_firebase()


# ======================================
# HELPERS
# ======================================

def _ref(path: str):

    return db.reference(path)


# ======================================
# FILES
# ======================================

def save_file(
    code: str,
    message_ids: List[int],
    unlock_channel_id: Optional[int] = None,
    unlock_join_link: Optional[str] = None,
    post_type: str = "normal",
):

    data = {
        "message_ids": message_ids,
        "post_type": post_type,
    }

    if unlock_channel_id is not None:

        data[
            "unlock_channel_id"
        ] = unlock_channel_id

    if unlock_join_link:

        data[
            "unlock_join_link"
        ] = unlock_join_link

    _ref(
        f"files/{code}"
    ).set(data)


def get_file(
    code: str,
) -> Optional[List[int]]:

    data = _ref(
        f"files/{code}"
    ).get()

    if not data:
        return None

    if isinstance(data, list):
        return data

    return data.get(
        "message_ids"
    )


def get_post_type(
    code: str,
) -> Optional[str]:

    data = _ref(
        f"files/{code}"
    ).get()

    if not data:
        return None

    if isinstance(data, dict):

        return data.get(
            "post_type"
        )

    return None


def get_unlock_channel_id(
    code: str,
) -> Optional[int]:

    data = _ref(
        f"files/{code}"
    ).get()

    if not data:
        return None

    return data.get(
        "unlock_channel_id"
    )


def get_unlock_join_link(
    code: str,
) -> Optional[str]:

    data = _ref(
        f"files/{code}"
    ).get()

    if not data:
        return None

    return data.get(
        "unlock_join_link"
    )


# ======================================
# VIP
# ======================================

def add_vip(
    user_id: int,
):

    _ref(
        f"vip_users/{user_id}"
    ).set(
        {
            "user_id": user_id,
        }
    )


def remove_vip(
    user_id: int,
):

    _ref(
        f"vip_users/{user_id}"
    ).delete()


def is_vip(
    user_id: int,
) -> bool:

    result = _ref(
        f"vip_users/{user_id}"
    ).get()

    return result is not None


def get_vip_list() -> List[int]:

    data = _ref(
        "vip_users"
    ).get()

    if not data:
        return []

    users = []

    for key in data.keys():

        try:
            users.append(
                int(key)
            )

        except (
            ValueError,
            TypeError,
        ):
            continue

    return sorted(users)


# ======================================
# SCHEDULES
# ======================================

def save_schedule(
    schedule_id: str,
    data: Dict[str, Any],
):

    _ref(
        f"schedules/{schedule_id}"
    ).set(data)


def get_schedules() -> Dict[str, Any]:

    data = _ref(
        "schedules"
    ).get()

    if not data:
        return {}

    return data


def delete_schedule(
    schedule_id: str,
):

    _ref(
        f"schedules/{schedule_id}"
    ).delete()


# ======================================
# OPTIONAL FILE DELETE
# ======================================

def delete_file(
    code: str,
):

    _ref(
        f"files/{code}"
    ).delete()


# ======================================
# OPTIONAL DATABASE EXPORT
# ======================================

def export_database() -> Dict[str, Any]:

    data = _ref("").get()

    if not data:
        return {}

    return data
