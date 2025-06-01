import hashlib
import json
import logging
import os
from typing import Optional

import httpx
from aiocache import cached, Cache
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from httpx import AsyncClient

load_dotenv()

FRANCE_TRAVAIL_TOKEN_URL = "https://francetravail.io/connexion/oauth2/access_token?realm=partenaire"
FRANCE_TRAVAIL_BASE_OFFER_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/"
FRANCE_TRAVAIL_SEARCH_OFFERS_URL = f"{FRANCE_TRAVAIL_BASE_OFFER_URL}/search"
CLIENT_ID = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")

logger = logging.getLogger(__name__)

if not (CLIENT_ID or CLIENT_SECRET):
    raise RuntimeError("Missing credentials in .env")

app = FastAPI(title="France Travail Job Search API", version="1.0")


async def get_auth_header() -> dict:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("CLIENT_ID or CLIENT_SECRET not set")

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "api_offresdemploiv2 o2dsoffre"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with (httpx.AsyncClient() as client):
        response = await client.post(FRANCE_TRAVAIL_TOKEN_URL, data=data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch access token")

        return {"Authorization": f"Bearer {response.json().get("access_token")}"}


def compute_cache_key(params: dict) -> str:
    key_string = json.dumps(params, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


@app.get("/offres", summary="Rechercher des offres d'emploi", tags=["Offres d'emploi"])
@cached(ttl=600, cache=Cache.MEMORY, key_builder=lambda *args, **kwargs: compute_cache_key(
    {k: v for k, v in kwargs.items() if k != 'headers' and v is not None}))
async def search_offers(
        accesTravailleurHandicape: Optional[bool] = Query(None),
        appellation: Optional[str] = Query(None),
        codeNAF: Optional[str] = Query(None),
        codeROME: Optional[str] = Query(None),
        commune: Optional[str] = Query(None),
        departement: Optional[str] = Query(None),
        distance: Optional[int] = Query(None),
        domaine: Optional[str] = Query(None),
        dureeContratMax: Optional[str] = Query(None),
        dureeContratMin: Optional[str] = Query(None),
        dureeHebdo: Optional[str] = Query(None),
        dureeHebdoMax: Optional[str] = Query(None),
        dureeHebdoMin: Optional[str] = Query(None),
        entreprisesAdaptees: Optional[bool] = Query(None),
        experience: Optional[str] = Query(None),
        experienceExigence: Optional[str] = Query(None),
        grandDomaine: Optional[str] = Query(None),
        inclureLimitrophes: Optional[bool] = Query(None),
        maxCreationDate: Optional[str] = Query(None),
        minCreationDate: Optional[str] = Query(None),
        modeSelectionPartenaires: Optional[str] = Query(None),
        motsCles: Optional[str] = Query(None),
        natureContrat: Optional[str] = Query(None),
        niveauFormation: Optional[str] = Query(None),
        offresMRS: Optional[bool] = Query(None),
        offresManqueCandidats: Optional[bool] = Query(None),
        origineOffre: Optional[int] = Query(None),
        partenaires: Optional[str] = Query(None),
        paysContinent: Optional[str] = Query(None),
        periodeSalaire: Optional[str] = Query(None),
        permis: Optional[str] = Query(None),
        publieeDepuis: Optional[int] = Query(None),
        qualification: Optional[str] = Query(None),
        range: Optional[str] = Query(None),
        region: Optional[str] = Query(None),
        salaireMin: Optional[str] = Query(None),
        secteurActivite: Optional[str] = Query(None),
        sort: Optional[int] = Query(1),
        tempsPlein: Optional[bool] = Query(None),
        theme: Optional[str] = Query(None),
        typeContrat: Optional[str] = Query(None),
        headers=Depends(get_auth_header),
):
    query_params = {
        "accesTravailleurHandicape": accesTravailleurHandicape,
        "appellation": appellation,
        "codeNAF": codeNAF,
        "codeROME": codeROME,
        "commune": commune,
        "departement": departement,
        "distance": distance,
        "domaine": domaine,
        "dureeContratMax": dureeContratMax,
        "dureeContratMin": dureeContratMin,
        "dureeHebdo": dureeHebdo,
        "dureeHebdoMax": dureeHebdoMax,
        "dureeHebdoMin": dureeHebdoMin,
        "entreprisesAdaptees": entreprisesAdaptees,
        "experience": experience,
        "experienceExigence": experienceExigence,
        "grandDomaine": grandDomaine,
        "inclureLimitrophes": inclureLimitrophes,
        "maxCreationDate": maxCreationDate,
        "minCreationDate": minCreationDate,
        "modeSelectionPartenaires": modeSelectionPartenaires,
        "motsCles": motsCles,
        "natureContrat": natureContrat,
        "niveauFormation": niveauFormation,
        "offresMRS": offresMRS,
        "offresManqueCandidats": offresManqueCandidats,
        "origineOffre": origineOffre,
        "partenaires": partenaires,
        "paysContinent": paysContinent,
        "periodeSalaire": periodeSalaire,
        "permis": permis,
        "publieeDepuis": publieeDepuis,
        "qualification": qualification,
        "region": region,
        "salaireMin": salaireMin,
        "secteurActivite": secteurActivite,
        "sort": sort,
        "tempsPlein": tempsPlein,
        "theme": theme,
        "typeContrat": typeContrat,
        "range": range,
    }

    filtered_params = {k: v for k, v in query_params.items() if v is not None}

    async with AsyncClient() as client:
        response = await client.get(FRANCE_TRAVAIL_SEARCH_OFFERS_URL, params=filtered_params, headers=headers)

    if response.status_code in (200, 206):
        content = response.json()
        content_range = response.headers.get("Content-Range")

        if content_range:
            try:
                _, range_part = content_range.split(" ")
                range_values, total = range_part.split("/")
                start, end = map(int, range_values.split("-"))
                total = int(total)
                return {
                    "data": content,
                    "pagination": {
                        "start": start,
                        "end": end,
                        "total": total
                    }
                }
            except Exception:
                logger.warning(f"Could not parse Content-Range: {content_range}")

        return content
    elif response.status_code == 204:
        return JSONResponse(content={"message": response.json()["message"]}, status_code=204)
    elif response.status_code == 400:
        raise HTTPException(status_code=400, detail=response.json()["message"])
    elif response.status_code == 500:
        raise HTTPException(status_code=500, detail=response.json()["message"])
    else:
        logger.warning(f"Unhandled France Travail status code: {response.status_code}")
        raise HTTPException(status_code=response.status_code, detail=response.json()["message"])


@app.get("/offres/{id}", summary="Récupérer le détail d'une offre à partir de son identifiant.",
         tags=["Offres d'emploi"])
@cached(ttl=600, cache=Cache.MEMORY, key_builder=lambda *args, **kwargs: compute_cache_key(
    {k: v for k, v in kwargs.items() if k != 'headers' and v is not None}))
async def get_offer_by_id(id: str = Path(..., description="Identifiant de l'offre d'emploi."),
                          headers=Depends(get_auth_header)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{FRANCE_TRAVAIL_BASE_OFFER_URL}/{id}", headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request failed: {e}")

    return JSONResponse(status_code=response.status_code, content=response.json())
