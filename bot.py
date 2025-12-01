import re
import requests
from pyrogram import Client, filters

BOT_TOKEN = "YOUR_BOT_TOKEN"

app = Client(
    "bot",
    bot_token=BOT_TOKEN
)

def extract_link(text):
    match = re.search(r'(https?://[^\s]+)', text)
    return match.group(1) if match else None

def get_terabox_direct(link):
    api_url = "https://teraboxvideodownloader.neerajx.repl.co/api"
    r = requests.get(api_url, params={"url": link})
    data = r.json()

    if data.get("status") == "success":
        return data.get("download_url")
    return None

@app.on_message(filters.text)
async def dl(client, message):
    text = message.text

    link = extract_link(text)
    if not link:
        return await message.reply("❌ No valid link found.")

    msg = await message.reply("⏳ Extracting...")

    direct = get_terabox_direct(link)
    
    if not direct:
        return await msg.edit("❌ Unable to extract video.")

    try:
        await message.reply_video(direct)
        await msg.delete()
    except:
        await msg.edit("❌ Error while sending video.")

app.run()
