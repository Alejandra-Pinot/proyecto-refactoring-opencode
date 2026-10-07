# Tests unitarios de ui/display.py
from constants import SEPARATOR_CHAR, SEPARATOR_WIDTH, SUMMARY_MAX_LENGTH
from ui import display


def test_print_separator_usa_el_ancho_de_constants(capsys):
    display.print_separator()

    assert capsys.readouterr().out == f"{SEPARATOR_CHAR * SEPARATOR_WIDTH}\n"


def test_print_header_centra_el_texto_en_mayusculas(capsys):
    display.print_header("hola")

    lineas = capsys.readouterr().out.splitlines()
    assert lineas[0] == SEPARATOR_CHAR * SEPARATOR_WIDTH
    assert lineas[1] == "HOLA".center(SEPARATOR_WIDTH)
    assert lineas[2] == SEPARATOR_CHAR * SEPARATOR_WIDTH
    assert len(lineas) == 3


def test_mostrar_pelicula_none(capsys):
    display.mostrar_pelicula(None)

    salida = capsys.readouterr().out
    assert "No se encontró la película" in salida
    assert salida.count(SEPARATOR_CHAR * SEPARATOR_WIDTH) == 1


def test_mostrar_pelicula_completa(capsys):
    pelicula = {
        "Title": "The Forest",
        "Year": "2016",
        "imdbRating": "4.8",
        "Genre": "Horror",
        "Director": "Jason Zada",
        "Actors": "Natalie Dormer",
        "Plot": "Una mujer viaja al bosque",
        "Country": "USA",
        "Awards": "Ninguno",
    }

    display.mostrar_pelicula(pelicula)

    salida = capsys.readouterr().out
    assert "Título: The Forest" in salida
    assert "Año: 2016" in salida
    assert "Rating IMDB: 4.8" in salida
    assert "Género: Horror" in salida
    assert "Director: Jason Zada" in salida
    assert "Actores: Natalie Dormer" in salida
    assert "Trama: Una mujer viaja al bosque" in salida
    assert "País: USA" in salida
    assert "Premios: Ninguno" in salida


def test_mostrar_pelicula_vacia_imprime_na_en_todos_los_campos(capsys):
    display.mostrar_pelicula({})

    salida = capsys.readouterr().out
    assert "Título: N/A" in salida
    assert "Año: N/A" in salida
    assert "Rating: N/A" in salida
    assert "Género: N/A" in salida
    assert "Director: N/A" in salida
    assert "Actores: N/A" in salida
    assert "Trama: N/A" in salida
    assert "País: N/A" in salida
    assert "Premios: N/A" in salida


def test_mostrar_serie_envuelta_en_show(capsys):
    serie = {
        "show": {
            "name": "Breaking Bad",
            "language": "English",
            "genres": ["Drama", "Crime"],
            "rating": {"average": 9.4},
            "status": "Ended",
            "premiered": "2008-01-20",
            "ended": "2013-09-29",
            "runtime": 45,
            "summary": "Un profesor de química.",
        }
    }

    display.mostrar_serie(serie)

    salida = capsys.readouterr().out
    assert "Nombre: Breaking Bad" in salida
    assert "Idioma: English" in salida
    assert "Géneros: ['Drama', 'Crime']" in salida
    assert "Rating: 9.4" in salida
    assert "Estado: Ended" in salida
    assert "Estreno: 2008-01-20" in salida
    assert "Final: 2013-09-29" in salida
    assert "Episodios: 45" in salida
    assert "Resumen: Un profesor de química...." in salida


def test_mostrar_serie_directa_y_resumen_largo(capsys):
    resumen = "x" * (SUMMARY_MAX_LENGTH + 50)

    display.mostrar_serie({"name": "The Wire", "summary": resumen})

    salida = capsys.readouterr().out
    assert "Nombre: The Wire" in salida
    assert f"Resumen: {'x' * SUMMARY_MAX_LENGTH}..." in salida
    assert len(resumen[:SUMMARY_MAX_LENGTH] + "...") < len(resumen)


def test_mostrar_serie_vacia_imprime_na(capsys):
    display.mostrar_serie({})

    salida = capsys.readouterr().out
    assert "Nombre: N/A" in salida
    assert "Idioma: N/A" in salida
    assert "Géneros: []" in salida
    assert "Rating: N/A" in salida
    assert "Estado: N/A" in salida
    assert "Estreno: N/A" in salida
    assert "Final: N/A" in salida
    assert "Episodios: N/A" in salida
    assert "Resumen: N/A..." in salida


def test_mostrar_lista_con_formato_hardcodeado(capsys):
    display.mostrar_lista_peliculas(
        [
            {"titulo": "Die Hard", "anio": 1988, "rating": 8.2},
            {"titulo": "Superbad", "anio": 2007, "rating": 7.6},
        ]
    )

    lineas = capsys.readouterr().out.splitlines()
    assert lineas == ["1. Die Hard (1988) - 8.2", "2. Superbad (2007) - 7.6"]


def test_mostrar_lista_formato_omdb(capsys):
    display.mostrar_lista_peliculas(
        [{"Title": "Forrest Gump", "Year": "1994"}, {"Title": "Memento"}]
    )

    lineas = capsys.readouterr().out.splitlines()
    assert lineas == ["1. Forrest Gump (1994)", "2. Memento (N/A)"]


def test_mostrar_lista_elemento_desconocido(capsys):
    display.mostrar_lista_peliculas([{"otra": "clave"}, {"Title": "Ok"}])

    lineas = capsys.readouterr().out.splitlines()
    assert lineas == ["1. Película desconocida", "2. Ok (N/A)"]


def test_mostrar_lista_vacia_no_imprime_nada(capsys):
    display.mostrar_lista_peliculas([])

    assert capsys.readouterr().out == ""
