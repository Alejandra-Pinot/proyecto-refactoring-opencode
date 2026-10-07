# Tests unitarios de api/tvmaze.py con mocks (sin red; TVMaze no usa credencial)
import logging

import pytest
import requests

from api import tvmaze
from config import CONFIG
from exceptions import ApiError

URL_SERIES = "http://api.tvmaze.com/search/shows?q=breaking bad"
URL_DETALLE = "http://api.tvmaze.com/shows/169"


class RespuestaFalsa:
    def __init__(self, data=None, status_code=200, json_invalido=False):
        self.data = data
        self.status_code = status_code
        self.json_invalido = json_invalido

    def json(self):
        if self.json_invalido:
            raise ValueError("cuerpo no JSON")
        return self.data


def resultados():
    return [{"show": {"id": 169, "name": "Breaking Bad"}}]


# --- hacer_request ---


def test_request_exitoso_devuelve_el_json(monkeypatch):
    capturado = {}

    def fake_get(url, params=None, timeout=None):
        capturado.update({"url": url, "params": params, "timeout": timeout})
        return RespuestaFalsa({"id": 169})

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    data = tvmaze.hacer_request(URL_DETALLE, {"foo": "bar"})

    assert data == {"id": 169}
    assert capturado["url"] == URL_DETALLE
    assert capturado["params"] == {"foo": "bar"}
    assert capturado["timeout"] == CONFIG["timeout"]


def test_request_usa_el_timeout_de_config(monkeypatch):
    capturado = {}
    CONFIG["timeout"] = 11

    def fake_get(url, params=None, timeout=None):
        capturado["timeout"] = timeout
        return RespuestaFalsa({})

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    tvmaze.hacer_request(URL_DETALLE)

    assert capturado["timeout"] == 11


def test_error_de_red_se_convierte_en_api_error(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.exceptions.ConnectionError("sin red")

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    with pytest.raises(ApiError) as excinfo:
        tvmaze.hacer_request(URL_DETALLE)

    assert isinstance(excinfo.value.__cause__, requests.exceptions.RequestException)
    assert URL_DETALLE in str(excinfo.value)


def test_cuerpo_no_json_se_convierte_en_api_error(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return RespuestaFalsa(json_invalido=True)

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    with pytest.raises(ApiError) as excinfo:
        tvmaze.hacer_request(URL_DETALLE)

    assert isinstance(excinfo.value.__cause__, ValueError)


def test_error_de_timeout_se_convierte_en_api_error(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.exceptions.Timeout("muy lento")

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    with pytest.raises(ApiError):
        tvmaze.hacer_request(URL_DETALLE)


def test_log_de_peticion_registra_la_url(monkeypatch, caplog):
    def fake_get(url, params=None, timeout=None):
        return RespuestaFalsa([])

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    with caplog.at_level(logging.DEBUG, logger="api.tvmaze"):
        tvmaze.hacer_request(URL_DETALLE)

    assert f"Haciendo request a {URL_DETALLE}" in caplog.text


def test_log_de_status_solo_con_verbose(monkeypatch, caplog):
    def fake_get(url, params=None, timeout=None):
        return RespuestaFalsa([])

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    CONFIG["verbose"] = False
    with caplog.at_level(logging.DEBUG, logger="api.tvmaze"):
        tvmaze.hacer_request(URL_DETALLE)
    assert "Status code" not in caplog.text

    caplog.clear()
    CONFIG["verbose"] = True
    with caplog.at_level(logging.DEBUG, logger="api.tvmaze"):
        tvmaze.hacer_request(URL_DETALLE)
    assert "Status code: 200" in caplog.text


# --- buscar_series ---


def test_buscar_series_construye_la_url_de_busqueda(monkeypatch):
    capturado = {}

    def fake_get(url, params=None, timeout=None):
        capturado["url"] = url
        return RespuestaFalsa(resultados())

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    serie = tvmaze.buscar_series("breaking bad")

    assert capturado["url"] == URL_SERIES
    assert serie[0]["show"]["name"] == "Breaking Bad"


def test_buscar_series_sin_resultados(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return RespuestaFalsa([])

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    assert tvmaze.buscar_series("nadie") == []


def test_buscar_series_propaga_api_error(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.exceptions.ConnectionError("sin red")

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    with pytest.raises(ApiError):
        tvmaze.buscar_series("breaking bad")


# --- obtener_detalles_serie ---


def test_detalles_con_id_entero(monkeypatch):
    capturado = {}

    def fake_get(url, params=None, timeout=None):
        capturado["url"] = url
        return RespuestaFalsa({"id": 169, "name": "Breaking Bad"})

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    serie = tvmaze.obtener_detalles_serie(169)

    assert capturado["url"] == URL_DETALLE
    assert serie["name"] == "Breaking Bad"


def test_detalles_con_id_cadena(monkeypatch):
    capturado = {}

    def fake_get(url, params=None, timeout=None):
        capturado["url"] = url
        return RespuestaFalsa({"id": 169})

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    tvmaze.obtener_detalles_serie("169")

    assert capturado["url"] == URL_DETALLE


def test_detalles_propagan_api_error(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        raise requests.exceptions.ConnectionError("sin red")

    monkeypatch.setattr(tvmaze.requests, "get", fake_get)

    with pytest.raises(ApiError):
        tvmaze.obtener_detalles_serie(169)
