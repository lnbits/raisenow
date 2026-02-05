from fastapi import Request
from lnurl.core import encode as lnurl_encode


def lnurler(record_id: str, route_name: str, req: Request) -> str:
    url = req.url_for(route_name, record_id=record_id)
    url_str = str(url)
    if url.netloc.endswith(".onion"):
        url_str = url_str.replace("https://", "http://")
    return str(lnurl_encode(url_str))
