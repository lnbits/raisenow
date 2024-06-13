import asyncio
import json
from loguru import logger
from math import floor
from typing import Optional
import httpx

from lnbits import bolt11
from lnbits.core.models import Payment
from lnbits.core.crud import get_standalone_payment
from lnbits.core.models import Payment

from lnbits.core.services import create_invoice, websocket_updater, fee_reserve, pay_invoice
from lnbits.helpers import get_current_extension_name
from lnbits.tasks import register_invoice_listener
from lnbits.core.views.api import api_lnurlscan

from .crud import get_raisenow, update_raisenow, get_participant, update_participant


async def wait_for_paid_invoices():
    logger.debug(get_current_extension_name())
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, get_current_extension_name())
    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:

    if payment.extra.get("tag") == "raisenow_sent":
        await websocket_updater(payment.extra.get("raisenow"), str(payment.extra))

    if payment.extra.get("tag") != "raisenow":
        return

    record_id = payment.extra.get("recordId")

    amount_msat = int(payment.amount)
    safe_amount_msat = amount_msat - fee_reserve(amount_msat)

    participant_record = await get_participant(record_id)
    logger.debug(participant_record)
    participant_total = int(participant_record.total or 0) + int(safe_amount_msat)
    participant_data_to_update = {"total": participant_total}

    raisenow_record = await get_raisenow(participant_record.raisenow)
    raisenow_total = int(raisenow_record.total or 0) + int(safe_amount_msat)
    raisenow_data_to_update = {"total": raisenow_total}

    memo = f"LNbits raisenow to the raise {raisenow_record.name} for {participant_record.name}"
    payment_request = await get_lnurl_invoice(
        participant_record.lnaddress, payment.wallet_id, safe_amount_msat, memo
    )
    extra = {
        "tag": "raisenow_sent",
        "participant": record_id,
        "participant_total": participant_total,
        "raisenow": raisenow_record.id,
        "raisenow_total": raisenow_total,
    }
    if payment_request:
        await pay_invoice(
            payment_request=payment_request,
            wallet_id=payment.wallet_id,
            description=memo,
            extra=extra,
        )
    await update_participant(participant_id=record_id, **participant_data_to_update)
    await update_raisenow(raisenow_id=raisenow_record.id, **raisenow_data_to_update)


async def get_lnurl_invoice(
    lnaddress, wallet_id, amount_msat, memo
) -> Optional[str]:

    from lnbits.core.views.api import api_lnurlscan

    data = await api_lnurlscan(lnaddress)
    rounded_amount = floor(amount_msat / 1000) * 1000

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                data["callback"],
                params={"amount": rounded_amount, "comment": memo},
                timeout=40,
            )
            if r.is_error:
                raise httpx.ConnectError("issue with scrub callback")
            r.raise_for_status()
        except (httpx.ConnectError, httpx.RequestError):
            logger.error(
                f"splitting LNURL failed: Failed to connect to {data['callback']}."
            )
            return None
        except Exception as exc:
            logger.error(f"splitting LNURL failed: {str(exc)}.")
            return None

    params = json.loads(r.text)
    if params.get("status") == "ERROR":
        logger.error(f"{data['callback']} said: '{params.get('reason', '')}'")
        return None

    invoice = bolt11.decode(params["pr"])

    lnurlp_payment = await get_standalone_payment(invoice.payment_hash)

    if lnurlp_payment and lnurlp_payment.wallet_id == wallet_id:
        logger.error(f"split failed. cannot split payments to yourself via LNURL.")
        return None

    if invoice.amount_msat != rounded_amount:
        logger.error(
            f"{data['callback']} returned an invalid invoice. Expected {amount_msat} msat, got {invoice.amount_msat}."
        )
        return None

    return params["pr"]
