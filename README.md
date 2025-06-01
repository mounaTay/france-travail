# France Travail

Recherche des offres en CDI du departement 07 sur l'API France Travail

## Fonctionnalités

- Recherche d’offres CDI du departement 07
- Tests unitaires avec `pytest`
- Intégration continue via GitHub Actions

---

## Setup

### Prérequis

- Un client id et un client secret disponible sur [France Travail](https://francetravail.io/compte/applications/11752),
  puis les renseigner dans le fichier [.env](.env)
- [docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)

### Installation

Clonez le dépôt :

```bash
git clone https://github.com/mounaTay/france-travail.git
cd france-travail
docker compose up
```

Une fois le job terminé, les fichiers sont trouvés dans le dossier [data](data).

3 fichiers sont générés:

1. [Competences](data/competences.csv): contient les informations des competences requises sur les offres
2. [Entreprises](data/entreprises.csv): contient les details des entreprises
3. [offres d'emploi](data/offres_emploi.csv): contient la liste des offres CDI du departement 07
