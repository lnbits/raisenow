from fastapi import Request
from lnbits.settings import settings
from lnurl import LnurlPayActionResponse, LnurlPayResponse
from lnurl import execute_pay_request as lnurlp
from lnurl import handle as lnurl_handle
from lnurl.core import encode as lnurl_encode


async def get_pr(ln_address: str, amount_msat: int = 10_000) -> str | None:
    try:
        res = await lnurl_handle(ln_address)
        if not isinstance(res, LnurlPayResponse):
            return None
        res2 = await lnurlp(
            res,
            msat=str(amount_msat),
            user_agent=settings.user_agent,
            timeout=5,
        )
        if not isinstance(res, LnurlPayActionResponse):
            return None
        return res2.pr
    except Exception as e:
        print(f"Error handling LNURL: {e}")
        return None


def lnurler(record_id: str, route_name: str, req: Request) -> str:
    url = req.url_for(route_name, record_id=record_id)
    url_str = str(url)
    if url.netloc.endswith(".onion"):
        url_str = url_str.replace("https://", "http://")
    return str(lnurl_encode(url_str))
