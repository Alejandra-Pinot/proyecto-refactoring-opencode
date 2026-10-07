# Tests unitarios de api/omdb.py con mocks (sin red, sin credencial real)
import logging

import pytest
import requests

from api import omdb
from config import CONFIG
from exceptions import ApiError

# Clave falsa exclusiva de los tests: nunca usar la credencial real
CLAVE_FALSA = "clave-de-test-omdb"
BASE = "http://www.omdbapi.com/"


class RespuestaFalsa:
    def __init__(self, data=None, status_code=200, json_invalido=False):
        self.data = data
        self.status_code = status_code
        self.json_invalido = json_invalido

    def json(self):
        if self.json_invalido:
            raise ValueError("cuerpo no JSON")
        return self.data


@pytest.fixture
def con_clave(monkeypatch):
    monkeypatch.setattr(omdb, "_API_KEY_OMDB", CLAVE_FALSA)


# --- credencial (Fase 5) ---


def test_sin_credencial_lanza_api_error(monkeypatch):
    monkeypatch.setattr(omdb, "_API_KEY_OMDB", "")

    with pytest.raises(ApiError) as excinfo:
        omdb.hacer_request(BASE)

    assert "OMDB_API_KEY" in str(excinfo.value)


def test_credencial_con_solo_espacios_lanza_api_error(monkeypatch):
    monkeypatch.setattr(omdb, "_API_KEY_OMDB", "   ")

    with pytest.raises(ApiError):
        omdb.hacer_request(BASE)


def test_sin_credencial_no_hace_ninguna_peticion(monkeypatch):
    monkeypatch.setattr(omdb, "_API_KEY_OMDB", "")

    def no_debe_llamar(url, params=None, timeout=None):
        raise AssertionError("no debe llamar a la red sin credencial")

    monkeypatch.setattr(omdb.requests, "get", no_debe_llamar)

    with pytest.raises(ApiError):
        omdb.hacer_request(BASE)


def test_sin_credencial_no_registra_nada_en_el_log(monkeypatch, caplog):
    monkeypatch.setattr(omdb, "_API_KEY_OMDB", "")

    with caplog.at_level(logging.DEBUG, logger="api.omdb"):
        with pytest.raises(ApiError):
            omdb.hacer_request(BASE, {"t": "forest", "apikey": omdb._API_KEY_OMDB})

    assert caplog.text == ""


# --- hacer_request ---


def test_request_exitoso_devuelve_el_json(con_clave, monkeypatch):
    capturado = {}

    def fake_get(url, params=None, timeout=None):
        capturado.update({"url": url, "params": params, "timeout": timeout})
        return RespuestaFalsa({"Response": "True", "Title": "The Forest"})

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    data = omdb.hacer_request(BASE, {"t": "forest"})

    assert data["Title"] == "The Forest"
    assert capturado["url"] == BASE
    assert capturado["params"] == {"t": "forest"}
    assert capturado["timeout"] == CONFIG["timeout"]


def test_request_usa_el_timeout_de_config(con_clave, monkeypatch):
    capturado = {}
    CONFIG["timeout"] = 7

    def fake_get(url, params=None, timeout=None):
        capturado["timeout"] = timeout
        return RespuestaFalsa({})

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    omdb.hacer_request(BASE)

    assert capturado["timeout"] == 7


def test_error_de_red_se_convierte_en_api_error(con_clave, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.exceptions.ConnectionError("sin red")

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    with pytest.raises(ApiError) as excinfo:
        omdb.hacer_request(BASE)

    assert isinstance(excinfo.value.__cause__, requests.exceptions.RequestException)
    assert BASE in str(excinfo.value)


def test_cuerpo_no_json_se_convierte_en_api_error(con_clave, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return RespuestaFalsa(json_invalido=True)

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    with pytest.raises(ApiError) as excinfo:
        omdb.hacer_request(BASE)

    assert isinstance(excinfo.value.__cause__, ValueError)


def test_el_log_de_peticion_no_muestra_la_clave(con_clave, monkeypatch, caplog):
    def fake_get(url, params=None, timeout=None):
        return RespuestaFalsa({"Response": "True"})

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    with caplog.at_level(logging.DEBUG, logger="api.omdb"):
        omdb.hacer_request(BASE, {"t": "forest", "apikey": omdb._API_KEY_OMDB})

    # Aserción con mensaje estático: jamás imprime la credencial
    if omdb._API_KEY_OMDB and omdb._API_KEY_OMDB in caplog.text:
        pytest.fail("La credencial aparece en los logs")
    assert "apikey" not in caplog.text


def test_error_de_red_no_incluye_la_clave_en_el_mensaje(con_clave, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.exceptions.ConnectionError("fallo")

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    with pytest.raises(ApiError) as excinfo:
        omdb.hacer_request(BASE, {"apikey": omdb._API_KEY_OMDB})

    if omdb._API_KEY_OMDB and omdb._API_KEY_OMDB in str(excinfo.value):
        pytest.fail("La credencial aparece en el mensaje de error")


# --- buscar_pelicula ---


def test_buscar_pelicula_response_true(con_clave, monkeypatch):
    capturado = {}

    def fake_get(url, params=None, timeout=None):
        capturado["params"] = params
        return RespuestaFalsa({"Response": "True", "Title": "The Forest"})

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    pelicula = omdb.buscar_pelicula("forest")

    assert pelicula["Title"] == "The Forest"
    assert capturado["params"]["t"] == "forest"
    assert capturado["params"]["apikey"] == CLAVE_FALSA


def test_buscar_pelicula_response_false_devuelve_none(con_clave, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return RespuestaFalsa({"Response": "False", "Error": "Movie not found!"})

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    assert omdb.buscar_pelicula("zzz") is None


def test_buscar_pelicula_propaga_api_error(con_clave, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.exceptions.Timeout("muy lento")

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    with pytest.raises(ApiError):
        omdb.buscar_pelicula("forest")


# --- buscar_peliculas_por_actor ---


def test_buscar_actor_response_true(con_clave, monkeypatch):
    capturado = {}

    def fake_get(url, params=None, timeout=None):
        capturado["params"] = params
        return RespuestaFalsa(
            {
                "Response": "True",
                "Search": [{"Title": "Forrest Gump", "Year": "1994"}],
            }
        )

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    peliculas = omdb.buscar_peliculas_por_actor("Tom Hanks")

    assert [p["Title"] for p in peliculas] == ["Forrest Gump"]
    assert capturado["params"]["s"] == "Tom Hanks"
    assert capturado["params"]["type"] == "movie"
    assert capturado["params"]["apikey"] == CLAVE_FALSA


def test_buscar_actor_response_false_devuelve_lista_vacia(con_clave, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return RespuestaFalsa({"Response": "False", "Error": "no results"})

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    assert omdb.buscar_peliculas_por_actor("nadie") == []


def test_buscar_actor_sin_campo_search_devuelve_lista_vacia(con_clave, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return RespuestaFalsa({"Response": "True"})

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    assert omdb.buscar_peliculas_por_actor("nadie") == []


def test_buscar_actor_propaga_api_error(con_clave, monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.exceptions.ConnectionError("sin red")

    monkeypatch.setattr(omdb.requests, "get", fake_get)

    with pytest.raises(ApiError):
        omdb.buscar_peliculas_por_actor("Tom Hanks")
