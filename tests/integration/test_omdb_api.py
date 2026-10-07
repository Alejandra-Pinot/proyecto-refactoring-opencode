# Tests de integración con la API real de OMDB (red real permitida).
# Si OMDB_API_KEY no está en el entorno, el módulo entero queda SKIPPED (nunca FAILED).
# La credencial no se imprime, no se copia y no se escribe en ningún archivo.
import logging
import os

import pytest

from api import omdb
from constants import BASE_URL_OMDB

pytestmark = pytest.mark.skipif(
    not os.getenv("OMDB_API_KEY", "").strip(),
    reason="OMDB_API_KEY no está configurada en el entorno",
)


def test_hacer_request_responde_con_datos_json():
    data = omdb.hacer_request(BASE_URL_OMDB, {"t": "forest"})

    assert isinstance(data, dict)
    assert "Response" in data


def test_buscar_pelicula_existente_devuelve_datos():
    pelicula = omdb.buscar_pelicula("forest")

    assert isinstance(pelicula, dict)
    assert pelicula["Response"] == "True"
    assert "Title" in pelicula


def test_buscar_pelicula_inexistente_devuelve_none():
    assert omdb.buscar_pelicula("zzzqqqxyz pelicula inexistente 12345") is None


def test_buscar_peliculas_por_actor_con_resultados():
    peliculas = omdb.buscar_peliculas_por_actor("Tom Hanks")

    assert isinstance(peliculas, list)
    assert len(peliculas) > 0
    for item in peliculas:
        assert "Title" in item


def test_buscar_peliculas_por_actor_sin_resultados():
    assert omdb.buscar_peliculas_por_actor("zzzqqqxyz actor inexistente 12345") == []


def test_la_credencial_no_aparece_en_los_logs(caplog):
    with caplog.at_level(logging.DEBUG, logger="api.omdb"):
        omdb.buscar_pelicula("forest")

    clave = os.getenv("OMDB_API_KEY", "")
    # Aserción con mensaje estático: jamás muestra la credencial
    if clave and clave in caplog.text:
        pytest.fail("La credencial aparece en los logs")
    assert "apikey" not in caplog.text


def test_el_log_de_peticion_registra_solo_parametros_visibles(caplog):
    with caplog.at_level(logging.DEBUG, logger="api.omdb"):
        omdb.buscar_pelicula("forest")

    mensajes = [record.getMessage() for record in caplog.records]
    peticiones = [m for m in mensajes if "Haciendo request" in m]

    assert len(peticiones) == 1
    assert "'t': 'forest'" in peticiones[0]
