import os
import logging
import io
import requests

from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from terabox import get_direct_link, DownloadError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN variable missing! Add in Railway → Variables.")

# Telegram bot normal limit ~50MB, thoda kam rakhte hain
MAX_FILE_SIZE = 48 * 1024 * 1024  # 48 MB


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Terabox link bhejo, main direct video bhejne ki कोशिश करूँगा.\n\n"
        "Agar file 48MB se badi hogi to sirf direct link bhejunga."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()

    if "terabox" not in url.lower():
        await message.reply_text("Mujhe sirf Terabox ka share link bhejo 🙂")
        return

    status = await message.reply_text("🔄 Link process ho raha hai, thoda rukko...")

    # 1) Pehle Terabox se real download link nikaalo
    try:
        direct_url, filename = get_direct_link(url)
    except DownloadError as e:
        logger.exception("Terabox DownloadError")
        await status.edit_text(f"❌ Error: {e}")
        return
    except Exception:
        logger.exception("Unexpected error in get_direct_link")
        await status.edit_text("❌ Direct link nahi mil paya. Dusra link try karo.")
        return

    if not direct_url:
        await status.edit_text("❌ Direct link empty mila. Link check karo.")
        return

    # 2) Ab direct_url se video download karo
    try:
        resp = requests.get(direct_url, stream=True, timeout=60)
        resp.raise_for_status()
    except Exception:
        logger.exception("Error while downloading video")
        await status.edit_text("❌ Video download nahi ho paaya. Thodi der baad try karo.")
        return

    # Size check
    size = int(resp.headers.get("Content-Length", 0))
    if size and size > MAX_FILE_SIZE:
        await status.edit_text(
            "⚠️ Video bahut badi hai (48 MB se zyada).\n"
            await status.edit_text("Main file send nahi kar sakta, file size 48MB se badi hai.")
    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
