# API TVMaze (independiente de OMDB; HTTP local)
import logging
from typing import Any

import requests

from config import CONFIG
from constants import BASE_URL_TVMAZE
from exceptions import ApiError
from models.series import SeriesSearchItem, SeriesShow

logger = logging.getLogger(__name__)


def hacer_request(url: str, params: dict[str, Any] | None = None) -> Any:
    """Hace request; convierte errores de red/JSON en ApiError"""
    if CONFIG["debug"]:
        logger.debug("Haciendo request a %s", url)

    try:
        response = requests.get(url, params=params, timeout=CONFIG["timeout"])
    except requests.exceptions.RequestException as e:
        raise ApiError(f"Error en la petición a {url}") from e

    if CONFIG["verbose"]:
        logger.debug("Status code: %s", response.status_code)

    try:
        return response.json()
    except ValueError as e:
        raise ApiError(f"Respuesta no JSON desde {url}") from e


def buscar_series(nombre: str) -> list[SeriesSearchItem]:
    """Busca series en TVMaze (sin caché; la caché vive en el servicio)"""
    url = f"{BASE_URL_TVMAZE}/search/shows?q={nombre}"
    return hacer_request(url)


def obtener_detalles_serie(id_serie: int | str) -> SeriesShow:
    """Obtiene detalles de serie"""
    url = f"{BASE_URL_TVMAZE}/shows/{id_serie}"
    return hacer_request(url)
