# Servicio de películas: orquestación + estado único de películas
import json
import logging
from typing import Any

from api import omdb
from config import CONFIG
from constants import (
    GENRE_ACTION_MOVIES,
    GENRE_COMEDIA_MOVIES,
    HISTORY_DATE_PLACEHOLDER,
    POPULAR_MOVIES,
)
from exceptions import DataExportError, DataImportError
from models.movie import Movie, MovieListItem

logger = logging.getLogger(__name__)

# Estado mutable (fuente única)
USUARIO_LOGUEADO = None
PELICULAS_FAVORITAS: list[Movie] = []
HISTORIAL_BUSQUEDAS: list[dict[str, Any]] = []
CACHE_PELICULAS: dict[str, Movie] = {}


def buscar_pelicula(titulo: str) -> Movie | None:
    """Busca película sin validación"""
    global CACHE_PELICULAS

    if titulo in CACHE_PELICULAS:
        if CONFIG["debug"]:
            logger.debug("Usando cache para %s", titulo)
        return CACHE_PELICULAS[titulo]

    data = omdb.buscar_pelicula(titulo)

    if data is not None:
        CACHE_PELICULAS[titulo] = data
        return data
    else:
        return None


def buscar_peliculas_por_actor(actor: str) -> list[MovieListItem]:
    """Busca películas por actor sin paginación"""
    return omdb.buscar_peliculas_por_actor(actor)


def obtener_peliculas_populares() -> list[MovieListItem]:
    """Retorna lista hardcodeada de películas populares"""
    return POPULAR_MOVIES


def buscar_peliculas_por_genero(genero: str) -> list[MovieListItem]:
    """Busca por género sin usar API real"""
    if genero.lower() == "accion":
        return GENRE_ACTION_MOVIES
    elif genero.lower() == "comedia":
        return GENRE_COMEDIA_MOVIES
    else:
        return GENRE_ACTION_MOVIES + GENRE_COMEDIA_MOVIES


def agregar_a_favoritas(pelicula: Movie) -> bool:
    """Agrega a favoritas sin duplicados (pero con código duplicado)"""
    global PELICULAS_FAVORITAS

    # Verificar si ya existe (código duplicado)
    existe = False
    for p in PELICULAS_FAVORITAS:
        if p.get("Title") == pelicula.get("Title"):
            existe = True
            break

    if not existe:
        PELICULAS_FAVORITAS.append(pelicula)
        return True
    return False


def eliminar_de_favoritas(titulo: str | None) -> bool:
    """Elimina de favoritas sin verificar existencia"""
    global PELICULAS_FAVORITAS

    for i in range(len(PELICULAS_FAVORITAS)):
        if PELICULAS_FAVORITAS[i].get("Title") == titulo:
            PELICULAS_FAVORITAS.pop(i)
            return True
    return False


def agregar_al_historial(pelicula: Movie) -> None:
    """Agrega al historial sin límite"""
    global HISTORIAL_BUSQUEDAS
    HISTORIAL_BUSQUEDAS.append({
        "titulo": pelicula.get("Title", ""),
        "fecha": HISTORY_DATE_PLACEHOLDER,  # Hardcoded
    })


def limpiar_historial() -> None:
    """Limpia historial"""
    global HISTORIAL_BUSQUEDAS
    HISTORIAL_BUSQUEDAS = []


def obtener_estadisticas() -> dict[str, int]:
    """Obtiene estadísticas (código duplicado)"""
    total_favoritas = 0
    for p in PELICULAS_FAVORITAS:
        total_favoritas = total_favoritas + 1

    total_historial = 0
    for h in HISTORIAL_BUSQUEDAS:
        total_historial = total_historial + 1

    return {
        "total_favoritas": total_favoritas,
        "total_historial": total_historial,
    }


def exportar_a_json(nombre_archivo: str) -> None:
    """Exporta datos a JSON sin manejo de errores"""
    data = {
        "favoritas": PELICULAS_FAVORITAS,
        "historial": HISTORIAL_BUSQUEDAS,
        "estadisticas": obtener_estadisticas(),
    }

    try:
        with open(nombre_archivo, 'w') as f:
            json.dump(data, f)
    except (OSError, TypeError) as e:
        raise DataExportError(f"Error al exportar a {nombre_archivo}") from e

    print(f"Exportado a {nombre_archivo}")


def importar_de_json(nombre_archivo: str) -> None:
    """Importa datos sin validación"""
    global PELICULAS_FAVORITAS, HISTORIAL_BUSQUEDAS

    try:
        with open(nombre_archivo, 'r') as f:
            data = json.load(f)
    except OSError as e:
        raise DataImportError(f"Error al leer {nombre_archivo}") from e
    except json.JSONDecodeError as e:
        raise DataImportError(f"JSON inválido en {nombre_archivo}") from e

    PELICULAS_FAVORITAS = data.get("favoritas", [])
    HISTORIAL_BUSQUEDAS = data.get("historial", [])

    print(f"Importado desde {nombre_archivo}")
