"""Géocodage côté pipeline, par le service de la Géoplateforme de l'IGN.

Sert à situer une commune sur la carte. Le site, lui, géocode l'adresse saisie
directement dans le navigateur : ce module ne concerne que les traitements
hors ligne.
"""

from __future__ import annotations

import time

import requests

BASE = "https://data.geopf.fr/geocodage"
#: Le service accepte 50 requêtes par seconde et par adresse IP. On reste loin
#: en dessous : rien ne presse dans un traitement hors ligne.
PAUSE_S = 0.08


def centre_de_la_commune(nom: str, insee: str, *, delai: int = 20) -> tuple[float, float] | None:
    """Coordonnées du centre d'une commune, vérifiées par son code INSEE.

    Renvoie None si le service ne répond pas, ou si le résultat porte un autre
    code INSEE que celui attendu : mieux vaut aucune page qu'une page qui situe
    la commune ailleurs.
    """
    time.sleep(PAUSE_S)
    try:
        reponse = requests.get(
            f"{BASE}/search",
            params={"q": nom, "index": "address", "type": "municipality", "limit": 5},
            timeout=delai,
        )
        reponse.raise_for_status()
        donnees = reponse.json()
    except Exception:  # noqa: BLE001 — une commune manquante n'arrête pas le traitement
        return None

    for element in donnees.get("features", []):
        proprietes = element.get("properties") or {}
        if str(proprietes.get("citycode") or "") != insee:
            continue
        coordonnees = (element.get("geometry") or {}).get("coordinates") or []
        if len(coordonnees) >= 2:
            return float(coordonnees[0]), float(coordonnees[1])
    return None
