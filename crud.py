from typing import List, Optional, Union

from lnbits.helpers import urlsafe_short_hash
from lnbits.lnurl import encode as lnurl_encode
from . import db
from .models import CreateRaiseNowData, RaiseNow, CreateParticipantData, Participant
from loguru import logger
from fastapi import Request
from lnurl import encode as lnurl_encode
import shortuuid

#######################################
############### RAISES ################
#######################################

async def create_raisenow(
    wallet_id: str, data: CreateRaiseNowData, req: Request
) -> RaiseNow:
    raisenow_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO raisenow.raises (id, wallet, name, description, closing_date, lnurlpay)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            raisenow_id,
            wallet_id,
            data.name,
            data.description,
            data.total,
            data,closing_date,
            data.lnurlpay,
        ),
    )
    raisenow = await get_raisenow(raisenow_id, req)
    assert raisenow, "Newly created table couldn't be retrieved"
    return raisenow

async def get_raisenow(
    raisenow_id: str, req: Optional[Request] = None
) -> Optional[RaiseNow]:
    row = await db.fetchone(
        "SELECT * FROM raisenow.raises WHERE id = ?", (raisenow_id,)
    )
    if not row:
        return None
    rowAmended = raisenow(**row)
    if req:
        rowAmended.lnurlpay = lnurl_encode(
            req.url_for("raisenow.api_lnurl_pay", raisenow_id=row.id)._url
        )
    return rowAmended


async def get_raisenows(
    wallet_ids: Union[str, List[str]], req: Optional[Request] = None
) -> List[RaiseNow]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM raisenow.raises WHERE wallet IN ({q})", (*wallet_ids,)
    )
    tempRows = [raisenow(**row) for row in rows]
    if req:
        for row in tempRows:
            row.lnurlpay = lnurl_encode(
                req.url_for("raisenow.api_lnurl_pay", raisenow_id=row.id)._url
            )
    return tempRows


async def update_raisenow(
    raisenow_id: str, req: Optional[Request] = None, **kwargs
) -> RaiseNow:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    logger.debug(kwargs.items())
    await db.execute(
        f"UPDATE raisenow.raises SET {q} WHERE id = ?",
        (*kwargs.values(), raisenow_id),
    )
    raisenow = await get_raisenow(raisenow_id, req)
    assert raisenow, "Newly updated raisenow couldn't be retrieved"
    return raisenow


async def delete_raisenow(raisenow_id: str) -> None:
    await db.execute(
        "DELETE FROM raisenow.raises WHERE id = ?", (raisenow_id,)
    )


#######################################
########### Particpants ###############
#######################################


async def create_participant(
    wallet_id: str, data: CreateParticipantData, req: Request
) -> Participant:
    participant_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO raisenow.participants (id, wallet, name, raisenow, description, total)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            participant_id,
            wallet_id,
            data.name,
            data.raisenow,
            data.description,
            data.total,
        ),
    )
    participant = await get_participant(participant_id, req)
    assert participant, "Newly created participant couldn't be retrieved"
    return participant


async def get_participant(
    raisenow_id: str, req: Optional[Request] = None
) -> Optional[Participant]:
    row = await db.fetchone(
        "SELECT * FROM raisenow.participants WHERE id = ?", (raisenow_id,)
    )
    if not row:
        return None
    rowAmended = raisenow(**row)
    if req:
        rowAmended.lnurlpay = lnurl_encode(
            req.url_for("raisenow.api_lnurl_pay", raisenow_id=row.id)._url
        )
    return rowAmended


async def get_participants(
    wallet_ids: Union[str, List[str]], req: Optional[Request] = None
) -> List[Participant]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM raisenow.participants WHERE wallet IN ({q})", (*wallet_ids,)
    )
    tempRows = [raisenow(**row) for row in rows]
    if req:
        for row in tempRows:
            row.lnurlpay = lnurl_encode(
                req.url_for("raisenow.api_lnurl_pay", raisenow_id=row.id)._url
            )
    return tempRows


async def update_participant(
    raisenow_id: str, req: Optional[Request] = None, **kwargs
) -> Participant:
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    logger.debug(kwargs.items())
    await db.execute(
        f"UPDATE raisenow.participants SET {q} WHERE id = ?",
        (*kwargs.values(), raisenow_id),
    )
    raisenow = await get_raisenow(raisenow_id, req)
    assert raisenow, "Newly updated raisenow couldn't be retrieved"
    return raisenow


async def delete_participant(raisenow_id: str) -> None:
    await db.execute(
        "DELETE FROM raisenow.participants WHERE id = ?", (raisenow_id,)
    )