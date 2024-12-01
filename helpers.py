import httpx
from fastapi import Request
from lnbits.core.views.api import api_lnurlscan
from lnurl.core import encode as lnurl_encode


async def get_pr(ln_address):
    data = await api_lnurlscan(ln_address)
    if data.get("status") == "ERROR":
        return
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=f"{data['callback']}?amount=10000")
            if response.status_code != 200:
                return
            return response.json()["pr"]
    except Exception:
        return None


def lnurler(record_id: str, route_name: str, req: Request) -> str:
    url = req.url_for(route_name, record_id=record_id)
    url_str = str(url)
    if url.netloc.endswith(".onion"):
        url_str = url_str.replace("https://", "http://")
    return str(lnurl_encode(url_str))
