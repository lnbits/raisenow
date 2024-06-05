# Data models for your extension

from sqlite3 import Row
from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request

from lnbits.lnurl import encode as lnurl_encode
from urllib.parse import urlparse

# Raises - called raisenow as raises is a reserved keyword in Python

class CreateRaiseNowData(BaseModel):
    wallet: Optional[str]
    name: Optional[str]
    description: Optional[str]
    background_image: Optional[str]
    header_image: Optional[str]
    total: Optional[int]
    live_dates: Optional[str]


class RaiseNow(BaseModel):
    id: str
    wallet: Optional[str]
    name: Optional[str]
    description: Optional[str]
    background_image: Optional[str]
    header_image: Optional[str]
    total: Optional[int]
    live_dates: Optional[str]
    lnurlpay: Optional[str]

    @classmethod
    def from_row(cls, row: Row) -> "raisenow":
        return cls(**dict(row))

# Participants

class CreateParticipantData(BaseModel):
    wallet: Optional[str]
    name: Optional[str]
    raisenow: Optional[str]
    description: Optional[str]
    total: Optional[int]


class Participant(BaseModel):
    id: str
    wallet: Optional[str]
    name: Optional[str]
    raisenow: Optional[str]
    description: Optional[str]
    total: Optional[int]
    lnurlpay: Optional[str]

    @classmethod
    def from_row(cls, row: Row) -> "raisenow":
        return cls(**dict(row))