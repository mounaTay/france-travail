import pytest

from main import save_offers_to_csv, search_offers
import pandas as pd


class TestOffres:
    @pytest.fixture(scope="module")
    def offers(self):
        return [
            {
                "id": "193FKBM",
                "entreprise": {"nom": "WAS", "entrepriseAdaptee": False},
                "competences": [
                    {
                        "code": "100341",
                        "libelle": "Procédures d'encaissement",
                        "exigence": "S",
                    },
                    {
                        "code": "102405",
                        "libelle": "Techniques de mise en rayon",
                        "exigence": "S",
                    },
                    {
                        "code": "300375",
                        "libelle": "Organiser, aménager un espace de vente",
                        "exigence": "S",
                    },
                    {
                        "code": "300374",
                        "libelle": "Présenter et valoriser un produit ou un service",
                        "exigence": "E",
                    },
                ],
            }
        ]

    def test_basic_search(self):
        response = search_offers()
        assert len(response) > 0

    def test_save_entreprises_info_to_csv(self, offers, tmp_path):
        file = tmp_path / "entreprises.csv"
        save_offers_to_csv(offers, tmp_path)

        df = pd.read_csv(file, sep="|")
        assert "nom" in df.columns
        assert df.iloc[0]["nom"] == "WAS"

    def test_save_competences_info_to_csv(self, offers, tmp_path):
        file = tmp_path / "competences.csv"
        save_offers_to_csv(offers, tmp_path)

        df = pd.read_csv(file, sep="|")
        assert "code" in df.columns
        assert df.iloc[0]["code"] == 100341

    def test_save_offre_d_emploi_to_csv(self, offers, tmp_path):
        file = tmp_path / "offres_emploi.csv"
        save_offers_to_csv(offers, tmp_path)

        df = pd.read_csv(file, sep="|")
        assert "id" in df.columns
        assert df.iloc[0]["id"] == "193FKBM"
