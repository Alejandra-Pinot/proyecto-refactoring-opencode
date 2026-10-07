# Modelos de serie (representación de tipos; runtime = dict)
from typing import TypedDict


class SeriesRating(TypedDict, total=False):
    average: float | int | None


class SeriesShow(TypedDict, total=False):
    """Show de TVMaze realmente usado por el proyecto."""
    id: int
    name: str
    language: str
    genres: list
    rating: SeriesRating
    status: str
    premiered: str
    ended: str
    runtime: int
    summary: str | None


class SeriesSearchItem(TypedDict, total=False):
    """Ítem de resultados de búsqueda de TVMaze."""
    show: SeriesShow
