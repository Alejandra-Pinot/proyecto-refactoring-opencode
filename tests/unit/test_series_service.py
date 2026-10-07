# Tests unitarios de services/series_service.py (sin red)
import pytest

from constants import SERIES_CACHE_PREFIX
from exceptions import ApiError
from services import series_service


def resultados():
    return [
        {"show": {"id": 169, "name": "Breaking Bad", "status": "Ended"}},
        {"show": {"id": 167, "name": "Better Call Saul", "status": "Ended"}},
    ]


def test_cache_miss_llama_a_tvmaze_y_cachea(monkeypatch):
    llamadas = []

    def fake(nombre):
        llamadas.append(nombre)
        return resultados()

    monkeypatch.setattr(series_service.tvmaze, "buscar_series", fake)

    serie = series_service.buscar_series("breaking bad")

    assert serie[0]["show"]["name"] == "Breaking Bad"
    assert llamadas == ["breaking bad"]
    assert f"{SERIES_CACHE_PREFIX}breaking bad" in series_service.CACHE_SERIES


def test_cache_hit_no_vuelve_a_llamar_a_tvmaze(monkeypatch):
    llamadas = []

    def fake(nombre):
        llamadas.append(nombre)
        return resultados()

    monkeypatch.setattr(series_service.tvmaze, "buscar_series", fake)

    series_service.buscar_series("breaking bad")
    series_service.buscar_series("breaking bad")

    assert llamadas == ["breaking bad"]


def test_resultado_vacio_tambien_se_cachea(monkeypatch):
    llamadas = []

    def fake(nombre):
        llamadas.append(nombre)
        return []

    monkeypatch.setattr(series_service.tvmaze, "buscar_series", fake)

    assert series_service.buscar_series("nadie") == []
    assert series_service.buscar_series("nadie") == []
    assert llamadas == ["nadie"]


def test_distintos_nombres_usan_claves_distintas(monkeypatch):
    monkeypatch.setattr(
        series_service.tvmaze, "buscar_series", lambda nombre: resultados()
    )

    series_service.buscar_series("breaking bad")
    series_service.buscar_series("the wire")

    assert set(series_service.CACHE_SERIES) == {
        f"{SERIES_CACHE_PREFIX}breaking bad",
        f"{SERIES_CACHE_PREFIX}the wire",
    }


def test_api_error_se_propaga_y_no_cachea(monkeypatch):
    def falla(nombre):
        raise ApiError("sin conexión")

    monkeypatch.setattr(series_service.tvmaze, "buscar_series", falla)

    with pytest.raises(ApiError):
        series_service.buscar_series("breaking bad")

    assert series_service.CACHE_SERIES == {}


def test_detalles_delega_en_tvmaze(monkeypatch):
    esperado = {"id": 169, "name": "Breaking Bad"}
    capturado = {}

    def fake(id_serie):
        capturado["id"] = id_serie
        return esperado

    monkeypatch.setattr(series_service.tvmaze, "obtener_detalles_serie", fake)

    assert series_service.obtener_detalles_serie(169) == esperado
    assert capturado["id"] == 169


def test_detalles_acepta_id_cadena(monkeypatch):
    capturado = {}

    def fake(id_serie):
        capturado["id"] = id_serie
        return {"id": 169}

    monkeypatch.setattr(series_service.tvmaze, "obtener_detalles_serie", fake)

    series_service.obtener_detalles_serie("169")

    assert capturado["id"] == "169"


def test_detalles_propagan_api_error(monkeypatch):
    def falla(id_serie):
        raise ApiError("fallo")

    monkeypatch.setattr(series_service.tvmaze, "obtener_detalles_serie", falla)

    with pytest.raises(ApiError):
        series_service.obtener_detalles_serie(169)
