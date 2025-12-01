import requests
import os

class DownloadError(Exception):
    pass

TERABOX_API = os.getenv("TERABOX_API")  # Railway variable

def get_direct_link(share_url: str):
    if "terabox" not in share_url.lower():
        raise DownloadError("Not a valid Terabox link.")

    if not TERABOX_API:
        raise DownloadError("TERABOX_API variable missing in Railway.")

    try:
        r = requests.get(
            TERABOX_API,
            params={"url": share_url},
            timeout=30
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        raise DownloadError(f"API error: {e}")

    direct = data.get("direct_url") or data.get("download_url")
    filename = data.get("filename")

    if not direct:
        raise DownloadError("Direct link not found.")

    return direct, filename
