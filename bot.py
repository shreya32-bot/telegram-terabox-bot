import re
import os
import requests
from pyrogram import Client, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("bot", bot_token=BOT_TOKEN)


def extract_link(text):
    match = re.search(r'(https?://[^\s]+)', text)
    return match.group(1) if match else None


def get_terabox(link):
    api = "https://api.terabox.tech/api"
    r = requests.get(api, params={"url": link}).json()

    if r.get("status") == "success":
        return r.get("download_url"), r.get("size")
    return None, None


@app.on_message(filters.text)
async def main(client, message):
    link = extract_link(message.text)

    if not link:
        return await message.reply("❌ No valid TeraBox link found.")

    msg = await message.reply("⏳ Processing video…")

    dl_url, size = get_terabox(link)

    if not dl_url:
        return await msg.edit("❌ Failed to extract video.")

    # Size check (50MB limit)
    if size and size > 48 * 1024 * 1024:
        return await msg.edit(
            f"⚠️ Video is **{round(size/1024/1024,2)} MB**, too large to upload.\n\n"
            f"➡️ Here is the direct download link:\n{dl_url}"
        )

    try:
        await message.reply_video(dl_url)
        await msg.delete()
    except:
        await msg.edit("❌ Error while uploading. File may be too large.")


app.run()
