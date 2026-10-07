# Servicio de series: orquestación + estado único de series
from api import tvmaze
from config import CONFIG
from constants import SERIES_CACHE_PREFIX
from models.series import SeriesSearchItem, SeriesShow

# Estado mutable (fuente única)
CACHE_SERIES: dict[str, list[SeriesSearchItem]] = {}


def buscar_series(nombre: str) -> list[SeriesSearchItem]:
    """Busca series en TVMaze"""
    global CACHE_SERIES

    cache_key = f"{SERIES_CACHE_PREFIX}{nombre}"
    if cache_key in CACHE_SERIES:
        return CACHE_SERIES[cache_key]

    data = tvmaze.buscar_series(nombre)

    CACHE_SERIES[cache_key] = data
    return data


def obtener_detalles_serie(id_serie: int | str) -> SeriesShow:
    """Obtiene detalles de serie"""
    return tvmaze.obtener_detalles_serie(id_serie)
