from http import HTTPStatus

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse

from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.settings import settings

from . import raisenow_ext, raisenow_renderer
from .crud import get_raisenow

ranow = Jinja2Templates(directory="ranow")


#######################################
##### ADD YOUR PAGE ENDPOINTS HERE ####
#######################################


# Backend admin page


@raisenow_ext.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return raisenow_renderer().TemplateResponse(
        "raisenow/index.html", {"request": request, "user": user.dict()}
    )


# Frontend shareable page


@raisenow_ext.get("/{raisenow_id}")
async def raisenow(request: Request, raisenow_id):
    raisenow = await get_raisenow(raisenow_id, request)
    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )
    return raisenow_renderer().TemplateResponse(
        "raisenow/raisenow.html",
        {
            "request": request,
            "raisenow_id": raisenow_id,
            "lnurlpay": raisenow.lnurlpay,
            "web_manifest": f"/raisenow/manifest/{raisenow_id}.webmanifest",
        },
    )


# Manifest for public page, customise or remove manifest completely


@raisenow_ext.get("/manifest/{raisenow_id}.webmanifest")
async def manifest(raisenow_id: str):
    raisenow = await get_raisenow(raisenow_id)
    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )

    return {
        "short_name": settings.lnbits_site_title,
        "name": raisenow.name + " - " + settings.lnbits_site_title,
        "icons": [
            {
                "src": settings.lnbits_custom_logo
                if settings.lnbits_custom_logo
                else "https://cdn.jsdelivr.net/gh/lnbits/lnbits@0.3.0/docs/logos/lnbits.png",
                "type": "image/png",
                "sizes": "900x900",
            }
        ],
        "start_url": "/raisenow/" + raisenow_id,
        "background_color": "#1F2234",
        "description": "Minimal extension to build on",
        "display": "standalone",
        "scope": "/raisenow/" + raisenow_id,
        "theme_color": "#1F2234",
        "shortcuts": [
            {
                "name": raisenow.name + " - " + settings.lnbits_site_title,
                "short_name": raisenow.name,
                "description": raisenow.name + " - " + settings.lnbits_site_title,
                "url": "/raisenow/" + raisenow_id,
            }
        ],
    }
