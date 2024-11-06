from datetime import datetime
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Query, Request
from lnbits.core.services import create_invoice

from .crud import get_participant, get_raisenow

raisenow_lnurl_router: APIRouter = APIRouter()


@raisenow_lnurl_router.get(
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
        live_dates = raisenow_record.live_dates.split(",")
        start_date = datetime.strptime(live_dates[0], "%Y/%m/%d").date()
        end_date = datetime.strptime(live_dates[1], "%Y/%m/%d").date()
        current_date = datetime.now().date()
        if not start_date <= current_date <= end_date:
            return {"status": "ERROR", "reason": "The raise is not live."}

    return {
        "callback": str(
            request.url_for("raisenow.api_lnurl_pay_callback", record_id=record_id)
        ),
        "maxSendable": 1000000000,
        "minSendable": 10000,
        "metadata": '[["text/plain", "' + record.name + '"]]',
        "tag": "payRequest",
    }


@raisenow_lnurl_router.get(
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

    payment = await create_invoice(
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
        "pr": payment.bolt11,
        "routes": [],
        "successAction": {
            "tag": "message",
            "message": f"Paid {participant_record.name}",
        },
    }
