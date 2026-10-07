# Fixtures compartidos de la suite (Fase 6): aislamiento de estado mutable
import pytest

from config import CONFIG
from services import movie_service, series_service


@pytest.fixture(autouse=True)
def estado_limpio():
    """Estado mutable limpio antes de cada test y restaurado después"""
    favoritas = movie_service.PELICULAS_FAVORITAS
    historial = movie_service.HISTORIAL_BUSQUEDAS
    cache_peliculas = movie_service.CACHE_PELICULAS
    cache_series = series_service.CACHE_SERIES
    usuario = movie_service.USUARIO_LOGUEADO

    movie_service.PELICULAS_FAVORITAS = []
    movie_service.HISTORIAL_BUSQUEDAS = []
    movie_service.CACHE_PELICULAS = {}
    series_service.CACHE_SERIES = {}
    movie_service.USUARIO_LOGUEADO = None

    yield

    movie_service.PELICULAS_FAVORITAS = favoritas
    movie_service.HISTORIAL_BUSQUEDAS = historial
    movie_service.CACHE_PELICULAS = cache_peliculas
    series_service.CACHE_SERIES = cache_series
    movie_service.USUARIO_LOGUEADO = usuario


@pytest.fixture(autouse=True)
def config_intacta():
    """CONFIG vuelve a su estado original tras cada test"""
    original = dict(CONFIG)
    yield
    CONFIG.clear()
    CONFIG.update(original)


def pytest_collection_modifyitems(items):
    """Aplica los markers unit/integration según la carpeta (D6)"""
    for item in items:
        ruta = str(getattr(item, "path", getattr(item, "fspath", ""))).replace("\\", "/")
        if "/tests/unit/" in ruta:
            item.add_marker(pytest.mark.unit)
        elif "/tests/integration/" in ruta:
            item.add_marker(pytest.mark.integration)
