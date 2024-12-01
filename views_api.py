from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
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
from .helpers import lnurler
from .models import CreateParticipantData, CreateRaiseNowData, Participant, RaiseNow

raisenow_api_router = APIRouter()

#######################################
############### RAISES ################
#######################################

## Get all the records belonging to the user


@raisenow_api_router.get("/api/v1/ranow", status_code=HTTPStatus.OK)
async def api_raisenows(
    req: Request,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
):
    user = await get_user(key_info.wallet.user)
    wallet_ids = user.wallet_ids if user else []
    raisenows = await get_raisenows(wallet_ids)
    for raisenow in raisenows:
        raisenow.lnurlpay = lnurler(raisenow.id, "raisenow.api_lnurl_pay", req)
    return raisenows


## Get a single record


@raisenow_api_router.get(
    "/api/v1/ranow/{raisenow_id}",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(require_invoice_key)],
)
async def api_raisenow(req: Request, raisenow_id: str):
    raisenow = await get_raisenow(raisenow_id)
    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )
    raisenow.lnurlpay = lnurler(raisenow.id, "raisenow.api_lnurl_pay", req)
    return raisenow


## update a record


@raisenow_api_router.put("/api/v1/ranow", status_code=HTTPStatus.OK)
async def api_raisenow_update(
    req: Request,
    data: RaiseNow,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
):
    if key_info.wallet.id != data.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )
    raisenow = await update_raisenow(data)
    raisenow.lnurlpay = lnurler(raisenow.id, "raisenow.api_lnurl_pay", req)
    return raisenow


## Create a new record


@raisenow_api_router.post(
    "/api/v1/ranow",
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(require_invoice_key)],
)
async def api_raisenow_create(req: Request, data: CreateRaiseNowData):
    raisenow = await create_raisenow(data)
    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Could not create raisenow."
        )
    raisenow.lnurlpay = lnurler(raisenow.id, "raisenow.api_lnurl_pay", req)
    return raisenow


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
    participants = await get_participants(raisenow_id)
    if not participants:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="participant does not exist."
        )
    for participant in participants:
        participant.lnurlpay = lnurler(participant.id, "raisenow.api_lnurl_pay", req)
    return participants


## Get a single record


@raisenow_api_router.get(
    "/api/v1/participant/{participant_id}",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(require_invoice_key)],
)
async def api_participant(req: Request, participant_id: str):
    participant = await get_participant(participant_id)
    if not participant:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="participant does not exist."
        )
    participant.lnurlpay = lnurler(participant.id, "raisenow.api_lnurl_pay", req)
    return participant


## update a record


@raisenow_api_router.put(
    "/api/v1/participant/{participant_id}", status_code=HTTPStatus.OK
)
async def api_participant_update(
    req: Request,
    data: Participant,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
):
    participant = await get_participant(data.id)
    assert participant, "participant couldn't be retrieved"

    raisenow = await get_raisenow(participant.raisenow)
    assert raisenow, "raisenow couldn't be retrieved"

    if key_info.wallet.id != raisenow.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )
    participant = await update_participant(data)
    if not participant:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Could not update participants."
        )
    participant.lnurlpay = lnurler(participant.id, "raisenow.api_lnurl_pay", req)
    return participant


## Create a new record


@raisenow_api_router.post(
    "/api/v1/participant",
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(require_invoice_key)],
)
async def api_participant_create(req: Request, data: CreateParticipantData):
    participant = await create_participant(data)
    if not participant:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Could not create participant."
        )
    participant.lnurlpay = lnurler(participant.id, "raisenow.api_lnurl_pay", req)
    return participant


## Delete a record


@raisenow_api_router.delete(
    "/api/v1/participant/{participant_id}", status_code=HTTPStatus.OK
)
async def api_participant_delete(
    participant_id: str,
    key_info: WalletTypeInfo = Depends(require_admin_key),
):
    participant = await get_participant(participant_id)
    logger.debug(participant)
    if not participant:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="participant does not exist."
        )
    raisenow = await get_raisenow(participant.raisenow)
    assert raisenow, "raisenow couldn't be retrieved"

    if raisenow.wallet != key_info.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )

    await delete_participant(participant_id)
    return "", HTTPStatus.NO_CONTENT
