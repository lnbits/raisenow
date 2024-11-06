import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db
from .tasks import wait_for_paid_invoices
from .views import raisenow_generic_router
from .views_api import raisenow_api_router
from .lnurl import raisenow_lnurl_router

raisenow_ext: APIRouter = APIRouter(prefix="/raisenow", tags=["raisenow"])
raisenow_ext.include_router(raisenow_generic_router)
raisenow_ext.include_router(raisenow_api_router)
raisenow_ext.include_router(raisenow_lnurl_router)

raisenow_static_files = [
    {
        "path": "/raisenow/static",
        "name": "raisenow_static",
    }
]


scheduled_tasks: list[asyncio.Task] = []


def raisenow_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def raisenow_start():
    task = create_permanent_unique_task("ext_raisenow", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = ["db", "raisenow_ext", "raisenow_static_files"]
