"""Prepara los datos de "Pisos Madrid" a partir de idealista18 (Madrid_Sale, ODbL 1.0).

Genera en data/:
  - pisos.csv               todos los pisos limpios (unos 75.000), con la columna publicado_en
  - pisos_muestra_5000.csv  5.000 pisos del histórico, para importar en directo
  - LICENSE                 texto de la ODbL 1.0 del repositorio original

Uso (desde la raíz del repo):
  python -m venv .venv && .venv/bin/pip install -r scripts/requirements-datos.txt
  .venv/bin/python scripts/preparar_datos.py

Los ficheros originales se descargan de un commit fijo del repositorio
paezha/idealista18 a una carpeta temporal; no se guardan en el repo.
"""

from __future__ import annotations

import argparse
import tempfile
import urllib.request
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import rdata
from shapely import STRtree
from shapely.geometry import MultiPolygon, Point, Polygon

COMMIT = "e9ef80618f8a9cc28f672ac138f298bbd519918e"
BASE = f"https://raw.githubusercontent.com/paezha/idealista18/{COMMIT}"
FUENTES = {
    "Madrid_Sale.rda": f"{BASE}/data/Madrid_Sale.rda",
    "Madrid_Polygons.rda": f"{BASE}/data/Madrid_Polygons.rda",
    "LICENSE.md": f"{BASE}/LICENSE.md",
}

DISTRITOS = {
    "01": "Centro", "02": "Arganzuela", "03": "Retiro", "04": "Salamanca",
    "05": "Chamartín", "06": "Tetuán", "07": "Chamberí", "08": "Fuencarral-El Pardo",
    "09": "Moncloa-Aravaca", "10": "Latina", "11": "Carabanchel", "12": "Usera",
    "13": "Puente de Vallecas", "14": "Moratalaz", "15": "Ciudad Lineal", "16": "Hortaleza",
    "17": "Villaverde", "18": "Villa de Vallecas", "19": "Vicálvaro",
    "20": "San Blas-Canillejas", "21": "Barajas",
}
TRIMESTRES = {201803: "2018-T1", 201806: "2018-T2", 201809: "2018-T3", 201812: "2018-T4"}
BOOLEANOS = {
    "HASLIFT": "ascensor", "HASTERRACE": "terraza", "HASAIRCONDITIONING": "aire_acondicionado",
    "HASPARKINGSPACE": "garaje", "HASBOXROOM": "trastero", "HASSWIMMINGPOOL": "piscina",
    "HASDOORMAN": "portero", "HASGARDEN": "jardin", "ISDUPLEX": "duplex",
    "ISSTUDIO": "estudio", "ISINTOPFLOOR": "ultima_planta",
}
MADRID = ZoneInfo("Europe/Madrid")
INICIO_COLA = datetime(2026, 11, 24, 7, 0, tzinfo=MADRID)  # primer día de "pisos nuevos"
PISOS_POR_DIA = 50
SEMILLA = 2026


def descargar(destino: Path) -> dict[str, Path]:
    rutas = {}
    for nombre, url in FUENTES.items():
        ruta = destino / nombre
        if not ruta.exists():
            print(f"Descargando {url}")
            urllib.request.urlretrieve(url, ruta)
        rutas[nombre] = ruta
    return rutas


def leer_rda(ruta: Path, objeto: str) -> pd.DataFrame:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # avisos inofensivos sobre clases sf/crs/bbox de R
        return rdata.conversion.convert(rdata.parser.parse_file(ruta), default_encoding="utf8")[objeto]


def a_geometria(anillos):
    def poligono(r):
        return Polygon(r[0], r[1:])

    if isinstance(anillos[0], list):
        return MultiPolygon([poligono(p) for p in anillos])
    return poligono(anillos)


def preparar(rutas: dict[str, Path]) -> pd.DataFrame:
    venta = leer_rda(rutas["Madrid_Sale.rda"], "Madrid_Sale").reset_index(drop=True)
    barrios = leer_rda(rutas["Madrid_Polygons.rda"], "Madrid_Polygons").reset_index(drop=True)
    print(f"Anuncios originales: {len(venta):,}")

    # 1. Barrio y distrito: punto en polígono contra los barrios de idealista
    arbol = STRtree([a_geometria(g) for g in barrios["geometry"]])
    puntos = [Point(x, y) for x, y in zip(venta["LONGITUDE"], venta["LATITUDE"])]
    i_punto, i_barrio = arbol.query(puntos, predicate="within")
    asignado = pd.Series(-1, index=venta.index)
    asignado.iloc[i_punto] = i_barrio
    venta = venta[asignado >= 0].copy()
    idx = asignado[asignado >= 0]
    venta["barrio"] = barrios["LOCATIONNAME"].iloc[idx.values].astype(str).values
    venta["distrito"] = [
        DISTRITOS[barrios["LOCATIONID"].iloc[i].split("-")[7]] for i in idx.values
    ]
    print(f"Dentro de algún barrio: {len(venta):,}")

    # 2. Un anuncio por ASSETID (los duplicados están dentro del mismo trimestre)
    venta["ASSETID"] = venta["ASSETID"].astype(str)
    venta = venta.sort_values("PERIOD", kind="stable").drop_duplicates("ASSETID", keep="last")
    print(f"Sin duplicados: {len(venta):,}")

    # 3. Valores extremos
    venta = venta[(venta["ROOMNUMBER"] <= 10) & (venta["BATHNUMBER"] <= 6) & (venta["PRICE"] <= 3_000_000)]
    print(f"Sin valores extremos: {len(venta):,}")

    # 4. Columnas finales con nombres en castellano
    estado = np.select(
        [venta["BUILTTYPEID_1"] == 1, venta["BUILTTYPEID_2"] == 1, venta["BUILTTYPEID_3"] == 1],
        ["obra_nueva", "a_reformar", "buen_estado"],
        default=None,
    )
    pisos = pd.DataFrame({
        "id_anuncio": venta["ASSETID"].values,
        "trimestre": venta["PERIOD"].map(TRIMESTRES).values,
        "precio": venta["PRICE"].round().astype(int).values,
        "precio_m2": venta["UNITPRICE"].round().astype(int).values,
        "superficie_m2": venta["CONSTRUCTEDAREA"].round().astype(int).values,
        "habitaciones": venta["ROOMNUMBER"].astype(int).values,
        "banos": venta["BATHNUMBER"].astype(int).values,
        "planta": pd.array(venta["FLOORCLEAN"].round(), dtype="Int64"),
        "exterior": pd.array(venta["FLATLOCATIONID"].map({1: True, 2: False}), dtype="boolean"),
        "estado": estado,
        "anio_construccion": venta["CADCONSTRUCTIONYEAR"].astype(int).values,
    })
    for original, nuevo in BOOLEANOS.items():
        pisos[nuevo] = venta[original].astype(int).astype(bool).values
    pisos["dist_centro_km"] = venta["DISTANCE_TO_CITY_CENTER"].round(2).values
    pisos["dist_metro_km"] = venta["DISTANCE_TO_METRO"].round(2).values
    pisos["latitud"] = venta["LATITUDE"].round(6).values
    pisos["longitud"] = venta["LONGITUDE"].round(6).values
    pisos["barrio"] = venta["barrio"].values
    pisos["distrito"] = venta["distrito"].values

    # 5. publicado_en: el histórico (T1 a T3) ya publicado, el T4 sale a 50 pisos por día
    rng = np.random.default_rng(SEMILLA)
    historico = pisos["trimestre"] != "2018-T4"
    segundos = rng.integers(0, 30 * 24 * 3600, historico.sum())
    pisos.loc[historico, "publicado_en"] = [
        (INICIO_COLA.replace(hour=0) - timedelta(seconds=int(s))).isoformat() for s in segundos
    ]
    cola = np.flatnonzero(~historico.values)
    rng.shuffle(cola)
    for orden, fila in enumerate(cola):
        pisos.iloc[fila, pisos.columns.get_loc("publicado_en")] = (
            INICIO_COLA + timedelta(days=orden // PISOS_POR_DIA)
        ).isoformat()

    return pisos.sort_values(["publicado_en", "id_anuncio"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--descargas", type=Path, help="carpeta para los ficheros originales (por defecto, una temporal)")
    parser.add_argument("--salida", type=Path, default=Path(__file__).resolve().parent.parent / "data")
    args = parser.parse_args()

    destino = args.descargas or Path(tempfile.mkdtemp(prefix="idealista18-"))
    destino.mkdir(parents=True, exist_ok=True)
    rutas = descargar(destino)
    pisos = preparar(rutas)

    args.salida.mkdir(parents=True, exist_ok=True)
    pisos.to_csv(args.salida / "pisos.csv", index=False, na_rep="")
    muestra = pisos[pisos["trimestre"] != "2018-T4"].sample(5000, random_state=SEMILLA)
    muestra.sort_values("publicado_en").to_csv(args.salida / "pisos_muestra_5000.csv", index=False, na_rep="")
    (args.salida / "LICENSE").write_text(rutas["LICENSE.md"].read_text(encoding="utf-8"), encoding="utf-8")

    hist = (pisos["trimestre"] != "2018-T4").sum()
    print(
        f"\nListo: {len(pisos):,} pisos ({hist:,} de histórico, {len(pisos) - hist:,} en cola), "
        f"{pisos['distrito'].nunique()} distritos, {pisos['barrio'].nunique()} barrios."
    )
    print(f"Escrito en {args.salida}")


if __name__ == "__main__":
    main()
