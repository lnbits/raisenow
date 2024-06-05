from http import HTTPStatus
import json

import httpx
from fastapi import Depends, Query, Request
from lnurl import decode as decode_lnurl
from loguru import logger
from starlette.exceptions import HTTPException

from lnbits.core.crud import get_user
from lnbits.core.models import Payment
from lnbits.core.services import create_invoice
from lnbits.core.views.api import api_payment
from lnbits.decorators import (
    WalletTypeInfo,
    check_admin,
    get_key_type,
    require_admin_key,
    require_invoice_key,
)

from . import raisenow_ext
from .crud import (
    create_raisenow,
    update_raisenow,
    delete_raisenow,
    get_raisenow,
    get_raisenows,
)
from .models import CreateRaiseNowData, CreateParticipantData, Participant, RaiseNow


#######################################
############### RAISES ################
#######################################

## Get all the records belonging to the user

@raisenow_ext.get("/api/v1/ranow", status_code=HTTPStatus.OK)
async def api_raisenows(
    req: Request,
    all_wallets: bool = Query(False),
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    wallet_ids = [wallet.wallet.id]
    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []
    return [
        raisenow.dict() for raisenow in await get_raisenows(wallet_ids, req)
    ]


## Get a single record


@raisenow_ext.get("/api/v1/ranow/{raisenow_id}", status_code=HTTPStatus.OK)
async def api_raisenow(
    req: Request, raisenow_id: str, WalletTypeInfo=Depends(get_key_type)
):
    raisenow = await get_raisenow(raisenow_id, req)
    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )
    return raisenow.dict()


## update a record


@raisenow_ext.put("/api/v1/ranow/{raisenow_id}")
async def api_raisenow_update(
    req: Request,
    data: CreateRaiseNowData,
    raisenow_id: str,
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    if not raisenow_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )
    raisenow = await get_raisenow(raisenow_id, req)
    assert raisenow, "raisenow couldn't be retrieved"

    if wallet.wallet.id != raisenow.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )
    raisenow = await update_raisenow(
        raisenow_id=raisenow_id, **data.dict(), req=req
    )
    return raisenow.dict()


## Create a new record


@raisenow_ext.post("/api/v1/ranow", status_code=HTTPStatus.CREATED)
async def api_raisenow_create(
    req: Request,
    data: CreateRaiseNowData,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    raisenow = await create_raisenow(
        wallet_id=wallet.wallet.id, data=data, req=req
    )
    return raisenow.dict()


## Delete a record


@raisenow_ext.delete("/api/v1/ranow/{raisenow_id}")
async def api_raisenow_delete(
    raisenow_id: str, wallet: WalletTypeInfo = Depends(require_admin_key)
):
    raisenow = await get_raisenow(raisenow_id)

    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )

    if raisenow.wallet != wallet.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )

    await delete_raisenow(raisenow_id)
    return "", HTTPStatus.NO_CONTENT


#######################################
########### Particpants ###############
#######################################

## Get all the records belonging to the user


@raisenow_ext.get("/api/v1/participants", status_code=HTTPStatus.OK)
async def api_raisenows(
    req: Request,
    all_wallets: bool = Query(False),
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    wallet_ids = [wallet.wallet.id]
    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []
    return [
        raisenow.dict() for raisenow in await get_raisenows(wallet_ids, req)
    ]


## Get a single record


@raisenow_ext.get("/api/v1/participants/{raisenow_id}", status_code=HTTPStatus.OK)
async def api_raisenow(
    req: Request, raisenow_id: str, WalletTypeInfo=Depends(get_key_type)
):
    raisenow = await get_raisenow(raisenow_id, req)
    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )
    return raisenow.dict()


## update a record


@raisenow_ext.put("/api/v1/participants/{raisenow_id}")
async def api_raisenow_update(
    req: Request,
    data: CreateRaiseNowData,
    raisenow_id: str,
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    if not raisenow_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )
    raisenow = await get_raisenow(raisenow_id, req)
    assert raisenow, "raisenow couldn't be retrieved"

    if wallet.wallet.id != raisenow.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )
    raisenow = await update_raisenow(
        raisenow_id=raisenow_id, **data.dict(), req=req
    )
    return raisenow.dict()


## Create a new record


@raisenow_ext.post("/api/v1/participants", status_code=HTTPStatus.CREATED)
async def api_raisenow_create(
    req: Request,
    data: CreateRaiseNowData,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    raisenow = await create_raisenow(
        wallet_id=wallet.wallet.id, data=data, req=req
    )
    return raisenow.dict()


## Delete a record


@raisenow_ext.delete("/api/v1/participants/{raisenow_id}")
async def api_raisenow_delete(
    raisenow_id: str, wallet: WalletTypeInfo = Depends(require_admin_key)
):
    raisenow = await get_raisenow(raisenow_id)

    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )

    if raisenow.wallet != wallet.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your raisenow."
        )

    await delete_raisenow(raisenow_id)
    return "", HTTPStatus.NO_CONTENT
