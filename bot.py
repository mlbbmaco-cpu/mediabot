import asyncio
import secrets
import telegram

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from types import SimpleNamespace

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import (
    TOKEN,
    OWNER_ID,
    CHANNEL_ID,
    UPLOAD_CHANNEL_ID,
    BOT_USERNAME,
    WEB_URL,
)

from firebase import (
    save_file,
    get_file,
    get_unlock_channel_id,
    get_unlock_join_link,
    get_post_type,
    add_vip,
    remove_vip,
    is_vip,
    get_vip_list,
    save_schedule,
    get_schedules,
    delete_schedule,
    save_expiry_job,
    get_expiry_jobs,
    delete_expiry_job,
    delete_file,
)


print(
    "BOT VERSION 15 - VIP DISABLED "
    "+ UNIVERSAL PUBLIC SEND "
    "+ SUB2UNLOCK + PERSISTENT SCHEDULER"
)


# ======================================
# CONFIG
# ======================================

POST_CHANNEL_ID = -1004401856873

VIP_TAG = "💎 VIP CONTENT"

WATCH_BUTTON_TEXT = "🎬 Watch Free ▶️"
VIP_BUTTON_TEXT = "👑 VIP Access"

# ======================================
# CONTENT EXPIRATION
# ======================================

# Both downloaded copies sent to users and public channel posts
# expire after 48 hours.
CONTENT_DELETE_AFTER_SECONDS = 48 * 60 * 60
POST_DELETE_AFTER_SECONDS = 48 * 60 * 60

POST_EXPIRY_TEXT = "\" පැය 48 කින් පසු වීඩියෝ ඩිලීට් වනු ඇත \""

STOP_UPLOAD_BUTTON_TEXT = "🛑 Stop Uploading"

SCHEDULE_TIMEZONE = ZoneInfo("Asia/Colombo")


# ======================================
# FEATURE SWITCHES
# ======================================

# VIP is temporarily disabled/hidden.
#
# IMPORTANT:
# All VIP functions/code remain in this file.
#
# Change to True later when you want VIP
# functionality back.
VIP_ENABLED = False


# ======================================
# PUBLIC SEND
# ======================================

PUBLIC_SEND_STORAGE_CHANNEL_ID = UPLOAD_CHANNEL_ID

# Silent internal batching timer.
# User is NOT told about this timer.
PUBLIC_SEND_WAIT_SECONDS = 20


# ======================================
# STORAGE
# ======================================

upload_batches = {}

owner_mode = None

admin_post_data = {}


# ======================================
# SUB2UNLOCK
# ======================================

sub2unlock_channel = None
sub2unlock_channel_id = None
sub2unlock_join_link = None
sub2unlock_waiting_for_id = False


# ======================================
# PUBLIC SEND STORAGE
# ======================================

public_send_batches = {}
public_send_tasks = {}


# ======================================
# SCHEDULER
# ======================================

scheduled_tasks = set()
expiry_tasks = set()


# ======================================
# SAFE COPY WITH RETRY
# ======================================

async def copy_message_with_retry(
    bot,
    *,
    chat_id,
    from_chat_id,
    message_id,
    protect_content=False,
    label="file",
    caption=None,
):

    while True:

        try:

            kwargs = {
                "chat_id": chat_id,
                "from_chat_id": from_chat_id,
                "message_id": message_id,
                "protect_content": protect_content,
            }

            if caption is not None:
                kwargs["caption"] = caption

            return await bot.copy_message(
                **kwargs
            )

        except telegram.error.RetryAfter as e:

            wait = int(
                getattr(
                    e,
                    "retry_after",
                    1,
                )
            ) + 1

            print(
                f"⚠️ Flood wait {wait}s "
                f"while copying {label}"
            )

            await asyncio.sleep(wait)

        except telegram.error.TimedOut:

            print(
                f"⚠️ Telegram timeout while copying "
                f"{label}. Retrying..."
            )

            await asyncio.sleep(5)

        except Exception as e:

            print(
                f"❌ Copy error {label}: {e}"
            )

            raise


# ======================================
# ADMIN MENU
#
# VIP BUTTON IS HIDDEN WHEN DISABLED.
# ======================================

def get_admin_menu():

    buttons = []

    # ==================================
    # VIP
    # ==================================

    if VIP_ENABLED:

        buttons.append(
            [
                InlineKeyboardButton(
                    "🟣 VIP Post",
                    callback_data="mode:vip",
                )
            ]
        )

    # ==================================
    # NORMAL
    # ==================================

    buttons.append(
        [
            InlineKeyboardButton(
                "🔵 Normal Post",
                callback_data="mode:normal",
            )
        ]
    )

    # ==================================
    # SUB2UNLOCK
    # ==================================

    buttons.append(
        [
            InlineKeyboardButton(
                "🟢 Sub2Unlock",
                callback_data="mode:sub2unlock",
            )
        ]
    )

    return InlineKeyboardMarkup(
        buttons
    )


# ======================================
# ADMIN STOP BUTTON
# ======================================

def get_upload_stop_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    STOP_UPLOAD_BUTTON_TEXT,
                    callback_data="upload:stop",
                )
            ]
        ]
    )


# ======================================
# SHOW ADMIN MENU
# ======================================

async def show_admin_menu(
    chat_id,
    context,
    text="📂 Select Post Type",
):

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=get_admin_menu(),
    )


# ======================================
# RESET ADMIN STATE
# ======================================

def reset_admin_state(user_id):

    global owner_mode
    global sub2unlock_channel
    global sub2unlock_channel_id
    global sub2unlock_join_link
    global sub2unlock_waiting_for_id

    owner_mode = None

    admin_post_data.pop(
        user_id,
        None,
    )

    upload_batches.pop(
        user_id,
        None,
    )

    sub2unlock_channel = None
    sub2unlock_channel_id = None
    sub2unlock_join_link = None
    sub2unlock_waiting_for_id = False


# ======================================
# WEB LINK
# ======================================

def make_web_link(code):

    return (
        WEB_URL.rstrip("/")
        + f"/?start={code}"
    )


# ======================================
# VIP
#
# TEMPORARILY DISABLED
#
# FUNCTIONS ARE KEPT.
# ======================================

async def vip_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    # VIP disabled.
    if not VIP_ENABLED:
        return

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:

        await update.message.reply_text(
            "Usage:\n/vip USER_ID"
        )

        return

    try:

        user_id = int(
            context.args[0]
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Invalid ID"
        )

        return

    add_vip(user_id)

    await update.message.reply_text(
        f"💎 VIP Added\n\n🆔 {user_id}"
    )


# ======================================
# REMOVE VIP
#
# TEMPORARILY DISABLED
#
# FUNCTION IS KEPT.
# ======================================

async def removevip_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not VIP_ENABLED:
        return

    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:

        await update.message.reply_text(
            "Usage:\n/removevip USER_ID"
        )

        return

    try:

        user_id = int(
            context.args[0]
        )

    except ValueError:

        await update.message.reply_text(
            "❌ Invalid ID"
        )

        return

    remove_vip(user_id)

    await update.message.reply_text(
        f"❌ VIP Removed\n\n🆔 {user_id}"
    )


# ======================================
# VIP LIST
#
# TEMPORARILY DISABLED
#
# FUNCTION IS KEPT.
# ======================================

async def viplist_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not VIP_ENABLED:
        return

    if update.effective_user.id != OWNER_ID:
        return

    users = get_vip_list()

    if not users:

        await update.message.reply_text(
            "💎 No VIP users"
        )

        return

    await update.message.reply_text(
        "💎 VIP USERS\n\n"
        + "\n".join(
            str(x)
            for x in users
        )
    )


# ======================================
# PERSISTENT EXPIRY JOBS
# ======================================

async def save_expiry_task(
    application,
    *,
    job_id,
    job_type,
    chat_id,
    message_id,
    expires_at,
    code=None,
):

    data = {
        "type": job_type,
        "chat_id": int(chat_id),
        "message_id": int(message_id),
        "expires_at": float(expires_at),
    }

    if code:
        data["code"] = str(code)

    save_expiry_job(
        job_id,
        data,
    )

    task = application.create_task(
        run_expiry_job(
            application,
            job_id,
            data,
        )
    )

    expiry_tasks.add(task)

    return task


async def run_expiry_job(
    application,
    job_id,
    data,
):

    task = asyncio.current_task()

    try:

        expires_at = float(
            data.get("expires_at", 0)
        )

        while True:

            remaining = (
                expires_at
                - datetime.now(timezone.utc).timestamp()
            )

            if remaining <= 0:
                break

            await asyncio.sleep(
                min(remaining, 60)
            )

        chat_id = int(data["chat_id"])
        message_id = int(data["message_id"])
        job_type = data.get("type", "unknown")

        print(
            f"⏰ Expiry reached: {job_id} "
            f"({job_type})"
        )

        try:

            await application.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )

            print(
                f"🗑 Telegram message deleted: "
                f"{chat_id}/{message_id}"
            )

        except telegram.error.BadRequest as e:

            # Already deleted / inaccessible messages should not
            # keep the Firebase job forever.
            print(
                f"⚠️ Telegram message already unavailable: "
                f"{chat_id}/{message_id}: {e}"
            )

        except Exception as e:

            print(
                f"⚠️ Telegram deletion failed for "
                f"{chat_id}/{message_id}: {e}"
            )

        # The channel-post expiry is the lifetime of the
        # download code. Removing the Firebase file here makes
        # the public link expire permanently.
        if job_type == "channel_post":

            code = data.get("code")

            if code:

                try:

                    delete_file(code)

                    print(
                        f"🗑 Firebase download code deleted: "
                        f"{code}"
                    )

                except Exception as e:

                    print(
                        f"⚠️ Firebase code deletion failed "
                        f"for {code}: {e}"
                    )

        try:

            delete_expiry_job(
                job_id
            )

            print(
                f"🗑 Firebase expiry job deleted: "
                f"{job_id}"
            )

        except Exception as e:

            print(
                f"⚠️ Could not delete expiry job "
                f"{job_id}: {e}"
            )

    except asyncio.CancelledError:

        print(
            f"⚠️ Expiry task cancelled: {job_id}"
        )

        raise

    except Exception as e:

        print(
            f"❌ Expiry task failed {job_id}: {e}"
        )

    finally:

        if task:
            expiry_tasks.discard(task)


async def restore_expiry_jobs(
    application,
):

    print(
        "================================"
    )

    print(
        "🧹 RESTORING FIREBASE EXPIRY JOBS"
    )

    print(
        "================================"
    )

    try:

        jobs = get_expiry_jobs()

    except Exception as e:

        print(
            f"❌ Could not load expiry jobs: {e}"
        )

        return

    if not jobs:

        print(
            "ℹ️ No saved expiry jobs."
        )

        return

    restored = 0

    for job_id, data in jobs.items():

        try:

            if not isinstance(data, dict):
                continue

            if not data.get("chat_id"):
                continue

            if not data.get("message_id"):
                continue

            if not data.get("expires_at"):
                continue

            task = application.create_task(
                run_expiry_job(
                    application,
                    str(job_id),
                    dict(data),
                )
            )

            expiry_tasks.add(task)
            restored += 1

            print(
                f"✅ Restored expiry job {job_id}"
            )

        except Exception as e:

            print(
                f"❌ Failed restoring expiry job "
                f"{job_id}: {e}"
            )

    print(
        f"🧹 Restored {restored} expiry job(s)"
    )


# ======================================
# DOWNLOAD FILES
# ======================================

async def send_download_files(
    *,
    bot,
    chat_id,
    message_ids,
    application,
    delete_after_48h,
    protect_content=True,
    label="download",
    code=None,
):

    sent = []

    for i, msg_id in enumerate(
        message_ids,
        start=1,
    ):

        print(
            f"📤 Sending {label} "
            f"{i}/{len(message_ids)}"
        )

        try:

            copied = await copy_message_with_retry(
                bot,
                chat_id=chat_id,
                from_chat_id=CHANNEL_ID,
                message_id=msg_id,
                protect_content=protect_content,
                label=label,
            )

            sent.append(
                copied.message_id
            )

        except Exception as e:

            print(
                f"❌ Send error: {e}"
            )

    if delete_after_48h and sent:

        expires_at = (
            datetime.now(timezone.utc).timestamp()
            + CONTENT_DELETE_AFTER_SECONDS
        )

        for msg in sent:

            job_id = (
                f"user_download_"
                f"{chat_id}_"
                f"{msg}_"
                f"{secrets.token_hex(4)}"
            )

            try:

                await save_expiry_task(
                    application,
                    job_id=job_id,
                    job_type="user_download",
                    chat_id=chat_id,
                    message_id=msg,
                    expires_at=expires_at,
                    code=code,
                )

                print(
                    f"⏳ Persistent user deletion saved: "
                    f"{job_id}"
                )

            except Exception as e:

                print(
                    f"⚠️ Could not save user expiry job "
                    f"{job_id}: {e}"
                )


# ======================================
# PUBLIC SEND CHECK
#
# NOW ACCEPTS EVERYTHING.
#
# Text
# Links
# TXT
# PDF
# Video
# Image
# Audio
# Voice
# GIF
# Sticker
# Contact
# Location
# Poll
# Dice
# Etc.
# ======================================

def is_public_send_file(message):

    return message is not None


# ======================================
# PUBLIC USER DETAILS
# ======================================

def get_public_send_user_details(user):

    username = (
        f"@{user.username}"
        if user.username
        else "No username"
    )

    full_name = (
        user.full_name
        or "Unknown"
    )

    return (
        f"👤 User: {full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"🔗 Username: {username}"
    )


# ======================================
# PUBLIC MESSAGE TYPE
# ======================================

def is_text_only_message(message):

    return bool(
        message.text
        and not (
            message.document
            or message.photo
            or message.video
            or message.audio
            or message.voice
            or message.animation
            or message.sticker
            or message.contact
            or message.location
            or message.venue
            or message.poll
            or message.dice
            or message.video_note
            or message.game
        )
    )


# ======================================
# PUBLIC MESSAGE WITH CAPTION
#
# Telegram allows captions for media,
# but NOT normal text messages.
# ======================================

def can_have_caption(message):

    return bool(
        message.photo
        or message.video
        or message.document
        or message.audio
        or message.voice
        or message.animation
        or message.video_note
    )


# ======================================
# PUBLIC COPY WITH RETRY
#
# UNIVERSAL MESSAGE SUPPORT.
# ======================================

async def copy_public_send_file_with_retry(
    context,
    message,
    user_details,
):

    # ==================================
    # TEXT MESSAGE
    #
    # We cannot use copy_message with
    # caption for text.
    #
    # Therefore create a new text message
    # containing user details + original text.
    # ==================================

    if is_text_only_message(message):

        final_text = (
            f"{user_details}\n\n"
            f"📝 {message.text}"
        )

        while True:

            try:

                print(
                    f"📤 Public Text Send -> "
                    f"{PUBLIC_SEND_STORAGE_CHANNEL_ID}"
                )

                result = await context.bot.send_message(
                    chat_id=PUBLIC_SEND_STORAGE_CHANNEL_ID,
                    text=final_text,
                    disable_web_page_preview=False,
                )

                print(
                    f"✅ Public text stored: "
                    f"{result.message_id}"
                )

                return result

            except telegram.error.RetryAfter as e:

                wait = int(
                    getattr(
                        e,
                        "retry_after",
                        1,
                    )
                ) + 1

                print(
                    f"⚠️ Public text flood wait: "
                    f"{wait}s"
                )

                await asyncio.sleep(
                    wait
                )

            except telegram.error.TimedOut:

                print(
                    "⚠️ Public text timeout. "
                    "Retrying in 5 seconds..."
                )

                await asyncio.sleep(5)

            except Exception as e:

                print(
                    f"❌ Public text send error: {e}"
                )

                raise

    # ==================================
    # MEDIA WITH CAPTION
    # ==================================

    original_caption = (
        message.caption
        or ""
    ).strip()

    if original_caption:

        final_caption = (
            f"{user_details}\n\n"
            f"📝 {original_caption}"
        )

    else:

        final_caption = user_details

    # ==================================
    # COPY MEDIA / OTHER TELEGRAM TYPES
    # ==================================

    while True:

        try:

            print(
                f"📤 Public Send -> "
                f"{PUBLIC_SEND_STORAGE_CHANNEL_ID}"
            )

            kwargs = {
                "chat_id": (
                    PUBLIC_SEND_STORAGE_CHANNEL_ID
                ),
                "from_chat_id": message.chat.id,
                "message_id": message.message_id,
            }

            # Only caption-capable messages get
            # the user information as caption.
            #
            # For stickers, contacts, locations,
            # polls, dice, etc. Telegram may reject
            # a caption argument.
            if can_have_caption(message):

                kwargs["caption"] = final_caption

            result = await context.bot.copy_message(
                **kwargs
            )

            print(
                f"✅ Public message stored: "
                f"{result.message_id}"
            )

            # ==================================
            # NON-CAPTION MESSAGE TYPES
            #
            # Keep original message intact.
            # User details are stored separately
            # only when Telegram does not support
            # attaching them to the message.
            # ==================================

            if not can_have_caption(message):

                try:

                    await context.bot.send_message(
                        chat_id=(
                            PUBLIC_SEND_STORAGE_CHANNEL_ID
                        ),
                        text=user_details,
                    )

                except Exception as e:

                    print(
                        f"⚠️ Could not store "
                        f"user details: {e}"
                    )

            return result

        except telegram.error.RetryAfter as e:

            wait = int(
                getattr(
                    e,
                    "retry_after",
                    1,
                )
            ) + 1

            print(
                f"⚠️ Public Send flood wait: "
                f"{wait}s"
            )

            await asyncio.sleep(
                wait
            )

        except telegram.error.TimedOut:

            print(
                "⚠️ Public Send timeout. "
                "Retrying in 5 seconds..."
            )

            await asyncio.sleep(5)

        except Exception as e:

            print(
                f"❌ Public Send copy error: {e}"
            )

            raise


# ======================================
# PUBLIC SEND PROCESS BATCH
# ======================================

async def process_public_send_batch(
    user_id,
    context,
):

    batch = public_send_batches.pop(
        user_id,
        None,
    )

    public_send_tasks.pop(
        user_id,
        None,
    )

    if not batch:
        return

    user = batch["user"]

    messages = batch["messages"]

    user_details = get_public_send_user_details(
        user
    )

    print(
        "================================"
    )

    print(
        "📥 PUBLIC SEND BATCH"
    )

    print(
        f"User: {user.full_name}"
    )

    print(
        f"User ID: {user.id}"
    )

    print(
        f"Messages: {len(messages)}"
    )

    print(
        f"Storage: "
        f"{PUBLIC_SEND_STORAGE_CHANNEL_ID}"
    )

    print(
        "================================"
    )

    successful = 0

    for index, message in enumerate(
        messages,
        start=1,
    ):

        try:

            print(
                f"📦 Storing public message "
                f"{index}/{len(messages)}"
            )

            await copy_public_send_file_with_retry(
                context,
                message,
                user_details,
            )

            successful += 1

        except Exception as e:

            print(
                f"❌ Failed public message "
                f"{index}: {e}"
            )

    # ==================================
    # ONE FINAL USER MESSAGE
    # ==================================

    try:

        if successful:

            await context.bot.send_message(
                chat_id=user.id,
                text=(
                    f"✅ {successful} message"
                    f"{'s' if successful != 1 else ''} "
                    f"sent."
                ),
            )

        else:

            await context.bot.send_message(
                chat_id=user.id,
                text=(
                    "❌ Message send failed. "
                    "Please try again."
                ),
            )

    except Exception as e:

        print(
            f"⚠️ Public Send confirmation failed: "
            f"{e}"
        )


# ======================================
# PUBLIC SILENT WAIT
#
# 20 SECOND TIMER.
#
# EVERY NEW MESSAGE RESETS TIMER.
# ======================================

async def public_send_wait_task(
    user_id,
    context,
):

    try:

        await asyncio.sleep(
            PUBLIC_SEND_WAIT_SECONDS
        )

        await process_public_send_batch(
            user_id,
            context,
        )

    except asyncio.CancelledError:

        print(
            f"⏳ Public Send timer cancelled "
            f"for user {user_id}"
        )

        raise

    except Exception as e:

        print(
            f"❌ Public Send task error: {e}"
        )


# ======================================
# PUBLIC SEND RECEIVE MESSAGE
#
# OWNER IS NEVER HANDLED HERE.
#
# ANY MESSAGE IS ACCEPTED.
# ======================================

async def handle_public_send_file(
    update,
    context,
):

    if not update.message:
        return

    user = update.effective_user

    if not user:
        return

    # ==================================
    # ABSOLUTE OWNER BLOCK
    # ==================================

    if user.id == OWNER_ID:
        return

    message = update.message

    # ==================================
    # ACCEPT EVERYTHING
    # ==================================

    if not is_public_send_file(message):
        return

    # ==================================
    # CREATE USER BATCH
    # ==================================

    if user.id not in public_send_batches:

        public_send_batches[user.id] = {
            "user": user,
            "messages": [],
        }

    batch = public_send_batches[user.id]

    batch["messages"].append(
        message
    )

    count = len(
        batch["messages"]
    )

    print(
        f"📥 Public Send message received "
        f"from {user.id}: {count}"
    )

    # ==================================
    # RESET SILENT TIMER
    # ==================================

    old_task = public_send_tasks.get(
        user.id
    )

    if old_task:

        old_task.cancel()

    task = context.application.create_task(
        public_send_wait_task(
            user.id,
            context,
        )
    )

    public_send_tasks[user.id] = task

    # ==================================
    # SIMPLE ACK
    # ==================================

    try:

        await message.reply_text(
            "📥 Received."
        )

    except Exception as e:

        print(
            f"⚠️ Public acknowledgement failed: "
            f"{e}"
        )


# ======================================
# START
# ======================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    user_id = update.effective_user.id

    # ==================================
    # PUBLIC SEND
    # ==================================

    if (
        context.args
        and context.args[0].strip().lower() == "send"
    ):

        await update.message.reply_text(
            "📤 Send anything you want."
        )

        return

    # ==================================
    # VIP CONTACT
    #
    # DISABLED
    # ==================================

    if (
        context.args
        and context.args[0] == "contact"
    ):

        if not VIP_ENABLED:
            return

        await update.message.reply_text(
            "💎 VIP Membership\n\n"
            "Contact admin to buy VIP access."
        )

        return

    # ==================================
    # OWNER MENU
    # ==================================

    if (
        user_id == OWNER_ID
        and not context.args
    ):

        await update.message.reply_text(
            "📂 Select Post Type",
            reply_markup=get_admin_menu(),
        )

        return

    if not context.args:

        await update.message.reply_text(
            "👋 Open a valid link."
        )

        return

    code = context.args[0].strip()

    # ==================================
    # VIP DIRECT LINK
    #
    # VIP DISABLED.
    # ==================================

    if code.startswith("vip_"):

        if not VIP_ENABLED:

            await update.message.reply_text(
                "❌ VIP is temporarily unavailable."
            )

            return

        real_code = code.replace(
            "vip_",
            "",
            1,
        )

        message_ids = get_file(
            real_code
        )

        if not message_ids:

            await update.message.reply_text(
                "❌ Link expired."
            )

            return

        if is_vip(user_id):

            await send_download_files(
                bot=context.bot,
                chat_id=update.effective_chat.id,
                message_ids=message_ids,
                application=context.application,
                delete_after_48h=False,
                protect_content=False,
                label="vip",
                code=real_code,
            )

            return

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💎 Buy VIP",
                        url=(
                            "https://t.me/"
                            "TeNfLiXMedia_bot"
                            "?start=contact"
                        ),
                    )
                ]
            ]
        )

        await update.message.reply_text(
            "🔒 VIP Access Only\n\n"
            "💎 Buy VIP to unlock.",
            reply_markup=keyboard,
        )

        return

    # ==================================
    # NORMAL LINK
    # ==================================

    message_ids = get_file(
        code
    )

    if not message_ids:

        await update.message.reply_text(
            "❌ Link expired."
        )

        return

    post_type = get_post_type(
        code
    )

    if not post_type:

        post_type = "normal"

    # ==================================
    # VIP USER
    #
    # ONLY ACTIVE IF VIP ENABLED.
    # ==================================

    if VIP_ENABLED and is_vip(user_id):

        await send_download_files(
            bot=context.bot,
            chat_id=update.effective_chat.id,
            message_ids=message_ids,
            application=context.application,
            delete_after_48h=False,
            protect_content=False,
            label="vip user",
        )

        return

    # ==================================
    # VIP POST
    #
    # WHEN VIP IS DISABLED, OLD VIP POSTS
    # ARE TREATED AS NORMAL POSTS.
    # ==================================

    if (
        post_type == "vip"
        and VIP_ENABLED
    ):

        await update.message.reply_text(
            "🔒 VIP Content\n\n"
            "💎 Buy VIP to access."
        )

        return

    # ==================================
    # SUB2UNLOCK
    # ==================================

    if post_type == "sub2unlock":

        unlock_join_link = (
            get_unlock_join_link(code)
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔗 JOIN CHANNEL",
                        url=unlock_join_link,
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔓 UNLOCK VIDEO",
                        callback_data=(
                            f"unlock:{code}"
                        ),
                    ),
                ],
            ]
        )

        await update.message.reply_text(
            "🔒 This video is locked.\n\n"
            "1️⃣ Join channel\n"
            "2️⃣ Press unlock",
            reply_markup=keyboard,
        )

        return

    # ==================================
    # NORMAL DOWNLOAD
    # ==================================

    await send_download_files(
        bot=context.bot,
        chat_id=update.effective_chat.id,
        message_ids=message_ids,
        application=context.application,
        delete_after_48h=True,
        protect_content=True,
        label="normal",
    )


# ======================================
# UNLOCK
# ======================================

async def unlock_video(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    code = query.data.split(
        ":",
        1,
    )[1]

    user_id = query.from_user.id

    message_ids = get_file(
        code
    )

    if not message_ids:

        await query.edit_message_text(
            "❌ Link expired."
        )

        return

    # ==================================
    # VIP BYPASS
    #
    # ONLY WHEN VIP ENABLED.
    # ==================================

    if VIP_ENABLED and is_vip(user_id):

        await send_download_files(
            bot=context.bot,
            chat_id=query.message.chat.id,
            message_ids=message_ids,
            application=context.application,
            delete_after_48h=False,
            protect_content=False,
            label="vip unlock",
        )

        return

    channel_id = get_unlock_channel_id(
        code
    )

    join_link = get_unlock_join_link(
        code
    )

    try:

        member = await context.bot.get_chat_member(
            chat_id=channel_id,
            user_id=user_id,
        )

        if member.status in (
            "member",
            "administrator",
            "creator",
            "owner",
        ):

            await query.edit_message_text(
                "✅ Verified\n\n"
                "🎬 Sending files..."
            )

            await send_download_files(
                bot=context.bot,
                chat_id=query.message.chat.id,
                message_ids=message_ids,
                application=context.application,
                delete_after_48h=True,
                protect_content=True,
                label="unlock",
                code=code,
            )

            return

    except Exception as e:

        print(
            f"❌ Membership check error: {e}"
        )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔗 JOIN CHANNEL",
                    url=join_link,
                )
            ],
            [
                InlineKeyboardButton(
                    "🔓 UNLOCK",
                    callback_data=f"unlock:{code}",
                )
            ],
        ]
    )

    await query.edit_message_text(
        "🔒 Please join channel first.",
        reply_markup=keyboard,
    )


# ======================================
# CAPTION
# ======================================

def build_post_caption(data):

    caption = data.get(
        "caption",
        "",
    )

    # VIP tag only when VIP is enabled.
    if (
        data.get("post_type") == "vip"
        and VIP_ENABLED
    ):
        base_caption = (
            f"{VIP_TAG}\n\n"
            f"{caption}"
        )
    else:
        base_caption = caption

    # Automatically add the 48-hour expiry notice to EVERY post.
    if base_caption.strip():
        return (
            f"{base_caption.strip()}\n\n"
            f"{POST_EXPIRY_TEXT}"
        )

    return POST_EXPIRY_TEXT



# ======================================
# SEND POST TO CHANNEL
#
# VIP BUTTON HIDDEN WHEN DISABLED.
# ======================================

async def send_post_to_channel(
    data,
    context,
):

    caption = build_post_caption(
        data
    )

    code = data["code"]

    watch_link = data["link"]

    vip_link = (
        f"https://t.me/"
        f"{BOT_USERNAME}"
        f"?start=vip_{code}"
    )

    # ==================================
    # VIP POST
    # ==================================

    if (
        data["post_type"] == "vip"
        and VIP_ENABLED
    ):

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        VIP_BUTTON_TEXT,
                        url=vip_link,
                    )
                ]
            ]
        )

    # ==================================
    # NORMAL POST
    #
    # ONLY WATCH BUTTON.
    # VIP BUTTON IS REMOVED.
    # ==================================

    else:

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        WATCH_BUTTON_TEXT,
                        url=watch_link,
                    )
                ]
            ]
        )

    media_chat_id = data.get(
        "media_chat_id"
    )

    media_message_id = data.get(
        "media_message_id"
    )

    if not media_chat_id or not media_message_id:

        media = data.get(
            "media_message"
        )

        if not media:

            raise ValueError(
                "No media information available"
            )

        media_chat_id = media.chat.id

        media_message_id = media.message_id

    while True:

        try:

            print(
                "================================"
            )

            print(
                "📤 POSTING TO CHANNEL"
            )

            print(
                f"Channel: {POST_CHANNEL_ID}"
            )

            print(
                f"Source chat: {media_chat_id}"
            )

            print(
                f"Source message: {media_message_id}"
            )

            print(
                f"Code: {code}"
            )

            print(
                "================================"
            )

            result = await context.bot.copy_message(
                chat_id=POST_CHANNEL_ID,
                from_chat_id=media_chat_id,
                message_id=media_message_id,
                caption=caption,
                reply_markup=keyboard,
            )

            print(
                "✅ POST UPLOADED SUCCESSFULLY"
            )

            print(
                f"Telegram message ID: "
                f"{result.message_id}"
            )

            # Persist the public post's 48-hour expiry in Firebase.
            # This survives Northflank/container restarts.
            expires_at = (
                datetime.now(timezone.utc).timestamp()
                + POST_DELETE_AFTER_SECONDS
            )

            expiry_job_id = (
                f"channel_post_"
                f"{POST_CHANNEL_ID}_"
                f"{result.message_id}"
            )

            await save_expiry_task(
                context.application,
                job_id=expiry_job_id,
                job_type="channel_post",
                chat_id=POST_CHANNEL_ID,
                message_id=result.message_id,
                expires_at=expires_at,
                code=code,
            )

            # Save the published post details into the schedule record
            # before the scheduled record is removed. This gives Firebase
            # a complete record of what was actually published.
            schedule_id = data.get("schedule_id")

            if schedule_id:

                try:

                    published_data = dict(data)
                    published_data.pop("media_message", None)
                    published_data["status"] = "published"
                    published_data["published_message_id"] = result.message_id
                    published_data["published_chat_id"] = POST_CHANNEL_ID
                    published_data["published_at"] = datetime.now(timezone.utc).isoformat()
                    published_data["expires_at"] = datetime.fromtimestamp(
                        expires_at,
                        tz=timezone.utc,
                    ).isoformat()
                    published_data["expiry_job_id"] = expiry_job_id

                    save_schedule(
                        str(schedule_id),
                        published_data,
                    )

                    print(
                        f"💾 Published scheduled-post details saved: "
                        f"{schedule_id}"
                    )

                except Exception as e:

                    print(
                        f"⚠️ Could not update scheduled-post details: {e}"
                    )

            return result

        except telegram.error.RetryAfter as e:

            wait = int(
                getattr(
                    e,
                    "retry_after",
                    1,
                )
            ) + 1

            print(
                f"⚠️ Channel flood wait: "
                f"{wait}s"
            )

            await asyncio.sleep(wait)

        except telegram.error.TimedOut:

            print(
                "⚠️ Channel upload timeout. "
                "Retrying..."
            )

            await asyncio.sleep(5)

        except Exception as e:

            print(
                f"❌ CHANNEL POST FAILED: {e}"
            )

            raise


# ======================================
# SCHEDULED POST TASK
# ======================================

async def scheduled_post_task(
    data,
    context,
    target,
):

    task = asyncio.current_task()

    if task:
        scheduled_tasks.add(task)

    schedule_id = data.get(
        "schedule_id"
    )

    try:

        while True:

            now = datetime.now(
                SCHEDULE_TIMEZONE
            )

            delay = (
                target - now
            ).total_seconds()

            if delay <= 0:
                break

            print(
                f"⏳ Scheduled post waiting "
                f"{delay:.1f}s"
            )

            await asyncio.sleep(
                min(delay, 60)
            )

        print(
            "================================"
        )

        print(
            "⏰ SCHEDULE TIME REACHED"
        )

        print(
            f"Current: "
            f"{datetime.now(SCHEDULE_TIMEZONE)}"
        )

        print(
            f"Target: {target}"
        )

        print(
            "================================"
        )

        await send_post_to_channel(
            data,
            context,
        )

        print(
            "✅ SCHEDULED POST COMPLETED"
        )

        if schedule_id:

            try:

                delete_schedule(
                    schedule_id
                )

                print(
                    f"🗑 Schedule removed: "
                    f"{schedule_id}"
                )

            except Exception as e:

                print(
                    f"⚠️ Could not remove schedule: "
                    f"{e}"
                )

    except asyncio.CancelledError:

        print(
            "⚠️ Scheduled task cancelled"
        )

        raise

    except Exception as e:

        print(
            f"❌ SCHEDULED POST FAILED: {e}"
        )

    finally:

        if task:
            scheduled_tasks.discard(task)


# ======================================
# RESTORE SCHEDULES
# ======================================

async def restore_saved_schedules(
    application,
):

    print(
        "================================"
    )

    print(
        "📅 RESTORING SAVED SCHEDULES"
    )

    print(
        "================================"
    )

    try:

        schedules = get_schedules()

    except Exception as e:

        print(
            f"❌ Could not load schedules: {e}"
        )

        return

    if not schedules:

        print(
            "ℹ️ No saved schedules."
        )

        return

    restored = 0

    for schedule_id, saved_data in schedules.items():

        try:

            if not isinstance(
                saved_data,
                dict,
            ):

                continue

            target_string = saved_data.get(
                "target"
            )

            if not target_string:
                continue

            target = datetime.fromisoformat(
                target_string
            )

            if target.tzinfo is None:

                target = target.replace(
                    tzinfo=SCHEDULE_TIMEZONE
                )

            restored_data = dict(
                saved_data
            )

            restored_data[
                "schedule_id"
            ] = str(schedule_id)

            restore_context = SimpleNamespace(
                bot=application.bot,
                application=application,
            )

            task = application.create_task(
                scheduled_post_task(
                    restored_data,
                    restore_context,
                    target,
                )
            )

            scheduled_tasks.add(task)

            restored += 1

            print(
                f"✅ Restored schedule "
                f"{schedule_id}"
            )

        except Exception as e:

            print(
                f"❌ Failed restoring "
                f"{schedule_id}: {e}"
            )

    print(
        f"📅 Restored {restored} schedule(s)"
    )


# ======================================
# SCHEDULE TIME
# ======================================

async def handle_schedule_time(
    update,
    context,
):

    data = admin_post_data.get(
        OWNER_ID
    )

    if not data:
        return False

    if data.get(
        "step"
    ) != "schedule_time":

        return False

    text = update.message.text.strip()

    try:

        if ":" in text:

            hour_str, minute_str = (
                text.split(":", 1)
            )

            hour = int(hour_str)
            minute = int(minute_str)

        else:

            hour = int(text)
            minute = 0

    except (
        ValueError,
        TypeError,
    ):

        await update.message.reply_text(
            "❌ Invalid time.\n\n"
            "Examples:\n"
            "8\n"
            "8:10\n"
            "13:26\n"
            "23:45"
        )

        return True

    if hour < 0 or hour > 23:

        await update.message.reply_text(
            "❌ Hour must be between 0 and 23."
        )

        return True

    if minute < 0 or minute > 59:

        await update.message.reply_text(
            "❌ Minute must be between 0 and 59."
        )

        return True

    now = datetime.now(
        SCHEDULE_TIMEZONE
    )

    target = now.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0,
    )

    if target <= now:

        target += timedelta(days=1)

    media = data.get(
        "media_message"
    )

    if not media:

        await update.message.reply_text(
            "❌ Media information missing.\n"
            "Please create the post again."
        )

        return True

    data["media_chat_id"] = (
        media.chat.id
    )

    data["media_message_id"] = (
        media.message_id
    )

    schedule_id = (
        datetime.now(
            SCHEDULE_TIMEZONE
        ).strftime(
            "%Y%m%d%H%M%S"
        )
        + "_"
        + secrets.token_hex(3)
    )

    data["schedule_id"] = schedule_id

    scheduled_data = data.copy()

    scheduled_data.pop(
        "media_message",
        None,
    )

    firebase_schedule = scheduled_data.copy()

    firebase_schedule[
        "target"
    ] = target.isoformat()

    firebase_schedule[
        "created_at"
    ] = datetime.now(
        SCHEDULE_TIMEZONE
    ).isoformat()

    try:

        save_schedule(
            schedule_id,
            firebase_schedule,
        )

    except Exception as e:

        await update.message.reply_text(
            "❌ Could not save schedule.\n\n"
            f"Error: {e}"
        )

        return True

    task = context.application.create_task(
        scheduled_post_task(
            scheduled_data,
            context,
            target,
        )
    )

    scheduled_tasks.add(task)

    reset_admin_state(
        OWNER_ID
    )

    await update.message.reply_text(
        "✅ Scheduled successfully.\n\n"
        f"🆔 {schedule_id}\n"
        f"📅 {target.strftime('%Y-%m-%d')}\n"
        f"⏰ {target.strftime('%H:%M:%S')}\n"
        f"🌏 Timezone: "
        f"{SCHEDULE_TIMEZONE.key}"
    )

    await show_admin_menu(
        update.message.chat.id,
        context,
    )

    return True


# ======================================
# SCHEDULE LIST
# ======================================

async def schedulelist_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.effective_user.id != OWNER_ID:
        return

    try:

        schedules = get_schedules()

    except Exception as e:

        await update.message.reply_text(
            "❌ Could not load schedules.\n\n"
            f"Error: {e}"
        )

        return

    if not schedules:

        await update.message.reply_text(
            "📅 No scheduled posts."
        )

        return

    now = datetime.now(
        SCHEDULE_TIMEZONE
    )

    lines = [
        "📅 SCHEDULED POSTS",
        "",
    ]

    sorted_schedules = []

    for schedule_id, data in schedules.items():

        if not isinstance(data, dict):
            continue

        target_string = data.get("target")

        if not target_string:
            continue

        try:

            target = datetime.fromisoformat(
                target_string
            )

            if target.tzinfo is None:

                target = target.replace(
                    tzinfo=SCHEDULE_TIMEZONE
                )

        except Exception:

            continue

        sorted_schedules.append(
            (
                target,
                str(schedule_id),
                data,
            )
        )

    sorted_schedules.sort(
        key=lambda x: x[0]
    )

    if not sorted_schedules:

        await update.message.reply_text(
            "📅 No valid scheduled posts."
        )

        return

    for index, (
        target,
        schedule_id,
        data,
    ) in enumerate(
        sorted_schedules,
        start=1,
    ):

        post_type = data.get(
            "post_type",
            "normal",
        )

        code = data.get(
            "code",
            "unknown",
        )

        caption = data.get(
            "caption",
            "",
        )

        if caption:

            caption = caption.replace(
                "\n",
                " ",
            )

            if len(caption) > 50:

                caption = (
                    caption[:47]
                    + "..."
                )

        status = (
            "⏳ Pending"
            if target > now
            else "⚠️ Due"
        )

        lines.append(
            f"{index}. {status}"
        )

        lines.append(
            f"📅 {target.strftime('%Y-%m-%d')}"
        )

        lines.append(
            f"⏰ {target.strftime('%H:%M:%S')}"
        )

        lines.append(
            f"📂 Type: {post_type}"
        )

        lines.append(
            f"🔑 Code: {code}"
        )

        lines.append(
            f"🆔 ID: {schedule_id}"
        )

        if caption:

            lines.append(
                f"📝 {caption}"
            )

        lines.append("")

    lines.append(
        f"🌏 Timezone: "
        f"{SCHEDULE_TIMEZONE.key}"
    )

    await update.message.reply_text(
        "\n".join(lines)
    )


# ======================================
# POST MEDIA
# ======================================

async def handle_post_media(
    update,
    context,
):

    data = admin_post_data.get(
        OWNER_ID
    )

    if not data:
        return False

    if data.get("step") != "media":
        return False

    msg = update.message

    if not (
        msg.video
        or msg.photo
        or msg.document
        or msg.animation
    ):

        await msg.reply_text(
            "❌ Please send post media "
            "(video, photo, document or animation)."
        )

        return True

    data["media_message"] = msg

    data["media_chat_id"] = (
        msg.chat.id
    )

    data["media_message_id"] = (
        msg.message_id
    )

    data["step"] = "caption"

    await msg.reply_text(
        "📝 Send caption."
    )

    return True


# ======================================
# CAPTION
# ======================================

async def handle_caption(
    update,
    context,
):

    data = admin_post_data.get(
        OWNER_ID
    )

    if not data:
        return False

    if data.get("step") != "caption":
        return False

    data["caption"] = (
        update.message.text
        or ""
    )

    data["step"] = "send_method"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🚀 Send Now",
                    callback_data="post:send_now",
                )
            ],
            [
                InlineKeyboardButton(
                    "⏰ Schedule",
                    callback_data="post:schedule",
                )
            ],
        ]
    )

    await update.message.reply_text(
        "Choose method:",
        reply_markup=keyboard,
    )

    return True


# ======================================
# POST BUTTONS
# ======================================

async def post_buttons(
    update,
    context,
):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != OWNER_ID:
        return

    data = admin_post_data.get(
        OWNER_ID
    )

    if not data:
        return

    if query.data == "post:send_now":

        try:

            await send_post_to_channel(
                data,
                context,
            )

            reset_admin_state(
                OWNER_ID
            )

            await query.edit_message_text(
                "✅ Posted."
            )

            await show_admin_menu(
                query.message.chat.id,
                context,
            )

        except Exception as e:

            print(
                f"❌ Immediate post failed: {e}"
            )

            await query.edit_message_text(
                "❌ Failed to post.\n\n"
                f"Error: {e}"
            )

        return

    if query.data == "post:schedule":

        data["step"] = "schedule_time"

        await query.edit_message_text(
            "⏰ Send posting time.\n\n"
            "Examples:\n"
            "8\n"
            "8:10\n"
            "13:26\n"
            "23:45\n\n"
            "🌏 Timezone: "
            f"{SCHEDULE_TIMEZONE.key}"
        )

        return


# ======================================
# ADMIN UPLOAD STOP BUTTON
# ======================================

async def upload_stop_button(
    update,
    context,
):

    query = update.callback_query

    if query.from_user.id != OWNER_ID:

        await query.answer(
            "❌ Owner only.",
            show_alert=True,
        )

        return

    await query.answer()

    try:

        await query.edit_message_reply_markup(
            reply_markup=None
        )

    except Exception as e:

        print(
            f"⚠️ Could not remove stop button: "
            f"{e}"
        )

    if not owner_mode:

        await query.message.reply_text(
            "ℹ️ Upload mode is not active."
        )

        return

    files = upload_batches.pop(
        OWNER_ID,
        [],
    )

    if not files:

        await query.message.reply_text(
            "❌ No files."
        )

        return

    mode = owner_mode

    await process_uploaded_files(
        update=update,
        context=context,
        files=files,
        mode=mode,
    )


# ======================================
# MODE BUTTONS
# ======================================

async def mode_buttons(
    update,
    context,
):

    global owner_mode

    query = update.callback_query

    await query.answer()

    if query.from_user.id != OWNER_ID:
        return

    user_id = OWNER_ID

    # ==================================
    # VIP
    #
    # BLOCKED WHEN DISABLED.
    # ==================================

    if query.data == "mode:vip":

        if not VIP_ENABLED:

            await query.answer(
                "VIP is temporarily disabled.",
                show_alert=True,
            )

            return

        reset_admin_state(
            user_id
        )

        owner_mode = "vip"

        upload_batches[user_id] = []

        await query.edit_message_text(
            "🟣 VIP Post Mode\n\n"
            "📤 Send files.\n\n"
            "You can send as many files as you want.\n\n"
            "When finished press:\n"
            "🛑 Stop Uploading\n\n"
            "Or type /stop\n\n"
            "Cancel post: /cancel"
        )

        return

    # ==================================
    # NORMAL
    # ==================================

    if query.data == "mode:normal":

        reset_admin_state(
            user_id
        )

        owner_mode = "normal"

        upload_batches[user_id] = []

        await query.edit_message_text(
            "🔵 Normal Post Mode\n\n"
            "📤 Send files.\n\n"
            "You can send as many files as you want.\n\n"
            "When finished press:\n"
            "🛑 Stop Uploading\n\n"
            "Or type /stop\n\n"
            "Cancel post: /cancel"
        )

        return

    # ==================================
    # SUB2UNLOCK
    # ==================================

    if query.data == "mode:sub2unlock":

        reset_admin_state(
            user_id
        )

        owner_mode = "sub2unlock"

        context.user_data[
            "waiting_sub2unlock_channel"
        ] = True

        await query.edit_message_text(
            "🟢 Sub2Unlock Mode\n\n"
            "Send channel username or ID.\n\n"
            "🌐 Public:\n"
            "@channelname\n"
            "https://t.me/channelname\n\n"
            "🔐 Private:\n"
            "-1001234567890\n\n"
            "Cancel post: /cancel"
        )

        return


# ======================================
# OWNER UPLOAD
#
# NO 20-SECOND TIMER.
# ALL FILES ARE COLLECTED UNTIL STOP.
# ======================================

async def owner_upload(
    update,
    context,
):

    global owner_mode

    if not update.message:
        return False

    if update.effective_user.id != OWNER_ID:
        return False

    if not owner_mode:
        return False

    if OWNER_ID not in upload_batches:

        upload_batches[OWNER_ID] = []

    # ==================================
    # ADD FILE
    # ==================================

    upload_batches[OWNER_ID].append(
        update.message
    )

    count = len(
        upload_batches[OWNER_ID]
    )

    print(
        "================================"
    )

    print(
        "📥 ADMIN UPLOAD"
    )

    print(
        f"Mode: {owner_mode}"
    )

    print(
        f"Batch count: {count}"
    )

    print(
        f"Storage: {CHANNEL_ID}"
    )

    print(
        "================================"
    )

    # ==================================
    # REMOVE OLD STOP MESSAGE
    # ==================================

    old_message_id = context.user_data.get(
        "upload_stop_message_id"
    )

    old_chat_id = context.user_data.get(
        "upload_stop_chat_id"
    )

    if old_message_id and old_chat_id:

        try:

            await context.bot.delete_message(
                chat_id=old_chat_id,
                message_id=old_message_id,
            )

        except Exception as e:

            print(
                f"⚠️ Old upload status removal failed: "
                f"{e}"
            )

    # ==================================
    # ONE CURRENT BATCH STATUS
    # ==================================

    try:

        button_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"📥 {count} file"
                f"{'s' if count != 1 else ''} received."
            ),
            reply_markup=get_upload_stop_keyboard(),
        )

        context.user_data[
            "upload_stop_message_id"
        ] = button_message.message_id

        context.user_data[
            "upload_stop_chat_id"
        ] = button_message.chat.id

    except Exception as e:

        print(
            f"⚠️ Could not show upload status: "
            f"{e}"
        )

    return True


# ======================================
# PROCESS ADMIN FILES
#
# ALWAYS CHANNEL_ID.
# NEVER UPLOAD_CHANNEL_ID.
# ======================================

async def process_uploaded_files(
    update,
    context,
    files,
    mode,
):

    global owner_mode

    if not files:

        await update.effective_chat.send_message(
            "❌ No files."
        )

        return

    copied = []

    for i, msg in enumerate(
        files,
        start=1,
    ):

        print(
            "================================"
        )

        print(
            f"📦 SAVING ADMIN FILE "
            f"{i}/{len(files)}"
        )

        print(
            f"From: {msg.chat.id}"
        )

        print(
            f"Message: {msg.message_id}"
        )

        print(
            f"Storage: {CHANNEL_ID}"
        )

        print(
            "================================"
        )

        result = await copy_message_with_retry(
            context.bot,
            chat_id=CHANNEL_ID,
            from_chat_id=msg.chat.id,
            message_id=msg.message_id,
            label="admin storage",
        )

        copied.append(
            result.message_id
        )

    # ==================================
    # CREATE CODE
    # ==================================

    code = secrets.token_urlsafe(8)

    # ==================================
    # FIREBASE
    # ==================================

    if mode == "vip":

        save_file(
            code,
            copied,
            post_type="vip",
        )

    elif mode == "normal":

        save_file(
            code,
            copied,
            post_type="normal",
        )

    elif mode == "sub2unlock":

        save_file(
            code,
            copied,
            sub2unlock_channel_id,
            sub2unlock_join_link,
            post_type="sub2unlock",
        )

    # ==================================
    # POST STATE
    # ==================================

    admin_post_data[OWNER_ID] = {

        "step": "media",

        "post_type": mode,

        "code": code,

        "link": make_web_link(code),

        "media_message": None,

        "media_chat_id": None,

        "media_message_id": None,

        "caption": None,
    }

    # ==================================
    # CLEAN UP
    # ==================================

    context.user_data.pop(
        "upload_stop_message_id",
        None,
    )

    context.user_data.pop(
        "upload_stop_chat_id",
        None,
    )

    owner_mode = None

    print(
        "================================"
    )

    print(
        "✅ ADMIN FILES SAVED"
    )

    print(
        f"Files: {len(copied)}"
    )

    print(
        f"Code: {code}"
    )

    print(
        f"Storage: {CHANNEL_ID}"
    )

    print(
        "================================"
    )

    await update.effective_chat.send_message(
        "✅ Files saved to private storage.\n\n"
        "🖼 Now send the post image/video/media."
    )


# ======================================
# /STOP
# ======================================

async def stop(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    global owner_mode

    if update.effective_user.id != OWNER_ID:
        return

    files = upload_batches.pop(
        OWNER_ID,
        [],
    )

    if not files:

        await update.message.reply_text(
            "❌ No files."
        )

        return

    # ==================================
    # REMOVE CURRENT STOP BUTTON
    # ==================================

    old_message_id = context.user_data.pop(
        "upload_stop_message_id",
        None,
    )

    old_chat_id = context.user_data.pop(
        "upload_stop_chat_id",
        None,
    )

    if old_message_id and old_chat_id:

        try:

            await context.bot.delete_message(
                chat_id=old_chat_id,
                message_id=old_message_id,
            )

        except Exception as e:

            print(
                f"⚠️ Could not remove stop message: "
                f"{e}"
            )

    mode = owner_mode

    if not mode:

        await update.message.reply_text(
            "❌ Upload mode is not active."
        )

        return

    await process_uploaded_files(
        update=update,
        context=context,
        files=files,
        mode=mode,
    )


# ======================================
# /CANCEL
# ======================================

async def cancel_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    global owner_mode

    if update.effective_user.id != OWNER_ID:
        return

    has_upload = bool(
        upload_batches.get(OWNER_ID)
    )

    has_post = bool(
        admin_post_data.get(OWNER_ID)
    )

    is_waiting_channel = bool(
        context.user_data.get(
            "waiting_sub2unlock_channel"
        )
    )

    if not (
        owner_mode
        or has_upload
        or has_post
        or is_waiting_channel
    ):

        await update.message.reply_text(
            "ℹ️ No active post creation."
        )

        return

    # ==================================
    # REMOVE STOP MESSAGE
    # ==================================

    old_message_id = context.user_data.pop(
        "upload_stop_message_id",
        None,
    )

    old_chat_id = context.user_data.pop(
        "upload_stop_chat_id",
        None,
    )

    if old_message_id and old_chat_id:

        try:

            await context.bot.delete_message(
                chat_id=old_chat_id,
                message_id=old_message_id,
            )

        except Exception as e:

            print(
                f"⚠️ Could not remove upload message: "
                f"{e}"
            )

    # ==================================
    # RESET EVERYTHING
    # ==================================

    reset_admin_state(
        OWNER_ID
    )

    context.user_data.pop(
        "waiting_sub2unlock_channel",
        None,
    )

    context.user_data.pop(
        "upload_stop_message_id",
        None,
    )

    context.user_data.pop(
        "upload_stop_chat_id",
        None,
    )

    await update.message.reply_text(
        "❌ Post creation cancelled."
    )

    await show_admin_menu(
        update.message.chat.id,
        context,
    )


# ======================================
# SUB2UNLOCK CHANNEL
# ======================================

async def handle_sub2unlock_channel(
    update,
    context,
):

    global sub2unlock_channel
    global sub2unlock_channel_id
    global sub2unlock_join_link

    if update.effective_user.id != OWNER_ID:
        return False

    if not context.user_data.get(
        "waiting_sub2unlock_channel"
    ):
        return False

    text = update.message.text.strip()

    if not text:

        await update.message.reply_text(
            "❌ Please send the channel."
        )

        return True

    chat_identifier = text

    # ==================================
    # TELEGRAM LINK
    # ==================================

    if "t.me/" in text:

        part = text.split(
            "t.me/",
            1
        )[1]

        if part.startswith("+"):

            await update.message.reply_text(
                "⚠️ Private invite link detected.\n\n"
                "Please send the private channel ID.\n\n"
                "Example:\n"
                "-1001234567890"
            )

            return True

        username = part.split(
            "?",
            1
        )[0]

        username = username.split(
            "/",
            1
        )[0]

        if not username:

            await update.message.reply_text(
                "❌ Invalid channel link."
            )

            return True

        chat_identifier = "@" + username

    # ==================================
    # CHANNEL ID
    # ==================================

    if text.startswith("-100"):

        try:

            chat_identifier = int(text)

        except ValueError:

            await update.message.reply_text(
                "❌ Invalid channel ID."
            )

            return True

    # ==================================
    # GET CHANNEL
    # ==================================

    try:

        chat = await context.bot.get_chat(
            chat_identifier
        )

    except Exception as e:

        print(
            f"❌ Could not access channel: {e}"
        )

        await update.message.reply_text(
            "❌ I could not access this channel.\n\n"
            "Make sure the bot is already inside "
            "the channel and is an admin."
        )

        return True

    if chat.type != "channel":

        await update.message.reply_text(
            "❌ This is not a Telegram channel."
        )

        return True

    # ==================================
    # BOT ADMIN CHECK
    # ==================================

    try:

        bot_member = await context.bot.get_chat_member(
            chat_id=chat.id,
            user_id=context.bot.id,
        )

        if bot_member.status not in (
            "administrator",
            "creator",
        ):

            await update.message.reply_text(
                "❌ The bot is not an administrator "
                "in this channel."
            )

            return True

    except Exception as e:

        print(
            f"❌ Bot admin check error: {e}"
        )

        await update.message.reply_text(
            "❌ I cannot check the bot's permissions."
        )

        return True

    # ==================================
    # SAVE CHANNEL
    # ==================================

    sub2unlock_channel = chat

    sub2unlock_channel_id = chat.id

    if chat.username:

        sub2unlock_join_link = (
            f"https://t.me/{chat.username}"
        )

    else:

        try:

            invite = (
                await context.bot.create_chat_invite_link(
                    chat_id=chat.id
                )
            )

            sub2unlock_join_link = (
                invite.invite_link
            )

        except Exception as e:

            print(
                f"❌ Private invite creation failed: "
                f"{e}"
            )

            await update.message.reply_text(
                "❌ Channel found, but I could not "
                "create an invite link."
            )

            return True

    context.user_data.pop(
        "waiting_sub2unlock_channel",
        None,
    )

    await update.message.reply_text(
        "✅ Channel connected!\n\n"
        f"📢 {chat.title}\n"
        f"🆔 {chat.id}\n\n"
        "📤 Now send your files.\n\n"
        "When finished:\n"
        "🛑 Stop Uploading\n"
        "or /stop\n\n"
        "Cancel post:\n"
        "/cancel"
    )

    return True


# ======================================
# OWNER ROUTER
# ======================================

async def owner_router(
    update,
    context,
):

    if not update.message:
        return

    user = update.effective_user

    if not user:
        return

    if user.id != OWNER_ID:
        return

    # ==================================
    # SUB2UNLOCK CHANNEL
    # ==================================

    if await handle_sub2unlock_channel(
        update,
        context,
    ):

        return

    # ==================================
    # SCHEDULE TIME
    # ==================================

    if await handle_schedule_time(
        update,
        context,
    ):

        return

    # ==================================
    # POST MEDIA
    # ==================================

    if await handle_post_media(
        update,
        context,
    ):

        return

    # ==================================
    # CAPTION
    # ==================================

    if await handle_caption(
        update,
        context,
    ):

        return

    # ==================================
    # OWNER UPLOAD
    # ==================================

    if owner_mode:

        if (
            update.message.video
            or update.message.photo
            or update.message.document
            or update.message.animation
        ):

            await owner_upload(
                update,
                context,
            )

            return


# ======================================
# STARTUP
# ======================================

async def post_init(
    application,
):

    await restore_saved_schedules(
        application
    )

    await restore_expiry_jobs(
        application
    )


# ======================================
# ERROR
# ======================================

async def error_handler(
    update,
    context,
):

    print(
        "================================"
    )

    print(
        "❌ BOT ERROR"
    )

    print(
        f"{context.error}"
    )

    print(
        "================================"
    )


# ======================================
# CREATE BOT
# ======================================

app = (
    Application
    .builder()
    .token(TOKEN)
    .post_init(post_init)
    .build()
)


# ======================================
# COMMANDS
# ======================================

app.add_handler(
    CommandHandler(
        "start",
        start,
    )
)

app.add_handler(
    CommandHandler(
        "stop",
        stop,
    )
)

app.add_handler(
    CommandHandler(
        "cancel",
        cancel_command,
    )
)

# ======================================
# VIP COMMANDS
#
# KEPT REGISTERED.
# DO NOTHING WHILE VIP_ENABLED=False.
# ======================================

app.add_handler(
    CommandHandler(
        "vip",
        vip_command,
    )
)

app.add_handler(
    CommandHandler(
        "removevip",
        removevip_command,
    )
)

app.add_handler(
    CommandHandler(
        "viplist",
        viplist_command,
    )
)

app.add_handler(
    CommandHandler(
        "schedulelist",
        schedulelist_command,
    )
)


# ======================================
# CALLBACKS
# ======================================

app.add_handler(
    CallbackQueryHandler(
        unlock_video,
        pattern=r"^unlock:",
    )
)

app.add_handler(
    CallbackQueryHandler(
        mode_buttons,
        pattern=r"^mode:",
    )
)

app.add_handler(
    CallbackQueryHandler(
        post_buttons,
        pattern=r"^post:",
    )
)

app.add_handler(
    CallbackQueryHandler(
        upload_stop_button,
        pattern=r"^upload:stop$",
    )
)


# ======================================
# ADMIN MESSAGE HANDLER
#
# ONLY OWNER.
# ======================================

app.add_handler(
    MessageHandler(
        filters.ALL & filters.User(OWNER_ID),
        owner_router,
    )
)


# ======================================
# PUBLIC SEND HANDLER
#
# IMPORTANT:
#
# filters.ALL means:
#
# TEXT       ✅
# LINKS      ✅
# TXT        ✅
# PDF        ✅
# VIDEO      ✅
# IMAGE      ✅
# AUDIO      ✅
# VOICE      ✅
# GIF        ✅
# STICKER    ✅
# CONTACT    ✅
# LOCATION   ✅
# POLL       ✅
# DICE       ✅
# ETC.       ✅
#
# OWNER IS EXCLUDED.
# ======================================

app.add_handler(
    MessageHandler(
        filters.ALL
        & ~filters.User(OWNER_ID),
        handle_public_send_file,
    )
)


# ======================================
# ERROR HANDLER
# ======================================

app.add_error_handler(
    error_handler
)


# ======================================
# RUN
# ======================================

if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        " TeNfLiX Controller Bot "
    )

    print(
        " VIP DISABLED "
    )

    print(
        " + Sub2Unlock + Schedule "
    )

    print(
        " + UNIVERSAL Public Send "
    )

    print(
        "================================"
    )

    print(
        f"Owner ID: {OWNER_ID}"
    )

    print(
        f"Admin/private storage: {CHANNEL_ID}"
    )

    print(
        f"Public Send storage: "
        f"{UPLOAD_CHANNEL_ID}"
    )

    print(
        f"Post channel: {POST_CHANNEL_ID}"
    )

    print(
        f"VIP enabled: {VIP_ENABLED}"
    )

    print(
        f"Scheduler timezone: "
        f"{SCHEDULE_TIMEZONE.key}"
    )

    print(
        "Public Send batching: "
        f"{PUBLIC_SEND_WAIT_SECONDS}s silent"
    )

    print(
        "Public Send accepts: ANY MESSAGE"
    )

    print(
        f"Current time: "
        f"{datetime.now(SCHEDULE_TIMEZONE)}"
    )

    print(
        "================================"
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
