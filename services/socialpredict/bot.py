#!/usr/bin/env python3
import os
import re
import asyncio
from typing import Dict, Optional

import httpx
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# ====== Config via environment variables ======
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
BASE_URL = os.environ.get("PREDICT_BASE_URL", "https://predict.dabney.house").rstrip("/")
ADMIN_USERNAME = os.environ.get("PREDICT_ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("PREDICT_ADMIN_PASSWORD", "")

LOGIN_PATH = "/api/v0/login"
CREATEUSER_PATH = "/api/v0/admin/createuser"

# Basic username rule: "first name + first letter of last name"
# Example: "alexj", "sarahk"
USERNAME_RE = re.compile(r"^[a-z]+[a-z]$", re.IGNORECASE)

# In-memory "one account per person" guard (not persistent across restarts)
created_for_telegram_user: Dict[int, str] = {}

TIMEOUT = httpx.Timeout(10.0, connect=10.0)

def require_env() -> None:
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not ADMIN_USERNAME:
        missing.append("PREDICT_ADMIN_USERNAME")
    if not ADMIN_PASSWORD:
        missing.append("PREDICT_ADMIN_PASSWORD")
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")

async def api_login_get_token(client: httpx.AsyncClient) -> str:
    """
    POST /api/v0/login
    {"username":"admin","password":"..."} -> {"token":"..."}
    """
    url = f"{BASE_URL}{LOGIN_PATH}"
    payload = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    r = await client.post(url, json=payload)
    r.raise_for_status()
    data = r.json()
    token = data.get("token")
    if not token:
        raise RuntimeError(f"Login succeeded but no token in response: {data}")
    return token

async def api_create_user(client: httpx.AsyncClient, token: str, username: str) -> dict:
    """
    POST /api/v0/admin/createuser
    Authorization: Bearer <token>
    {"username":"testuser"} -> {"message":"User created successfully","password":"...","username":"...","usertype":"REGULAR"}
    """
    url = f"{BASE_URL}{CREATEUSER_PATH}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"username": username}
    r = await client.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()

def normalize_username(raw: str) -> str:
    return raw.strip()

def username_ok(u: str) -> bool:
    # Enforce letters only, at least 2 chars, and "firstname + lastinitial" shape.
    # This is intentionally strict so people don't paste weird stuff.
    return bool(USERNAME_RE.fullmatch(u)) and len(u) >= 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = (
        "This bot creates an account for the prediction site.\n\n"
        "Run:\n"
        "`/makeaccount <username>`\n\n"
        "Username format: **first name + first letter of last name** (letters only).\n"
        "Example: `alexj`, `sarahk`.\n\n"
        "Please only make **one account per person** (honor system)."
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def makeaccount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    tg_user = update.effective_user
    if not tg_user:
        await update.message.reply_text("Could not identify your Telegram user.")
        return

    user_id = tg_user.id

    if user_id in created_for_telegram_user:
        await update.message.reply_text(
            f"You already created an account username: `{created_for_telegram_user[user_id]}`\n"
            "Honor system: one account per person.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/makeaccount <username>`\nExample: `/makeaccount alexj`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    username = normalize_username(context.args[0])

    if not username_ok(username):
        await update.message.reply_text(
            "Invalid username.\n\n"
            "Use letters only, format: **first name + first letter of last name**.\n"
            "Example: `alexj`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    await update.message.reply_text("Creating your account…")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            token = await api_login_get_token(client)
            data = await api_create_user(client, token, username)
        except httpx.HTTPStatusError as e:
            # Avoid leaking sensitive response bodies if they include tokens.
            status = e.response.status_code if e.response else "unknown"
            await update.message.reply_text(f"API error (HTTP {status}).")
            return
        except Exception as e:
            await update.message.reply_text(f"Error creating account: {type(e).__name__}: {e}")
            return

    # Expected: {"message":"User created successfully","password":"...","username":"...","usertype":"REGULAR"}
    created_username = data.get("username", username)
    password = data.get("password")

    if not password:
        await update.message.reply_text(
            "Account creation response did not include a password. Ask an admin to check the server logs."
        )
        return

    created_for_telegram_user[user_id] = created_username

    await update.message.reply_text(
        "✅ Account created.\n\n"
        f"**Username:** `{created_username}`\n"
        f"**Password:** `{password}`\n\n"
        "Save this password now.",
        parse_mode=ParseMode.MARKDOWN,
    )

async def main() -> None:
    require_env()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("makeaccount", makeaccount))

    # Run until Ctrl+C
    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    asyncio.run(main())
