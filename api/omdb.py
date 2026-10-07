# API OMDB (independiente de TVMaze; HTTP local)
import logging
import os
from typing import Any

import requests

from config import CONFIG
from constants import (
    BASE_URL_OMDB,
    OMDB_RESPONSE_TRUE,
    OMDB_TYPE_MOVIE,
)
from exceptions import ApiError
from models.movie import Movie, MovieListItem

logger = logging.getLogger(__name__)

# Credencial desde variables de entorno (Fase 5); nunca registrar su valor
_API_KEY_OMDB = os.getenv("OMDB_API_KEY", "")


def hacer_request(url: str, params: dict[str, Any] | None = None) -> Any:
    """Hace request; convierte errores de red/JSON en ApiError"""
    if not _API_KEY_OMDB.strip():
        raise ApiError("Falta la variable de entorno OMDB_API_KEY")

    if CONFIG["debug"]:
        params_visibles = {k: v for k, v in (params or {}).items() if k != "apikey"}
        logger.debug("Haciendo request a %s %s", url, params_visibles)

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


def buscar_pelicula(titulo: str) -> Movie | None:
    """Busca película sin validación (sin caché; la caché vive en el servicio)"""
    data = hacer_request(
        BASE_URL_OMDB, {"t": titulo, "apikey": _API_KEY_OMDB}
    )

    if data.get("Response") == OMDB_RESPONSE_TRUE:
        return data
    else:
        return None


def buscar_peliculas_por_actor(actor: str) -> list[MovieListItem]:
    """Busca películas por actor sin paginación"""
    data = hacer_request(
        BASE_URL_OMDB,
        {"s": actor, "type": OMDB_TYPE_MOVIE, "apikey": _API_KEY_OMDB},
    )

    if data.get("Response") == OMDB_RESPONSE_TRUE:
        return data.get("Search", [])
    return []
