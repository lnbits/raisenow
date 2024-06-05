import asyncio

from fastapi import APIRouter

from lnbits.db import Database
from lnbits.helpers import template_renderer
from lnbits.tasks import catch_everything_and_restart


db = Database("ext_raisenow")

raisenow_ext: APIRouter = APIRouter(
    prefix="/raisenow", tags=["raisenow"]
)

raisenow_static_files = [
    {
        "path": "/raisenow/static",
        "name": "raisenow_static",
    }
]


def raisenow_renderer():
    return template_renderer(["raisenow/templates"])


from .lnurl import *
from .tasks import wait_for_paid_invoices
from .views import *
from .views_api import *


def raisenow_start():
    loop = asyncio.get_event_loop()
    loop.create_task(catch_everything_and_restart(wait_for_paid_invoices))
