import asyncio
import json

from lnbits.core.models import Payment
from lnbits.core.services import (
    fee_reserve,
    get_pr_from_lnurl,
    pay_invoice,
    websocket_updater,
)
from lnbits.tasks import register_invoice_listener

from .crud import get_participant, get_raisenow, update_participant, update_raisenow


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_raisenow_invoice_listener")

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") != "raisenow":
        return
    if not payment.extra.get("recordId"):
        return
    record_id = payment.extra.get("recordId")
    amount_msat = int(payment.amount)
    safe_amount_msat = amount_msat - fee_reserve(amount_msat)

    participant_record = await get_participant(str(record_id))
    if not participant_record:
        return
    participant_total = int(participant_record.total or 0) + int(safe_amount_msat)
    participant_record.total = participant_total

    raisenow_record = await get_raisenow(participant_record.raisenow)
    if not raisenow_record:
        return
    raisenow_total = int(raisenow_record.total or 0) + int(safe_amount_msat)
    raisenow_record.total = raisenow_total

    memo = (
        f"LNbits raisenow to the raise {raisenow_record.name}"
        f" for {participant_record.name}"
    )
    if not participant_record.lnaddress:
        return
    payment_request = await get_pr_from_lnurl(
        participant_record.lnaddress, safe_amount_msat
    )
    extra = {
        "participant_id": record_id,
        "participant_name": participant_record.name,
        "participant_total": participant_total,
        "raisenow": raisenow_record.id,
        "raisenow_total": raisenow_total,
        "amount": safe_amount_msat,
    }
    if payment_request:
        await pay_invoice(
            payment_request=payment_request,
            wallet_id=payment.wallet_id,
            description=memo,
            extra=extra,
        )
    await update_participant(participant_record)
    await update_raisenow(raisenow_record)
    await websocket_updater(raisenow_record.id, json.dumps(extra))
