# Data models for your extension

from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from lnurl import encode as lnurl_encode

# Raises - called raisenow as raises is a reserved keyword in Python


class CreateRaiseNowData(BaseModel):
    name: str
    wallet: Optional[str]
    description: Optional[str]
    background_image: Optional[str]
    header_image: Optional[str]
    live_dates: Optional[str]
    total: Optional[int]
    live_dates: Optional[str]


class RaiseNow(BaseModel):
    id: str
    name: str
    wallet: Optional[str]
    description: Optional[str]
    background_image: Optional[str]
    header_image: Optional[str]
    live_dates: Optional[str]
    total: Optional[int] = 0
    live_dates: Optional[str]
    lnurlpay: Optional[str]

    def lnurlpay(self, req: Request) -> str:
        url = req.url_for("raisenow.api_lnurl_pay", record_id=id)
        url_str = str(url)
        if url.netloc.endswith(".onion"):
            url_str = url_str.replace("https://", "http://")

        return lnurl_encode(url_str)


# Participants


class CreateParticipantData(BaseModel):
    name: str
    raisenow: str
    description: Optional[str]
    profile_image: Optional[str]
    total: Optional[int] = 0
    lnaddress: Optional[str]


class Participant(BaseModel):
    id: str
    name: str
    raisenow: str
    description: Optional[str]
    profile_image: Optional[str]
    total: Optional[int]
    lnaddress: Optional[str]

    def lnurlpay(self, req: Request) -> str:
        url = req.url_for("raisenow.api_lnurl_pay", record_id=id)
        url_str = str(url)
        if url.netloc.endswith(".onion"):
            url_str = url_str.replace("https://", "http://")

        return lnurl_encode(url_str)
