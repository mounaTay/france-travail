import logging
import os
from pathlib import Path

import pandas as pd
import requests

FRANCE_TRAVAIL_TOKEN_URL = (
    "https://francetravail.io/connexion/oauth2/access_token?realm=partenaire"
)
FRANCE_TRAVAIL_BASE_OFFER_URL = (
    "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/"
)
FRANCE_TRAVAIL_SEARCH_OFFERS_URL = f"{FRANCE_TRAVAIL_BASE_OFFER_URL}/search"
CLIENT_ID = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")

logger = logging.getLogger(__name__)

if not (CLIENT_ID or CLIENT_SECRET):
    raise RuntimeError("Missing credentials in .env")


def get_auth_header() -> dict:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("CLIENT_ID or CLIENT_SECRET not set")

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "api_offresdemploiv2 o2dsoffre",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(FRANCE_TRAVAIL_TOKEN_URL, data=data, headers=headers)

    response.raise_for_status()
    return {"Authorization": f"Bearer {response.json().get('access_token')}"}


def search_offers():
    query_params = {
        "departement": "07",
        "typeContrat": "CDI",
    }

    response = requests.get(
        FRANCE_TRAVAIL_SEARCH_OFFERS_URL, params=query_params, headers=get_auth_header()
    )

    response.raise_for_status()
    offers = response.json().get("resultats", [])
    if not offers:
        return "No offers found."
    return offers


def save_offers_to_csv(offers: list[dict], folder: Path):
    df = pd.json_normalize(offers)
    if not os.path.exists(folder):
        os.mkdir(folder)
    # offre d'emploi
    df.to_csv(f"{folder}/offres_emploi.csv", index=False, sep="|")

    # entreprises
    df = pd.DataFrame.from_records(offers)
    entreprise = pd.json_normalize(df["entreprise"]).dropna(how="all").drop_duplicates()
    entreprise.to_csv(f"{folder}/entreprises.csv", index=False, sep="|")

    # competences
    competences = df.explode("competences", ignore_index=True)["competences"]
    competences_df = (
        pd.concat([pd.json_normalize(competences)], axis=1)
        .dropna(how="all")
        .drop_duplicates()
    )
    competences_df.to_csv(f"{folder}/competences.csv", sep="|", index=False)


if __name__ == "__main__":
    offers = search_offers()
    save_offers_to_csv(offers, Path("data"))
