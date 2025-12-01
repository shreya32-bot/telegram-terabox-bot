
from typing import Tuple, Optional

class DownloadError(Exception):
    """Custom error for Terabox failures"""

def get_direct_link(share_url: str) -> Tuple[str, Optional[str]]:
    """Basic placeholder: returns input URL as direct link."""

    if not share_url or "terabox" not in share_url.lower():
        raise DownloadError("Invalid Terabox link.")

    direct_url = share_url
    filename = None
    return direct_url, filename
