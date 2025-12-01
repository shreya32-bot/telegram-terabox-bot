from typing import Tuple, Optional
import os
import requests

class DownloadError(Exception):
    """Custom error for Terabox failures"""


# optional: Railway variable se API URL lo
TERABOX_API = os.getenv("TERABOX_API")  # e.g. https://example.com/api/terabox


def get_direct_link(share_url: str) -> Tuple[str, Optional[str]]:
    """
    Terabox share_url se direct download URL nikaalta hai.

    👉 IMPORTANT:
       - Yahaan tumko koi real API/service use karni padegi
         jo Terabox se direct link nikal sake.
       - Niche sirf example structure diya hai.
    """

    if not share_url or "terabox" not in share_url.lower():
        raise DownloadError("Valid Terabox link bhejo.")

    if not TERABOX_API:
        # Agar tumhare paas abhi API nahi hai to filhaal wahi URL return kar do
        # jise tum koi external site se nikal ke yahan paste karoge.
        # Is case me bot download karne ke liye isi direct_url ka use karega.
        return share_url, None

    try:
        resp = requests.get(
            TERABOX_API,
            params={"url": share_url},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise DownloadError(f"API request fail ho gayi: {e}")

    # yeh keys tumhare actual API ke hisaab se change karna padega
    direct_url = data.get("direct_url") or data.get("download_url")
    filename = data.get("filename")

    if not direct_url:
        raise DownloadError("API se direct_url nahi mila.")

    return direct_url, filename
