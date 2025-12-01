import os
import logging
import io
import re
import requests
from urllib.parse import urljoin

from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing! Add it in Railway Variables.")

MAX_FILE_SIZE = 48 * 1024 * 1024   # 48MB Limit


# -------------------------------
#  TERABOX DIRECT LINK EXTRACTOR
# -------------------------------

def extract_direct_link(share_url):
    """
    Extract direct download link from Terabox share link (No API Needed)
    Works on 1024terabox, teraboxapp, etc.
    """

    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": share_url,
    }

    # Load the page
    r = session.get(share_url, headers=headers, timeout=20)
    if r.status_code != 200:
        raise Exception("Could not load page.")

    html = r.text

    # Step 1 → Find file name
    filename = None
    fn_match = re.search(r'"file_name":"(.*?)"', html)
    if fn_match:
        filename = fn_match.group(1)

    # Step 2 → Find file download URL
    link_match = re.search(r'"direct_link":"(https.*?)"', html)

    if not link_match:
        # fallback method: find any download link
        link_match = re.search(r'(https://.*?download.*?)"', html)

    if not link_match:
        raise Exception("Direct link not found!")

    link = link_match.group(1).replace("\\/", "/")

    # Clean URL
    link = link.replace("u002F", "/")

    return link, filename


# -------------------------------
#  BOT HANDLERS
# -------------------------------

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

    status = await message.reply_text("🔄 Extracting direct download link...")

    # Step 1 → Extract Link
    try:
        direct_url, filename = extract_direct_link(url)
    except Exception as e:
        await status.edit_text(f"❌ Error extracting link: {e}")
        return

    if not direct_url:
        await status.edit_text("❌ No direct link found.")
        return

    await status.edit_text("⬇ Downloading video...")

    # Step 2 → Download Video
    try:
        resp = requests.get(direct_url, stream=True, timeout=60)
        resp.raise_for_status()
    except Exception:
        await status.edit_text("❌ Error while downloading video.")
        return

    size = int(resp.headers.get("Content-Length", 0))
    if size and size > MAX_FILE_SIZE:
        await status.edit_text(
            "⚠️ Video 48MB se badi hai. Upload nahi kar sakta.\n\n"
            f"👇 Direct link use karo:\n{direct_url}"
        )
        return

    video_data = io.BytesIO()
    for chunk in resp.iter_content(1024 * 1024):
        if chunk:
            video_data.write(chunk)

    video_data.seek(0)

    if not filename:
        filename = "video.mp4"

    await status.edit_text("📤 Uploading video to Telegram...")

    # Step 3 → Upload to Telegram
    try:
        await message.reply_video(
            video=InputFile(video_data, filename),
            caption="🎬 Terabox video downloaded successfully!",
        )
        await status.delete()
    except Exception:
        await status.edit_text(
            "⚠️ Could not upload to Telegram.\n\n"
            f"Direct Link: {direct_url}"
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, process_link))

    print("🚀 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
