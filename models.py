# Data models for your extension


from pydantic import BaseModel

# Raises - called raisenow as raises is a reserved keyword in Python


class CreateRaiseNowData(BaseModel):
    name: str
    wallet: str
    description: str | None
    background_image: str | None
    header_image: str | None
    total: int | None
    live_dates: str | None


class RaiseNow(BaseModel):
    id: str
    name: str
    wallet: str
    description: str | None
    background_image: str | None
    header_image: str | None
    total: int | None = 0
    live_dates: str | None
    lnurlpay: str | None


# Participants


class CreateParticipantData(BaseModel):
    name: str
    raisenow: str
    description: str | None
    profile_image: str | None
    total: int | None = 0
    lnaddress: str | None


class Participant(BaseModel):
    id: str
    name: str
    raisenow: str
    description: str | None
    profile_image: str | None
    total: int | None
    lnaddress: str | None
    lnurlpay: str | None
