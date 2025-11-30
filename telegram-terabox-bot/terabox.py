import requests

def get_video_from_terabox(url):
    try:
        api = "https://api.teraboxplayer.com/?url=" + url
        res = requests.get(api).json()

        if "video" in res:
            return res["video"]
        return None

    except:
        return None
