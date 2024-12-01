# Data models for your extension

from typing import Optional

from pydantic import BaseModel

# Raises - called raisenow as raises is a reserved keyword in Python


class CreateRaiseNowData(BaseModel):
    name: str
    wallet: str
    description: Optional[str]
    background_image: Optional[str]
    header_image: Optional[str]
    total: Optional[int]
    live_dates: Optional[str]


class RaiseNow(BaseModel):
    id: str
    name: str
    wallet: str
    description: Optional[str]
    background_image: Optional[str]
    header_image: Optional[str]
    total: Optional[int] = 0
    live_dates: Optional[str]
    lnurlpay: Optional[str]


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
    lnurlpay: Optional[str]
