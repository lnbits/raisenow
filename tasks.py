import asyncio

from loguru import logger

from lnbits.core.models import Payment
from lnbits.core.services import create_invoice, websocket_updater
from lnbits.helpers import get_current_extension_name
from lnbits.tasks import register_invoice_listener

from .crud import get_raisenow, update_raisenow


#######################################
########## RUN YOUR TASKS HERE ########
#######################################

# The usual task is to listen to invoices related to this extension


async def wait_for_paid_invoices():
    logger.debug(get_current_extension_name())
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, get_current_extension_name())
    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


# Do somethhing when an invoice related top this extension is paid


async def on_invoice_paid(payment: Payment) -> None:
    logger.debug("payment received for raisenow extension")
    if payment.extra.get("tag") != "raisenow":
        return

    raisenow_id = payment.extra.get("recordId")
    raisenow = await get_raisenow(raisenow_id)
    if not raisenow:
        logger.error(f"Could not find raisenow {raisenow_id}")
        return

    # update something in the db
    total = raisenow.total + payment.amount
    data_to_update = {"total": total}

    await update_raisenow(raisenow_id=raisenow_id, **data_to_update)

    # Here we send the payment data to the front end via websocket, for use on frontend or wherever

    some_payment_data = {
        "name": raisenow.name,
        "amount": payment.amount,
        "fee": payment.fee,
        "checking_id": payment.checking_id,
    }

    await websocket_updater(raisenow_id, str(some_payment_data))
