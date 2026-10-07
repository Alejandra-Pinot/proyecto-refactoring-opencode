# Visualización de la interfaz de consola
from typing import Any

from constants import SEPARATOR_CHAR, SEPARATOR_WIDTH, SUMMARY_MAX_LENGTH
from models.movie import Movie, MovieListItem
from models.series import SeriesShow


def print_separator() -> None:
    """Imprime separador"""
    print(SEPARATOR_CHAR * SEPARATOR_WIDTH)


def print_header(text: str) -> None:
    """Imprime header"""
    print_separator()
    print(text.upper().center(SEPARATOR_WIDTH))
    print_separator()


def mostrar_pelicula(pelicula: Movie | None) -> None:
    """Muestra película sin validación"""
    print_separator()
    if pelicula is None:
        print("No se encontró la película")
        return

    # Acceso directo a diccionario sin get()
    try:
        print(f"Título: {pelicula['Title']}")
    except KeyError:
        print("Título: N/A")

    try:
        print(f"Año: {pelicula['Year']}")
    except KeyError:
        print("Año: N/A")

    try:
        print(f"Rating IMDB: {pelicula['imdbRating']}")
    except KeyError:
        print("Rating: N/A")

    try:
        print(f"Género: {pelicula['Genre']}")
    except KeyError:
        print("Género: N/A")

    try:
        print(f"Director: {pelicula['Director']}")
    except KeyError:
        print("Director: N/A")

    try:
        print(f"Actores: {pelicula['Actors']}")
    except KeyError:
        print("Actores: N/A")

    try:
        print(f"Trama: {pelicula['Plot']}")
    except KeyError:
        print("Trama: N/A")

    try:
        print(f"País: {pelicula['Country']}")
    except KeyError:
        print("País: N/A")

    try:
        print(f"Premios: {pelicula['Awards']}")
    except KeyError:
        print("Premios: N/A")

    print_separator()


def mostrar_serie(serie: SeriesShow | dict[str, Any]) -> None:
    """Muestra serie"""
    print_separator()
    show = serie.get("show", serie)

    print(f"Nombre: {show.get('name', 'N/A')}")
    print(f"Idioma: {show.get('language', 'N/A')}")
    print(f"Géneros: {show.get('genres', [])}")
    print(f"Rating: {show.get('rating', {}).get('average', 'N/A')}")
    print(f"Estado: {show.get('status', 'N/A')}")
    print(f"Estreno: {show.get('premiered', 'N/A')}")
    print(f"Final: {show.get('ended', 'N/A')}")
    print(f"Episodios: {show.get('runtime', 'N/A')}")
    resumen = str(show.get("summary", "N/A"))
    print(f"Resumen: {resumen[:SUMMARY_MAX_LENGTH]}...")
    print_separator()


def mostrar_lista_peliculas(peliculas: list[MovieListItem]) -> None:
    """Muestra lista de películas"""
    i = 0
    while i < len(peliculas):
        if "titulo" in peliculas[i]:
            print(f"{i + 1}. {peliculas[i]['titulo']} ({peliculas[i]['anio']}) - {peliculas[i]['rating']}")
        elif "Title" in peliculas[i]:
            print(f"{i + 1}. {peliculas[i]['Title']} ({peliculas[i].get('Year', 'N/A')})")
        else:
            print(f"{i + 1}. Película desconocida")
        i += 1
