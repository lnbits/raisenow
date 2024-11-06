import json
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer
from lnbits.settings import settings

from .crud import get_participants, get_raisenow

raisenow_generic_router: APIRouter = APIRouter()


def raisenow_renderer():
    return template_renderer(["raisenow/templates"])


#######################################
##### ADD YOUR PAGE ENDPOINTS HERE ####
#######################################

# Backend admin page


@raisenow_generic_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: User = Depends(check_user_exists)):
    return raisenow_renderer().TemplateResponse(
        "raisenow/index.html", {"request": request, "user": user.json()}
    )


# Frontend shareable page


@raisenow_generic_router.get("/{raisenow_id}")
async def raisenow(request: Request, raisenow_id):
    raisenow = await get_raisenow(raisenow_id)
    if not raisenow:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="raisenow does not exist."
        )
    participants = await get_participants(raisenow_id)
    if not participants:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No participants found."
        )
    return raisenow_renderer().TemplateResponse(
        "raisenow/raisenow.html",
        {
            "request": request,
            "raisenow_id": raisenow_id,
            "header_image": raisenow.header_image,
            "background_image": raisenow.background_image,
            "participants": json.dumps([dict(p) for p in participants]),
            "lnurlpay": raisenow.lnurlpay,
            "web_manifest": f"/raisenow/manifest/{raisenow_id}.webmanifest",
        },
    )


# Manifest for public page, customise or remove manifest completely


@raisenow_generic_router.get("/manifest/{raisenow_id}.webmanifest")
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
                "src": (
                    settings.lnbits_custom_logo
                    if settings.lnbits_custom_logo
                    else "https://cdn.jsdelivr.net/gh/lnbits/lnbits@0.3.0/docs/logos/lnbits.png"
                ),
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
