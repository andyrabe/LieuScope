"""Découpage en tuiles XYZ, identique à celui du site (src/lib/verdict/tiles.ts)."""

from __future__ import annotations

import math
from dataclasses import dataclass

#: Zoom fixe de la couche des zones climatiques locales.
ZOOM_LCZ = 14


@dataclass(frozen=True)
class Tuile:
    z: int
    x: int
    y: int

    @property
    def chemin(self) -> str:
        return f"{self.z}/{self.x}/{self.y}.json"


def nombre_de_tuiles(z: int) -> int:
    return 2**z


def tuile_du_point(lon: float, lat: float, z: int) -> Tuile:
    """Tuile qui contient un point, en WGS84."""
    n = nombre_de_tuiles(z)
    lat = min(max(lat, -85.05112878), 85.05112878)
    x_norm = ((lon + 180.0) % 360.0) / 360.0
    lat_rad = math.radians(lat)
    y_norm = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0
    x = min(max(int(x_norm * n), 0), n - 1)
    y = min(max(int(y_norm * n), 0), n - 1)
    return Tuile(z, x, y)


def emprise_tuile(tuile: Tuile) -> tuple[float, float, float, float]:
    """Emprise d'une tuile : (ouest, sud, est, nord)."""
    n = nombre_de_tuiles(tuile.z)
    ouest = tuile.x / n * 360.0 - 180.0
    est = (tuile.x + 1) / n * 360.0 - 180.0
    nord = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * tuile.y / n))))
    sud = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (tuile.y + 1) / n))))
    return ouest, sud, est, nord


def tuiles_de_l_emprise(
    ouest: float, sud: float, est: float, nord: float, z: int
) -> list[Tuile]:
    """Toutes les tuiles touchées par une emprise."""
    coin_nord_ouest = tuile_du_point(ouest, nord, z)
    coin_sud_est = tuile_du_point(est, sud, z)
    return [
        Tuile(z, x, y)
        for x in range(coin_nord_ouest.x, coin_sud_est.x + 1)
        for y in range(coin_nord_ouest.y, coin_sud_est.y + 1)
    ]
