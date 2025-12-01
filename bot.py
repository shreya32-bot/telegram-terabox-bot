import re
import os
import requests
from pyrogram import Client, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")   # Railway se read hoga

app = Client(
    "bot",
    bot_token=BOT_TOKEN
)

def extract_link(text):
    match = re.search(r'(https?://[^\s]+)', text)
    return match.group(1) if match else None


def get_direct_terabox(link):
    try:
        api = "https://api.terabox.tech/api"
        r = requests.get(api, params={"url": link})
        data = r.json()
        if data.get("status") == "success":
            return data.get("download_url")
    except Exception as e:
        print("Error extracting:", e)
        return None
    return None


@app.on_message(filters.text)
async def handle(client, message):
    text = message.text
    link = extract_link(text)

    if not link:
        return await message.reply("❌ Valid TeraBox link nahi mila.")

    msg = await message.reply("⏳ Extracting video…")

    direct = get_direct_terabox(link)

    if not direct:
        return await msg.edit("❌ Unable to extract video. Link may be expired/private.")

    try:
        await message.reply_video(direct)
        await msg.delete()
    except Exception as e:
        print(e)
        await msg.edit("❌ Error sending video. File may be too large.")


app.run()

