# Tests unitarios de ui/menu.py: entradas guionizadas, sin red y sin limpiar la terminal
import logging

import pytest

from config import CONFIG
from exceptions import ApiError, DataImportError
from services import movie_service, series_service
from ui import menu

SEPARADOR = "=" * 60


class Entradas:
    """Secuencia de respuestas para input(); falla si se acaban"""

    def __init__(self, *valores):
        self.pendientes = list(valores)
        self.usadas = []

    def __call__(self, prompt=""):
        if not self.pendientes:
            raise AssertionError(f"Se agotaron las entradas (prompt: {prompt!r})")
        valor = self.pendientes.pop(0)
        self.usadas.append(valor)
        return valor


def preparar(monkeypatch, *valores):
    entradas = Entradas(*valores)
    monkeypatch.setattr("builtins.input", entradas)
    monkeypatch.setattr(menu, "delay", lambda segundos: None)
    monkeypatch.setattr(menu, "clear_screen", lambda: None)
    return entradas


def pelicula(titulo="The Forest", **extra):
    base = {"Title": titulo, "Year": "2016", "imdbRating": "4.8"}
    base.update(extra)
    return base


# --- clear_screen / delay ---


def test_clear_screen_llama_al_comando_del_sistema(monkeypatch):
    llamadas = []
    monkeypatch.setattr(menu.os, "system", lambda comando: llamadas.append(comando) or 0)

    menu.clear_screen()

    assert llamadas == ["cls" if menu.os.name == "nt" else "clear"]


def test_delay_duerme_el_tiempo_indicado(monkeypatch):
    llamadas = []
    monkeypatch.setattr(menu.time, "sleep", lambda segundos: llamadas.append(segundos))

    menu.delay(0.25)

    assert llamadas == [0.25]


# --- funcion_buscar_pelicula ---


def test_buscar_pelicula_con_titulo_vacio(monkeypatch, capsys):
    preparar(monkeypatch, "", "")
    llamadas = []
    monkeypatch.setattr(
        movie_service, "buscar_pelicula", lambda t: llamadas.append(t)
    )

    menu.funcion_buscar_pelicula()

    assert llamadas == []
    assert "Título vacío" in capsys.readouterr().out


def test_buscar_pelicula_agrega_a_favoritas_con_s(monkeypatch, capsys):
    preparar(monkeypatch, "forest", "s", "")
    monkeypatch.setattr(movie_service, "buscar_pelicula", lambda t: pelicula())

    menu.funcion_buscar_pelicula()

    salida = capsys.readouterr().out
    assert "Buscando..." in salida
    assert "Título: The Forest" in salida
    assert "¡Agregada a favoritos!" in salida
    assert [p["Title"] for p in movie_service.PELICULAS_FAVORITAS] == ["The Forest"]
    assert movie_service.HISTORIAL_BUSQUEDAS[0]["titulo"] == "The Forest"


def test_buscar_pelicula_acepta_si_con_mayusculas_y_espacios(monkeypatch, capsys):
    preparar(monkeypatch, "forest", "  SI  ", "")
    monkeypatch.setattr(movie_service, "buscar_pelicula", lambda t: pelicula())

    menu.funcion_buscar_pelicula()

    assert "¡Agregada a favoritos!" in capsys.readouterr().out
    assert len(movie_service.PELICULAS_FAVORITAS) == 1


def test_buscar_pelicula_con_no_no_agrega(monkeypatch, capsys):
    preparar(monkeypatch, "forest", "n", "")
    monkeypatch.setattr(movie_service, "buscar_pelicula", lambda t: pelicula())

    menu.funcion_buscar_pelicula()

    salida = capsys.readouterr().out
    assert "¡Agregada a favoritos!" not in salida
    assert movie_service.PELICULAS_FAVORITAS == []
    assert len(movie_service.HISTORIAL_BUSQUEDAS) == 1


def test_buscar_pelicula_duplicada_en_favoritas(monkeypatch, capsys):
    preparar(monkeypatch, "forest", "s", "")
    monkeypatch.setattr(movie_service, "buscar_pelicula", lambda t: pelicula())
    movie_service.PELICULAS_FAVORITAS.append(pelicula())

    menu.funcion_buscar_pelicula()

    assert "Ya está en favoritos" in capsys.readouterr().out
    assert len(movie_service.PELICULAS_FAVORITAS) == 1


def test_buscar_pelicula_no_encontrada(monkeypatch, capsys):
    preparar(monkeypatch, "zzz", "")
    monkeypatch.setattr(movie_service, "buscar_pelicula", lambda t: None)

    menu.funcion_buscar_pelicula()

    salida = capsys.readouterr().out
    assert "No se encontró la película" in salida
    assert movie_service.HISTORIAL_BUSQUEDAS == []


def test_buscar_pelicula_muestra_el_error_de_api(monkeypatch, capsys, caplog):
    preparar(monkeypatch, "forest", "")

    def falla(titulo):
        raise ApiError("Falta la variable de entorno OMDB_API_KEY")

    monkeypatch.setattr(movie_service, "buscar_pelicula", falla)

    with caplog.at_level(logging.ERROR, logger="ui.menu"):
        menu.funcion_buscar_pelicula()

    salida = capsys.readouterr().out
    assert "Error: Falta la variable de entorno OMDB_API_KEY" in salida
    assert "Error en búsqueda OMDB" in caplog.text
    assert movie_service.HISTORIAL_BUSQUEDAS == []


# --- funcion_buscar_actor ---


def test_buscar_actor_con_nombre_vacio(monkeypatch, capsys):
    preparar(monkeypatch, "", "")
    llamadas = []
    monkeypatch.setattr(
        movie_service, "buscar_peliculas_por_actor", lambda a: llamadas.append(a)
    )

    menu.funcion_buscar_actor()

    assert llamadas == []
    assert "Nombre de actor vacío" in capsys.readouterr().out


def test_buscar_actor_selecciona_la_primera_pelicula(monkeypatch, capsys):
    preparar(monkeypatch, "Tom Hanks", "1", "")
    monkeypatch.setattr(
        movie_service,
        "buscar_peliculas_por_actor",
        lambda a: [
            {"Title": "Forrest Gump", "Year": "1994"},
            {"Title": "Cast Away", "Year": "2000"},
        ],
    )
    detalles = []
    monkeypatch.setattr(
        movie_service, "buscar_pelicula", lambda t: detalles.append(t) or pelicula(t)
    )

    menu.funcion_buscar_actor()

    salida = capsys.readouterr().out
    assert "1. Forrest Gump (1994)" in salida
    assert detalles == ["Forrest Gump"]


def test_buscar_actor_volver_con_cero(monkeypatch, capsys):
    preparar(monkeypatch, "Tom Hanks", "0", "")
    monkeypatch.setattr(
        movie_service,
        "buscar_peliculas_por_actor",
        lambda a: [{"Title": "Forrest Gump"}],
    )
    llamadas = []
    monkeypatch.setattr(movie_service, "buscar_pelicula", lambda t: llamadas.append(t))

    menu.funcion_buscar_actor()

    assert llamadas == []
    assert "1. Forrest Gump" in capsys.readouterr().out


def test_buscar_actor_indice_fuera_de_rango(monkeypatch):
    preparar(monkeypatch, "Tom Hanks", "99", "")
    monkeypatch.setattr(
        movie_service,
        "buscar_peliculas_por_actor",
        lambda a: [{"Title": "Forrest Gump"}],
    )
    llamadas = []
    monkeypatch.setattr(movie_service, "buscar_pelicula", lambda t: llamadas.append(t))

    menu.funcion_buscar_actor()

    assert llamadas == []


def test_buscar_actor_entrada_no_numerica_no_crashea(monkeypatch):
    preparar(monkeypatch, "Tom Hanks", "²", "")
    monkeypatch.setattr(
        movie_service,
        "buscar_peliculas_por_actor",
        lambda a: [{"Title": "Forrest Gump"}],
    )
    llamadas = []
    monkeypatch.setattr(movie_service, "buscar_pelicula", lambda t: llamadas.append(t))

    menu.funcion_buscar_actor()

    assert llamadas == []


def test_buscar_actor_sin_resultados(monkeypatch, capsys):
    preparar(monkeypatch, "nadie", "")
    monkeypatch.setattr(movie_service, "buscar_peliculas_por_actor", lambda a: [])

    menu.funcion_buscar_actor()

    assert "No se encontraron películas para ese actor" in capsys.readouterr().out


def test_buscar_actor_muestra_el_error_de_api(monkeypatch, capsys, caplog):
    preparar(monkeypatch, "Tom Hanks", "")

    def falla(actor):
        raise ApiError("Error en la petición")

    monkeypatch.setattr(movie_service, "buscar_peliculas_por_actor", falla)

    with caplog.at_level(logging.ERROR, logger="ui.menu"):
        menu.funcion_buscar_actor()

    assert "Error: Error en la petición" in capsys.readouterr().out
    assert "Error en búsqueda OMDB" in caplog.text


# --- funcion_buscar_series ---


def test_buscar_series_con_nombre_vacio(monkeypatch, capsys):
    preparar(monkeypatch, "", "")
    llamadas = []
    monkeypatch.setattr(
        series_service, "buscar_series", lambda n: llamadas.append(n)
    )

    menu.funcion_buscar_series()

    assert llamadas == []
    assert "Nombre de serie vacío" in capsys.readouterr().out


def test_buscar_series_selecciona_la_primera(monkeypatch, capsys):
    preparar(monkeypatch, "breaking bad", "1", "")
    monkeypatch.setattr(
        series_service,
        "buscar_series",
        lambda n: [
            {"show": {"id": 169, "name": "Breaking Bad", "status": "Ended"}},
            {"show": {"id": 167, "name": "Better Call Saul", "status": "Ended"}},
        ],
    )
    ids = []
    monkeypatch.setattr(
        series_service,
        "obtener_detalles_serie",
        lambda i: ids.append(i) or {"name": "Breaking Bad"},
    )

    menu.funcion_buscar_series()

    salida = capsys.readouterr().out
    assert "1. Breaking Bad (Ended)" in salida
    assert "2. Better Call Saul (Ended)" in salida
    assert ids == [169]


def test_buscar_series_volver_con_cero(monkeypatch):
    preparar(monkeypatch, "breaking bad", "0", "")
    monkeypatch.setattr(
        series_service,
        "buscar_series",
        lambda n: [{"show": {"id": 169, "name": "Breaking Bad"}}],
    )
    llamadas = []
    monkeypatch.setattr(
        series_service, "obtener_detalles_serie", lambda i: llamadas.append(i)
    )

    menu.funcion_buscar_series()

    assert llamadas == []


def test_buscar_series_indice_fuera_de_rango(monkeypatch):
    preparar(monkeypatch, "breaking bad", "99", "")
    monkeypatch.setattr(
        series_service,
        "buscar_series",
        lambda n: [{"show": {"id": 169, "name": "Breaking Bad"}}],
    )
    llamadas = []
    monkeypatch.setattr(
        series_service, "obtener_detalles_serie", lambda i: llamadas.append(i)
    )

    menu.funcion_buscar_series()

    assert llamadas == []


def test_buscar_series_entrada_no_numerica_no_crashea(monkeypatch):
    preparar(monkeypatch, "breaking bad", "²", "")
    monkeypatch.setattr(
        series_service,
        "buscar_series",
        lambda n: [{"show": {"id": 169, "name": "Breaking Bad"}}],
    )
    llamadas = []
    monkeypatch.setattr(
        series_service, "obtener_detalles_serie", lambda i: llamadas.append(i)
    )

    menu.funcion_buscar_series()

    assert llamadas == []


def test_buscar_series_sin_resultados(monkeypatch, capsys):
    preparar(monkeypatch, "nadie", "")
    monkeypatch.setattr(series_service, "buscar_series", lambda n: [])

    menu.funcion_buscar_series()

    assert "No se encontraron series" in capsys.readouterr().out


def test_buscar_series_no_captura_api_error(monkeypatch):
    preparar(monkeypatch, "breaking bad", "")

    def falla(nombre):
        raise ApiError("sin conexión")

    monkeypatch.setattr(series_service, "buscar_series", falla)

    with pytest.raises(ApiError):
        menu.funcion_buscar_series()


# --- películas populares y género ---


def test_peliculas_populares_listan_las_cinco(capsys, monkeypatch):
    preparar(monkeypatch, "")

    menu.funcion_peliculas_populares()

    salida = capsys.readouterr().out
    assert "PELÍCULAS POPULARES" in salida
    assert "1. The Shawshank Redemption (1994) - 9.3" in salida
    assert "5. Forrest Gump (1994) - 8.8" in salida


def test_buscar_por_genero_vacio(monkeypatch, capsys):
    preparar(monkeypatch, "", "")
    llamadas = []
    monkeypatch.setattr(
        movie_service, "buscar_peliculas_por_genero", lambda g: llamadas.append(g)
    )

    menu.funcion_buscar_por_genero()

    assert llamadas == []
    assert "Género vacío" in capsys.readouterr().out


def test_buscar_por_genero_comedia(monkeypatch, capsys):
    preparar(monkeypatch, "comedia", "")
    llamadas = []
    monkeypatch.setattr(
        movie_service,
        "buscar_peliculas_por_genero",
        lambda g: llamadas.append(g) or [{"titulo": "Superbad", "anio": 2007, "rating": 7.6}],
    )

    menu.funcion_buscar_por_genero()

    salida = capsys.readouterr().out
    assert llamadas == ["comedia"]
    assert "Géneros disponibles: acción, comedia" in salida
    assert "1. Superbad (2007) - 7.6" in salida


# --- favoritos ---


def test_ver_favoritos_vacios(capsys, monkeypatch):
    preparar(monkeypatch, "")

    menu.funcion_ver_favoritos()

    salida = capsys.readouterr().out
    assert "MIS FAVORITOS" in salida
    assert "No tienes películas favoritas" in salida


def test_ver_favoritos_elimina_la_seleccionada(capsys, monkeypatch):
    preparar(monkeypatch, "1", "")
    movie_service.PELICULAS_FAVORITAS.append(pelicula("The Forest"))
    movie_service.PELICULAS_FAVORITAS.append(pelicula("Memento"))

    menu.funcion_ver_favoritos()

    salida = capsys.readouterr().out
    assert "1. The Forest" in salida
    assert "2. Memento" in salida
    assert "Eliminada de favoritos" in salida
    assert [p["Title"] for p in movie_service.PELICULAS_FAVORITAS] == ["Memento"]


def test_ver_favoritos_con_cero_no_elimina(monkeypatch):
    preparar(monkeypatch, "0", "")
    movie_service.PELICULAS_FAVORITAS.append(pelicula("The Forest"))

    menu.funcion_ver_favoritos()

    assert len(movie_service.PELICULAS_FAVORITAS) == 1


def test_ver_favoritos_indice_fuera_de_rango(monkeypatch):
    preparar(monkeypatch, "99", "")
    movie_service.PELICULAS_FAVORITAS.append(pelicula("The Forest"))

    menu.funcion_ver_favoritos()

    assert len(movie_service.PELICULAS_FAVORITAS) == 1


def test_ver_favoritos_enter_vacio_no_elimina(monkeypatch):
    preparar(monkeypatch, "", "")
    movie_service.PELICULAS_FAVORITAS.append(pelicula("The Forest"))

    menu.funcion_ver_favoritos()

    assert len(movie_service.PELICULAS_FAVORITAS) == 1


def test_ver_favoritos_entrada_no_numerica(monkeypatch):
    preparar(monkeypatch, "²", "")
    movie_service.PELICULAS_FAVORITAS.append(pelicula("The Forest"))

    menu.funcion_ver_favoritos()

    assert len(movie_service.PELICULAS_FAVORITAS) == 1


# --- historial ---


def test_ver_historial_vacio(capsys, monkeypatch):
    preparar(monkeypatch, "")

    menu.funcion_ver_historial()

    salida = capsys.readouterr().out
    assert "HISTORIAL DE BÚSQUEDAS" in salida
    assert "No hay historial" in salida


def test_ver_historial_no_limpiar_con_no(monkeypatch):
    preparar(monkeypatch, "n", "")
    movie_service.agregar_al_historial(pelicula())

    menu.funcion_ver_historial()

    assert len(movie_service.HISTORIAL_BUSQUEDAS) == 1


def test_ver_historial_limpiar_con_s(monkeypatch, capsys):
    preparar(monkeypatch, "s", "")
    movie_service.agregar_al_historial(pelicula())

    menu.funcion_ver_historial()

    assert "Historial limpiado" in capsys.readouterr().out
    assert movie_service.HISTORIAL_BUSQUEDAS == []


def test_ver_historial_limpiar_con_si(monkeypatch):
    preparar(monkeypatch, "SI", "")
    movie_service.agregar_al_historial(pelicula())

    menu.funcion_ver_historial()

    assert movie_service.HISTORIAL_BUSQUEDAS == []


# --- estadísticas ---


def test_estadisticas_imprime_los_totales(capsys, monkeypatch):
    preparar(monkeypatch, "")
    movie_service.agregar_a_favoritas(pelicula())
    movie_service.agregar_al_historial(pelicula("Uno"))
    movie_service.agregar_al_historial(pelicula("Dos"))

    menu.funcion_estadisticas()

    salida = capsys.readouterr().out
    assert "ESTADÍSTICAS" in salida
    assert "Total favoritas: 1" in salida
    assert "Total historial: 2" in salida


# --- exportar ---


def test_exportar_nombre_vacio(monkeypatch, capsys):
    preparar(monkeypatch, "", "")
    llamadas = []
    monkeypatch.setattr(movie_service, "exportar_a_json", lambda n: llamadas.append(n))

    menu.funcion_exportar()

    assert llamadas == []
    assert "Nombre de archivo vacío" in capsys.readouterr().out


def test_exportar_rechaza_slash(monkeypatch, capsys):
    preparar(monkeypatch, "carpeta/datos", "")
    llamadas = []
    monkeypatch.setattr(movie_service, "exportar_a_json", lambda n: llamadas.append(n))

    menu.funcion_exportar()

    assert llamadas == []
    assert "El nombre no puede contener / ni \\" in capsys.readouterr().out


def test_exportar_rechaza_contrabarra(monkeypatch, capsys):
    preparar(monkeypatch, "carpeta\\datos", "")
    llamadas = []
    monkeypatch.setattr(movie_service, "exportar_a_json", lambda n: llamadas.append(n))

    menu.funcion_exportar()

    assert llamadas == []
    assert "El nombre no puede contener / ni \\" in capsys.readouterr().out


def test_exportar_nombre_valido(monkeypatch):
    preparar(monkeypatch, "datos", "")
    llamadas = []
    monkeypatch.setattr(movie_service, "exportar_a_json", lambda n: llamadas.append(n))

    menu.funcion_exportar()

    assert llamadas == ["datos.json"]


# --- importar ---


def test_importar_nombre_vacio(monkeypatch, capsys):
    preparar(monkeypatch, "", "")
    llamadas = []
    monkeypatch.setattr(movie_service, "importar_de_json", lambda n: llamadas.append(n))

    menu.funcion_importar()

    assert llamadas == []
    assert "Nombre de archivo vacío" in capsys.readouterr().out


def test_importar_rechaza_slash(monkeypatch, capsys):
    preparar(monkeypatch, "carpeta/datos", "")
    llamadas = []
    monkeypatch.setattr(movie_service, "importar_de_json", lambda n: llamadas.append(n))

    menu.funcion_importar()

    assert llamadas == []
    assert "El nombre no puede contener / ni \\" in capsys.readouterr().out


def test_importar_nombre_valido(monkeypatch):
    preparar(monkeypatch, "datos", "")
    llamadas = []
    monkeypatch.setattr(movie_service, "importar_de_json", lambda n: llamadas.append(n))

    menu.funcion_importar()

    assert llamadas == ["datos.json"]


def test_importar_error_se_registra_y_no_corta_la_app(monkeypatch, capsys, caplog):
    preparar(monkeypatch, "roto", "")

    def falla(nombre):
        raise DataImportError(f"JSON inválido en {nombre}")

    monkeypatch.setattr(movie_service, "importar_de_json", falla)

    with caplog.at_level(logging.ERROR, logger="ui.menu"):
        menu.funcion_importar()

    salida = capsys.readouterr().out
    assert "Error al importar archivo" in salida
    assert "Error al importar archivo" in caplog.text


# --- configuración ---


def test_config_tiene_los_valores_por_defecto():
    assert CONFIG == {"debug": True, "verbose": True, "timeout": 30, "max_retries": 3}


def test_configuracion_volver_sin_cambios(capsys, monkeypatch):
    preparar(monkeypatch, "0", "")
    antes = dict(CONFIG)

    menu.funcion_configuracion()

    assert "Opción inválida" not in capsys.readouterr().out
    assert CONFIG == antes


def test_configuracion_opcion_invalida(capsys, monkeypatch):
    preparar(monkeypatch, "9", "")

    menu.funcion_configuracion()

    assert "Opción inválida" in capsys.readouterr().out


def test_configuracion_texto_no_numerico(capsys, monkeypatch):
    preparar(monkeypatch, "abc", "")

    menu.funcion_configuracion()

    assert "Opción inválida" in capsys.readouterr().out


def test_configuracion_alterna_debug(monkeypatch, capsys):
    preparar(monkeypatch, "1", "")
    inicial = CONFIG["debug"]

    menu.funcion_configuracion()

    assert CONFIG["debug"] is not inicial
    assert f"Debug ahora es: {not inicial}" in capsys.readouterr().out


def test_configuracion_alterna_verbose(monkeypatch, capsys):
    preparar(monkeypatch, "2", "")
    inicial = CONFIG["verbose"]

    menu.funcion_configuracion()

    assert CONFIG["verbose"] is not inicial
    assert f"Verbose ahora es: {not inicial}" in capsys.readouterr().out


def test_configuracion_timeout_valido(monkeypatch, capsys):
    preparar(monkeypatch, "3", "45", "")
    anterior = CONFIG["timeout"]

    menu.funcion_configuracion()

    assert CONFIG["timeout"] == 45
    assert CONFIG["timeout"] != anterior
    assert "CONFIGURACIÓN" in capsys.readouterr().out


def test_configuracion_timeout_con_espacios(monkeypatch):
    preparar(monkeypatch, "3", " 45 ", "")

    menu.funcion_configuracion()

    assert CONFIG["timeout"] == 45


def test_configuracion_timeout_cero(monkeypatch, capsys):
    preparar(monkeypatch, "3", "0", "")
    anterior = CONFIG["timeout"]

    menu.funcion_configuracion()

    assert CONFIG["timeout"] == anterior
    assert "Timeout inválido: debe ser un entero >= 1" in capsys.readouterr().out


def test_configuracion_timeout_negativo(monkeypatch, capsys):
    preparar(monkeypatch, "3", "-5", "")
    anterior = CONFIG["timeout"]

    menu.funcion_configuracion()

    assert CONFIG["timeout"] == anterior
    assert "Timeout inválido: debe ser un entero >= 1" in capsys.readouterr().out


def test_configuracion_timeout_texto(monkeypatch, capsys):
    preparar(monkeypatch, "3", "abc", "")
    anterior = CONFIG["timeout"]

    menu.funcion_configuracion()

    assert CONFIG["timeout"] == anterior
    assert "Timeout inválido: debe ser un entero >= 1" in capsys.readouterr().out


# --- menu_principal ---


@pytest.mark.parametrize(
    "entradas",
    [
        ["1", "", "", "12"],
        ["2", "", "", "12"],
        ["3", "", "", "12"],
        ["4", "", "12"],
        ["5", "", "", "12"],
        ["6", "", "12"],
        ["7", "", "12"],
        ["8", "", "12"],
        ["9", "", "", "12"],
        ["10", "", "", "12"],
        ["11", "0", "", "12"],
        ["12"],
    ],
    ids=[
        "buscar_pelicula",
        "buscar_actor",
        "buscar_series",
        "populares",
        "genero",
        "favoritos",
        "historial",
        "estadisticas",
        "exportar",
        "importar",
        "configuracion",
        "salir",
    ],
)
def test_menu_despacha_cada_opcion_y_sale(monkeypatch, capsys, entradas):
    preparar(monkeypatch, *entradas)

    menu.menu_principal()

    assert "¡Hasta luego!" in capsys.readouterr().out


def test_menu_con_opcion_invalida(monkeypatch, capsys):
    preparar(monkeypatch, "99", "12")

    menu.menu_principal()

    salida = capsys.readouterr().out
    assert "Opción inválida" in salida
    assert "¡Hasta luego!" in salida


def test_menu_muestra_las_doce_opciones(monkeypatch, capsys):
    preparar(monkeypatch, "12")

    menu.menu_principal()

    salida = capsys.readouterr().out
    assert "SISTEMA DE PELÍCULAS Y SERIES" in salida
    for numero in range(1, 13):
        assert f"{numero}. " in salida
    assert salida.count(SEPARADOR) >= 1
