from typing import List, Optional, Union

from fastapi import Request
from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import CreateParticipantData, CreateRaiseNowData, Participant, RaiseNow

db = Database("ext_raisenow")


async def create_raisenow(
    wallet_id: str, data: CreateRaiseNowData, req: Request
) -> CreateRaiseNowData:
    raisenow_id = urlsafe_short_hash()
    raisenow = CreateRaiseNowData(**data.dict(), wallet_id=wallet_id, id=raisenow_id)
    await db.insert("raisenow.raises", raisenow)
    return await get_raisenow(raisenow_id, req)


async def get_raisenow(raisenow_id: str) -> Optional[RaiseNow]:
    return await db.fetchone(
        "SELECT * FROM raisenow.raises WHERE id = :id",
        {"id": raisenow_id},
        RaiseNow,
    )


async def get_raisenows(wallet_ids: Union[str, List[str]]) -> List[RaiseNow]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]
    q = ",".join([f"'{wallet_id}'" for wallet_id in wallet_ids])
    return await db.fetchall(
        f"SELECT * FROM raisenow.raises WHERE wallet IN ({q}) ORDER BY id",
        model=RaiseNow,
    )


async def update_raisenow(raisenow: RaiseNow) -> RaiseNow:
    await db.update("raisenow.raises", raisenow)
    return raisenow


async def delete_raisenow(raisenow_id: str) -> None:
    await db.execute("DELETE FROM raisenow.raises WHERE id = :id", {"id": raisenow_id})


#######################################
########### Particpants ###############
#######################################


async def create_participant(
    wallet_id: str, data: CreateParticipantData, req: Request
) -> CreateParticipantData:
    participant_id = urlsafe_short_hash()
    participant = CreateParticipantData(
        **data.dict(), wallet_id=wallet_id, id=participant_id
    )
    await db.insert("raisenow.participants", participant)
    return await get_participant(participant_id, req)


async def get_participant(participant_id: str) -> Optional[Participant]:
    return await db.fetchone(
        "SELECT * FROM raisenow.participants WHERE id = :id",
        {"id": participant_id},
        Participant,
    )


async def get_participants(raisenow_id: str) -> List[RaiseNow]:
    return await db.fetchall(
        """
        SELECT * FROM raisenow.participants
        WHERE raisenow = :raisenow ORDER BY
        total DESC, name ASC
        """,
        {"raisenow": raisenow_id},
    )


async def update_participant(participant: Participant) -> Participant:
    await db.update("raisenow.participants", participant)
    return participant


async def delete_participant(participant_id: str) -> None:
    await db.execute(
        "DELETE FROM raisenow.participants WHERE id = :id", {"id": participant_id}
    )
