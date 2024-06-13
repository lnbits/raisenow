# Maybe your extension needs some LNURL stuff.
# Here is a very simple example of how to do it.
# Feel free to delete this file if you don't need it.

from http import HTTPStatus
from fastapi import Depends, Query, Request
from . import raisenow_ext
from .crud import get_raisenow, get_participant
from lnbits.core.services import create_invoice, pay_invoice
from loguru import logger
from typing import Optional
from .crud import update_raisenow
from .models import RaiseNow
import shortuuid
from datetime import datetime

#################################################
########### A very simple LNURLpay ##############
# https://github.com/lnurl/luds/blob/luds/06.md #
#################################################
#################################################

# Currently any any amount can be paid, but in the future this will be configurable.

@raisenow_ext.get(
    "/api/v1/lnurl/pay/{record_id}",
    status_code=HTTPStatus.OK,
    name="raisenow.api_lnurl_pay",
)
async def api_lnurl_pay(
    request: Request,
    record_id: Optional[str] = None,
):
    record = await get_participant(record_id)
    raisenow_record = await get_raisenow(record.raisenow)

    if raisenow_record.live_dates:
        live_dates = raisenow_record.live_dates.split(',')
        start_date = datetime.strptime(live_dates[0], "%Y/%m/%d").date()
        end_date = datetime.strptime(live_dates[1], "%Y/%m/%d").date()

        current_date = datetime.now().date()

        if not start_date <= current_date <= end_date:
            return {"status": "ERROR", "reason": "The raise is not live."}

    return {
        "callback": str(
            request.url_for(
                "raisenow.api_lnurl_pay_callback", record_id=record_id
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
    amount: int = Query(...),
):
    participant_record = await get_participant(record_id)
    raisenow_record = await get_raisenow(participant_record.raisenow)

    payment_hash, payment_request = await create_invoice(
        wallet_id=raisenow_record.wallet,
        amount=int(amount / 1000),
        memo=participant_record.name,
        unhashed_description=f'[["text/plain", "{participant_record.name}"]]'.encode(),
        extra={
            "tag": "raisenow",
            "recordId": participant_record.id,
            "extra": request.query_params.get("amount"),
        },
    )
    return {
        "pr": payment_request,
        "routes": [],
        "successAction": {"tag": "message", "message": f"Paid {participant_record.name}"},
    }