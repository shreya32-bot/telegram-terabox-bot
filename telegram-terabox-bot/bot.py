import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from terabox import get_video_from_terabox

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"   # <-- Apna token yahan daalna (GitHub par mat daalna)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update, context):
    await update.message.reply_text("Send any Terabox link, I will give direct video download.")

async def handle_message(update, context):
    link = update.message.text
    await update.message.reply_text("Processing your link...")

    video_url = get_video_from_terabox(link)

    if video_url:
        await update.message.reply_video(video_url)
    else:
        await update.message.reply_text("❌ Invalid Terabox Link!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
