# Tests unitarios de services/movie_service.py (sin red)
import json
import logging

import pytest

from constants import HISTORY_DATE_PLACEHOLDER
from exceptions import ApiError, DataExportError, DataImportError
from services import movie_service


def pelicula(titulo="The Forest", **extra):
    base = {"Title": titulo, "Year": "2016", "imdbRating": "4.8"}
    base.update(extra)
    return base


# --- buscar_pelicula (caché) ---


def test_cache_miss_llama_a_omdb_y_cachea(monkeypatch):
    llamadas = []

    def fake(titulo):
        llamadas.append(titulo)
        return pelicula()

    monkeypatch.setattr(movie_service.omdb, "buscar_pelicula", fake)

    resultado = movie_service.buscar_pelicula("forest")

    assert resultado["Title"] == "The Forest"
    assert llamadas == ["forest"]
    assert movie_service.CACHE_PELICULAS["forest"]["Title"] == "The Forest"


def test_cache_hit_no_vuelve_a_llamar_a_omdb(monkeypatch):
    llamadas = []

    def fake(titulo):
        llamadas.append(titulo)
        return pelicula()

    monkeypatch.setattr(movie_service.omdb, "buscar_pelicula", fake)

    movie_service.buscar_pelicula("forest")
    movie_service.buscar_pelicula("forest")

    assert llamadas == ["forest"]
    assert len(movie_service.CACHE_PELICULAS) == 1


def test_cache_prerellenada_no_llama_a_omdb(monkeypatch):
    movie_service.CACHE_PELICULAS["cacheada"] = pelicula("Cacheada")

    def no_debe_llamar(titulo):
        raise AssertionError("no debe consultar OMDB si ya hay caché")

    monkeypatch.setattr(movie_service.omdb, "buscar_pelicula", no_debe_llamar)

    assert movie_service.buscar_pelicula("cacheada")["Title"] == "Cacheada"


def test_cache_genera_log_debug(monkeypatch, caplog):
    movie_service.CACHE_PELICULAS["forest"] = pelicula()

    with caplog.at_level(logging.DEBUG, logger="services.movie_service"):
        movie_service.buscar_pelicula("forest")

    assert "Usando cache para forest" in caplog.text


def test_no_encontrado_devuelve_none_y_no_cachea(monkeypatch):
    monkeypatch.setattr(movie_service.omdb, "buscar_pelicula", lambda titulo: None)

    assert movie_service.buscar_pelicula("zzz") is None
    assert "zzz" not in movie_service.CACHE_PELICULAS


def test_api_error_se_propaga_y_no_cachea(monkeypatch):
    def falla(titulo):
        raise ApiError("sin conexión")

    monkeypatch.setattr(movie_service.omdb, "buscar_pelicula", falla)

    with pytest.raises(ApiError):
        movie_service.buscar_pelicula("forest")

    assert movie_service.CACHE_PELICULAS == {}


# --- buscar_peliculas_por_actor ---


def test_buscar_actor_delega_en_omdb(monkeypatch):
    esperado = [{"Title": "Forrest Gump"}]
    monkeypatch.setattr(
        movie_service.omdb, "buscar_peliculas_por_actor", lambda actor: esperado
    )

    assert movie_service.buscar_peliculas_por_actor("Tom Hanks") == esperado


def test_buscar_actor_sin_resultados(monkeypatch):
    monkeypatch.setattr(
        movie_service.omdb, "buscar_peliculas_por_actor", lambda actor: []
    )

    assert movie_service.buscar_peliculas_por_actor("nadie") == []


def test_buscar_actor_propaga_api_error(monkeypatch):
    def falla(actor):
        raise ApiError("fallo")

    monkeypatch.setattr(movie_service.omdb, "buscar_peliculas_por_actor", falla)

    with pytest.raises(ApiError):
        movie_service.buscar_peliculas_por_actor("x")


# --- películas populares y por género ---


def test_populares_devuelve_la_lista_hardcodeada():
    from constants import POPULAR_MOVIES

    resultado = movie_service.obtener_peliculas_populares()

    assert resultado is POPULAR_MOVIES
    assert len(resultado) == 5
    assert resultado[0]["titulo"] == "The Shawshank Redemption"


def test_genero_accion():
    titulos = [p["titulo"] for p in movie_service.buscar_peliculas_por_genero("accion")]
    assert titulos == ["Die Hard", "Mad Max Fury Road"]


def test_genero_comedia():
    titulos = [p["titulo"] for p in movie_service.buscar_peliculas_por_genero("comedia")]
    assert titulos == ["Superbad", "The Hangover"]


def test_genero_en_mayusculas():
    titulos = [p["titulo"] for p in movie_service.buscar_peliculas_por_genero("COMEDIA")]
    assert titulos == ["Superbad", "The Hangover"]


def test_genero_desconocido_devuelve_todas():
    assert len(movie_service.buscar_peliculas_por_genero("drama")) == 4


def test_genero_vacio_devuelve_todas():
    assert len(movie_service.buscar_peliculas_por_genero("")) == 4


# --- favoritas ---


def test_agregar_favorita_nueva():
    assert movie_service.agregar_a_favoritas(pelicula()) is True
    assert len(movie_service.PELICULAS_FAVORITAS) == 1


def test_agregar_favorita_duplicada_devuelve_false():
    movie_service.agregar_a_favoritas(pelicula())

    assert movie_service.agregar_a_favoritas(pelicula()) is False
    assert len(movie_service.PELICULAS_FAVORITAS) == 1


def test_agregar_dos_favoritas_distintas():
    assert movie_service.agregar_a_favoritas(pelicula("Uno")) is True
    assert movie_service.agregar_a_favoritas(pelicula("Dos")) is True
    assert len(movie_service.PELICULAS_FAVORITAS) == 2


def test_agregar_sin_title_como_si_fuese_duplicada():
    assert movie_service.agregar_a_favoritas({"Year": "2000"}) is True
    assert movie_service.agregar_a_favoritas({"Year": "2001"}) is False
    assert len(movie_service.PELICULAS_FAVORITAS) == 1


def test_eliminar_favorita_existente():
    movie_service.agregar_a_favoritas(pelicula("The Forest"))

    assert movie_service.eliminar_de_favoritas("The Forest") is True
    assert movie_service.PELICULAS_FAVORITAS == []


def test_eliminar_favorita_inexistente():
    movie_service.agregar_a_favoritas(pelicula("The Forest"))

    assert movie_service.eliminar_de_favoritas("Otra") is False
    assert len(movie_service.PELICULAS_FAVORITAS) == 1


def test_eliminar_con_lista_vacia():
    assert movie_service.eliminar_de_favoritas("The Forest") is False


def test_eliminar_coincidiendo_en_none():
    movie_service.PELICULAS_FAVORITAS.append({"Year": "2000"})

    assert movie_service.eliminar_de_favoritas(None) is True
    assert movie_service.PELICULAS_FAVORITAS == []


def test_eliminar_duplicada_quita_solo_la_primera():
    movie_service.PELICULAS_FAVORITAS = [pelicula("Doble"), pelicula("Doble")]

    assert movie_service.eliminar_de_favoritas("Doble") is True
    assert len(movie_service.PELICULAS_FAVORITAS) == 1


# --- historial ---


def test_agregar_al_historial():
    movie_service.agregar_al_historial(pelicula())

    assert movie_service.HISTORIAL_BUSQUEDAS == [
        {"titulo": "The Forest", "fecha": HISTORY_DATE_PLACEHOLDER}
    ]


def test_agregar_al_historial_sin_title():
    movie_service.agregar_al_historial({"Year": "2000"})

    assert movie_service.HISTORIAL_BUSQUEDAS[-1]["titulo"] == ""


def test_historial_no_tiene_limite():
    for i in range(50):
        movie_service.agregar_al_historial(pelicula(f"Peli {i}"))

    assert len(movie_service.HISTORIAL_BUSQUEDAS) == 50


def test_limpiar_historial():
    movie_service.agregar_al_historial(pelicula())
    movie_service.agregar_al_historial(pelicula("Otra"))

    movie_service.limpiar_historial()

    assert movie_service.HISTORIAL_BUSQUEDAS == []


def test_limpiar_historial_reasigna_el_objeto():
    anterior = movie_service.HISTORIAL_BUSQUEDAS
    movie_service.agregar_al_historial(pelicula())

    movie_service.limpiar_historial()

    assert movie_service.HISTORIAL_BUSQUEDAS == []
    assert movie_service.HISTORIAL_BUSQUEDAS is not anterior


# --- estadísticas ---


def test_estadisticas_con_estado_vacio():
    assert movie_service.obtener_estadisticas() == {
        "total_favoritas": 0,
        "total_historial": 0,
    }


def test_estadisticas_reflejan_el_estado_actual():
    movie_service.agregar_a_favoritas(pelicula("Uno"))
    movie_service.agregar_a_favoritas(pelicula("Dos"))
    movie_service.agregar_al_historial(pelicula("Tres"))
    movie_service.agregar_al_historial(pelicula("Cuatro"))
    movie_service.agregar_al_historial(pelicula("Cinco"))

    assert movie_service.obtener_estadisticas() == {
        "total_favoritas": 2,
        "total_historial": 3,
    }


# --- exportar ---


def test_exportar_json_con_estructura_completa(tmp_path, capsys):
    movie_service.agregar_a_favoritas(pelicula())
    movie_service.agregar_al_historial(pelicula())
    destino = tmp_path / "salida.json"

    movie_service.exportar_a_json(str(destino))

    assert destino.exists()
    data = json.loads(destino.read_text(encoding="utf-8"))
    assert set(data) == {"favoritas", "historial", "estadisticas"}
    assert data["favoritas"][0]["Title"] == "The Forest"
    assert data["historial"][0]["titulo"] == "The Forest"
    assert data["estadisticas"] == {"total_favoritas": 1, "total_historial": 1}
    assert f"Exportado a {destino}" in capsys.readouterr().out


def test_exportar_a_directorio_inexistente(tmp_path):
    with pytest.raises(DataExportError) as excinfo:
        movie_service.exportar_a_json(str(tmp_path / "no_existe" / "x.json"))

    assert isinstance(excinfo.value.__cause__, OSError)


def test_exportar_con_dato_no_serializable(tmp_path):
    movie_service.PELICULAS_FAVORITAS.append({"Title": "Rara", "extra": {1, 2}})

    with pytest.raises(DataExportError) as excinfo:
        movie_service.exportar_a_json(str(tmp_path / "rara.json"))

    assert isinstance(excinfo.value.__cause__, TypeError)


# --- importar ---


def test_importar_reemplaza_el_estado(tmp_path):
    movie_service.agregar_a_favoritas(pelicula("Antigua"))
    archivo = tmp_path / "datos.json"
    archivo.write_text(
        json.dumps(
            {
                "favoritas": [pelicula("Nueva")],
                "historial": [{"titulo": "x", "fecha": HISTORY_DATE_PLACEHOLDER}],
            }
        ),
        encoding="utf-8",
    )

    movie_service.importar_de_json(str(archivo))

    assert [p["Title"] for p in movie_service.PELICULAS_FAVORITAS] == ["Nueva"]
    assert len(movie_service.HISTORIAL_BUSQUEDAS) == 1


def test_importar_sin_las_claves_esperadas_usa_defaults(tmp_path):
    archivo = tmp_path / "otro.json"
    archivo.write_text(json.dumps({"otra_clave": 1}), encoding="utf-8")

    movie_service.importar_de_json(str(archivo))

    assert movie_service.PELICULAS_FAVORITAS == []
    assert movie_service.HISTORIAL_BUSQUEDAS == []


def test_importar_archivo_inexistente(tmp_path):
    with pytest.raises(DataImportError) as excinfo:
        movie_service.importar_de_json(str(tmp_path / "no_existe.json"))

    assert isinstance(excinfo.value.__cause__, OSError)


def test_importar_json_invalido(tmp_path):
    archivo = tmp_path / "roto.json"
    archivo.write_text("esto no es json {", encoding="utf-8")

    with pytest.raises(DataImportError) as excinfo:
        movie_service.importar_de_json(str(archivo))

    assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)


def test_importar_imprime_confirmacion(tmp_path, capsys):
    archivo = tmp_path / "ok.json"
    archivo.write_text(json.dumps({}), encoding="utf-8")

    movie_service.importar_de_json(str(archivo))

    assert f"Importado desde {archivo}" in capsys.readouterr().out
