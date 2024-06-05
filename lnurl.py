# Maybe your extension needs some LNURL stuff.
# Here is a very simple example of how to do it.
# Feel free to delete this file if you don't need it.

from http import HTTPStatus
from fastapi import Depends, Query, Request
from . import raisenow_ext
from .crud import get_raisenow
from lnbits.core.services import create_invoice, pay_invoice
from loguru import logger
from typing import Optional
from .crud import update_raisenow
from .models import RaiseNow
import shortuuid

#################################################
########### A very simple LNURLpay ##############
# https://github.com/lnurl/luds/blob/luds/06.md #
#################################################
#################################################

# Currently any any amount can be paid, but in the future this will be configurable.

@raisenow_ext.get(
    "/api/v1/lnurl/pay/{raisenow_id}",
    status_code=HTTPStatus.OK,
    name="raisenow.api_lnurl_pay",
)
async def api_lnurl_pay(
    request: Request,
    raisenow_id: Optional[str] = None,
    partipipant_id: Optional[str] = None
):
    if raisenow_id:
        record = await get_raisenow(raisenow_id)
        record_type = "raisenow"
        closing_date = record.closing_date
    elif partipipant_id:
        record = await get_partipipant(partipipant_id)
        record_type = "partipipant"
        raisenow = await get_raisenow(record.raisenow)
        closing_date = raisenow.closing_date
    if not record:
        return {"status": "ERROR", "reason": "No raisenow found"}
    if closing_date < datetime.now():
        return {"status": "ERROR", "reason": "Raise is closed"}
    return {
        "callback": str(
            request.url_for(
                "raisenow.api_lnurl_pay_callback", record_id=record.id, record_type=record_type
            )
        ),
        "maxSendable": 10000,
        "minSendable": 1000000000,
        "metadata": '[["text/plain", "' + record.name + '"]]',
        "tag": "payRequest",
    }


@raisenow_ext.get(
    "/api/v1/lnurl/pay/cb/{record_id}",
    status_code=HTTPStatus.OK,
    name="raisenow.api_lnurl_pay_callback",
)
async def api_lnurl_pay_cb(
    request: Request,
    record_id: str,
    record_type: str,
    amount: int = Query(...),
):
    if record_type == "raisenow":
        record = await get_raisenow(record_id)
    elif record_type == "participant":
        record = await get_participant(record_id)

    if not record:
        return {"status": "ERROR", "reason": "No raisenow found"}

    payment_hash, payment_request = await create_invoice(
        wallet_id=record.wallet,
        amount=int(amount / 1000),
        memo=record.name,
        unhashed_description=f'[["text/plain", "{record.name}"]]'.encode(),
        extra={
            "tag": "raisenow",
            "recordId": record,
            "extra": request.query_params.get("amount"),
        },
    )
    return {
        "pr": payment_request,
        "routes": [],
        "successAction": {"tag": "message", "message": f"Paid {record.name}"},
    }