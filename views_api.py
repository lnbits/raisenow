from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from lnbits.core.crud import get_user
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import require_admin_key, require_invoice_key
from loguru import logger

from .crud import (
    create_participant,
    create_raisenow,
    delete_participant,
    delete_raisenow,
    get_participant,
    get_participants,
    get_raisenow,
    get_raisenows,
    update_participant,
    update_raisenow,
)
from .models import CreateParticipantData, CreateRaiseNowData, RaiseNow

raisenow_api_router = APIRouter()

#######################################
############### RAISES ################
#######################################

## Get all the records belonging to the user


@raisenow_api_router.get("/api/v1/ranow", status_code=HTTPStatus.OK)
async def api_raisenows(
    all_wallets: bool = Query(False),
    key_info: WalletTypeInfo = Depends(require_invoice_key),
):
    wallet_ids = [key_info.wallet.id]
    if all_wallets:
        user = await get_user(key_info.wallet.user)
        wallet_ids = user.wallet_ids if user else []
    return [raisenow.dict() for raisenow in await get_raisenows(wallet_ids)]


## Get a single record


@raisenow_api_router.get("/api/v1/ranow/{raisenow_id}", status_code=HTTPStatus.OK)
async def api_raisenow(
    req: Request,
    raisenow_id: str,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
):
    raisenow = await get_raisenow(raisenow_id, req)
    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )
    return raisenow.dict()


## update a record


@raisenow_api_router.put("/api/v1/ranow", status_code=HTTPStatus.OK)
async def api_raisenow_update(
    data: RaiseNow,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
):
    if key_info.wallet.id != data.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )
    return await update_raisenow(data)


## Create a new record


@raisenow_api_router.post("/api/v1/ranow", status_code=HTTPStatus.CREATED)
async def api_raisenow_create(
    req: Request,
    data: CreateRaiseNowData,
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    raisenow = await create_raisenow(wallet_id=key_info.wallet.id, data=data, req=req)
    return raisenow.dict()


## Delete a record


@raisenow_api_router.delete("/api/v1/ranow/{raisenow_id}", status_code=HTTPStatus.OK)
async def api_raisenow_delete(
    raisenow_id: str, key_info: WalletTypeInfo = Depends(require_admin_key)
):
    raisenow = await get_raisenow(raisenow_id)

    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )

    if raisenow.wallet != key_info.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )

    await delete_raisenow(raisenow_id)
    return "", HTTPStatus.NO_CONTENT


#######################################
########### Particpants ###############
#######################################

## Get all the records belonging to the user


@raisenow_api_router.get(
    "/api/v1/participants/{raisenow_id}", status_code=HTTPStatus.OK
)
async def api_participants(req: Request, raisenow_id: str):
    participants = await get_participants(raisenow_id, req)
    if not participants:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="participant does not exist."
        )
    return [
        participant.dict() for participant in await get_participants(raisenow_id, req)
    ]


## Get a single record


@raisenow_api_router.get(
    "/api/v1/participant/{participant_id}", status_code=HTTPStatus.OK
)
async def api_participant(
    req: Request,
    participant_id: str,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
):
    participant = await get_participant(participant_id, req)
    if not participant:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="participant does not exist."
        )
    return participant.dict()


## update a record


@raisenow_api_router.put(
    "/api/v1/participant/{participant_id}", status_code=HTTPStatus.OK
)
async def api_participant_update(
    req: Request,
    data: CreateParticipantData,
    participant_id: str,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
):
    if not participant_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="participant does not exist."
        )
    participant = await get_participant(participant_id, req)
    assert participant, "participant couldn't be retrieved"

    raisenow = await get_raisenow(participant.raisenow, req)
    assert raisenow, "raisenow couldn't be retrieved"

    if key_info.wallet.id != raisenow.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )
    logger.debug(data.dict())
    participant = await update_participant(
        participant_id=participant_id, **data.dict(), req=req
    )
    return participant.dict()


## Create a new record


@raisenow_api_router.post("/api/v1/participant", status_code=HTTPStatus.CREATED)
async def api_participant_create(
    req: Request,
    data: CreateParticipantData,
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    participant = await create_participant(
        wallet_id=key_info.wallet.id, data=data, req=req
    )
    return participant.dict()


## Delete a record


@raisenow_api_router.delete(
    "/api/v1/participant/{participant_id}", status_code=HTTPStatus.OK
)
async def api_participant_delete(
    req: Request,
    participant_id: str,
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    participant = await get_participant(participant_id)
    logger.debug(participant)
    if not participant:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="participant does not exist."
        )
    raisenow = await get_raisenow(participant.raisenow, req)
    assert raisenow, "raisenow couldn't be retrieved"

    if raisenow.wallet != key_info.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )

    await delete_participant(participant_id)
    return "", HTTPStatus.NO_CONTENT
