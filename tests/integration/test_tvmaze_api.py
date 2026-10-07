# Tests de integración con la API real de TVMaze (sin credencial; red real permitida)
import pytest

from api import tvmaze

SERIE_DE_EJEMPLO = {
    "id": 169,
    "name": "Breaking Bad",
    "language": "English",
    "status": "Ended",
}


def test_buscar_series_devuelve_resultados():
    resultados = tvmaze.buscar_series("breaking bad")

    assert isinstance(resultados, list)
    assert len(resultados) > 0
    assert "show" in resultados[0]
    assert isinstance(resultados[0]["show"]["id"], int)
    assert isinstance(resultados[0]["show"]["name"], str)


def test_buscar_series_inexistente_devuelve_lista_vacia():
    resultados = tvmaze.buscar_series("zzzqqqxyz serie inexistente 12345")

    assert resultados == []


def test_buscar_series_devuelve_siempre_estructura_de_lista():
    resultados = tvmaze.buscar_series("the wire")

    assert isinstance(resultados, list)
    for item in resultados:
        assert isinstance(item, dict)
        assert "show" in item


def test_obtener_detalles_serie_por_id_entero():
    serie = tvmaze.obtener_detalles_serie(SERIE_DE_EJEMPLO["id"])

    assert serie["id"] == SERIE_DE_EJEMPLO["id"]
    assert serie["name"] == SERIE_DE_EJEMPLO["name"]
    assert serie["language"] == SERIE_DE_EJEMPLO["language"]
    assert serie["status"] == SERIE_DE_EJEMPLO["status"]


def test_obtener_detalles_serie_por_id_cadena():
    serie = tvmaze.obtener_detalles_serie(str(SERIE_DE_EJEMPLO["id"]))

    assert serie["id"] == SERIE_DE_EJEMPLO["id"]


def test_resultado_de_busqueda_relacionado_con_los_detalles():
    resultados = tvmaze.buscar_series("breaking bad")
    ids = [item["show"]["id"] for item in resultados]

    assert SERIE_DE_EJEMPLO["id"] in ids
