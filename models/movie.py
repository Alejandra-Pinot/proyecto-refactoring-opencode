# Modelos de película (representación de tipos; runtime = dict)
from typing import TypedDict


class Movie(TypedDict, total=False):
    """Detalle de película OMDB realmente usado por el proyecto."""
    Title: str
    Year: str
    imdbRating: str
    Genre: str
    Director: str
    Actors: str
    Plot: str
    Country: str
    Awards: str
    Response: str


class MovieListItem(TypedDict, total=False):
    """Ítem de lista de películas (hardcodeado u OMDB)."""
    titulo: str
    anio: int
    rating: float
    Title: str
    Year: str
