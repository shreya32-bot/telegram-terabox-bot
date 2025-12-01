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
    raise RuntimeError("BOT_TOKEN missing! Add it in Railway Variables.")

MAX_FILE_SIZE = 48 * 1024 * 1024   # 48 MB max for Telegram uploads


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me any *Terabox link* and I will try to download the video.\n"
        "⚠️ If video is more than 48 MB, Telegram cannot upload it, but I will give direct link."
    )


async def process_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    url = message.text.strip()

    if "terabox" not in url.lower():
        await message.reply_text("❌ Please send a valid Terabox link.")
        return

    status = await message.reply_text("🔄 Extracting download link...")

    # Step 1 → Extract direct download URL from terabox.py
    try:
        direct_url, filename = get_direct_link(url)
    except DownloadError as e:
        await status.edit_text(f"❌ Error: {e}")
        return
    except Exception:
        await status.edit_text("❌ Direct link extract nahi ho paaya.")
        return

    if not direct_url:
        await status.edit_text("❌ Direct link empty mila.")
        return

    await status.edit_text("⬇ Downloading video...")

    # Step 2 → Download the video
    try:
        resp = requests.get(direct_url, stream=True, timeout=60)
        resp.raise_for_status()
    except Exception:
        await status.edit_text("❌ Error while downloading video.")
        return

    # File size check
    size = int(resp.headers.get("Content-Length", 0))
    if size and size > MAX_FILE_SIZE:
        await status.edit_text(
            "⚠️ Video 48MB se badi hai, main send nahi kar sakta.\n\n"
            f"👇 Direct Download Link:\n{direct_url}"
        )
        return

    # Step 3 → Save chunks in RAM
    video_data = io.BytesIO()
    for chunk in resp.iter_content(1024 * 1024):
        if chunk:
            video_data.write(chunk)

        if video_data.tell() > MAX_FILE_SIZE:
            await status.edit_text(
                "⚠️ Video 48MB se badi ho gayi.\n\n"
                f"Direct link: {direct_url}"
            )
            return

    video_data.seek(0)

    if not filename:
        filename = "video.mp4"

    await status.edit_text("📤 Uploading video to Telegram...")

    # Step 4 → Send video
    try:
        await message.reply_video(
            video=InputFile(video_data, filename),
            caption="🎬 Terabox video downloaded successfully!",
        )
        await status.delete()
    except Exception:
        await status.edit_text(
            "❌ Telegram ko video send karne me error aaya.\n\n"
            f"👇 Direct link use karo:\n{direct_url}"
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, process_link))

    print("🚀 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
