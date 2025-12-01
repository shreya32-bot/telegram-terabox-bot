import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from terabox import get_direct_link, DownloadError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found. Add it in Railway → Variables.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me a Terabox link and I will try to get direct video link."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "terabox" not in url.lower():
        await update.message.reply_text("Please send a valid Terabox link.")
        return
    
    status = await update.message.reply_text("Processing... please wait!")

    try:
        direct_url, filename = get_direct_link(url)
        await status.edit_text(f"Direct Link:\n{direct_url}")
    except Exception as e:
        await status.edit_text(f"Error: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
