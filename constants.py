# Constantes del proyecto (Fase 2)

# API keys restantes (OMDB_API_KEY se lee de variables de entorno en api/omdb.py)
API_KEY_TMDB = ""  # Vacía porque no la usamos correctamente

# URLs base de las APIs
BASE_URL_OMDB = "http://www.omdbapi.com/"
BASE_URL_TMDB = "https://api.themoviedb.org/3/"
BASE_URL_TVMAZE = "http://api.tvmaze.com"

# Valores de la API OMDB
OMDB_RESPONSE_TRUE = "True"
OMDB_TYPE_MOVIE = "movie"

# Caché de series
SERIES_CACHE_PREFIX = "series_"

# Historial de búsquedas
HISTORY_DATE_PLACEHOLDER = "hoy"

# Películas populares (datos hardcodeados)
POPULAR_MOVIES = [
    {"titulo": "The Shawshank Redemption", "anio": 1994, "rating": 9.3},
    {"titulo": "The Godfather", "anio": 1972, "rating": 9.2},
    {"titulo": "The Dark Knight", "anio": 2008, "rating": 9.0},
    {"titulo": "Pulp Fiction", "anio": 1994, "rating": 8.9},
    {"titulo": "Forrest Gump", "anio": 1994, "rating": 8.8},
]

# Películas por género (datos hardcodeados)
GENRE_ACTION_MOVIES = [
    {"titulo": "Die Hard", "anio": 1988, "rating": 8.2},
    {"titulo": "Mad Max Fury Road", "anio": 2015, "rating": 8.1},
]
GENRE_COMEDIA_MOVIES = [
    {"titulo": "Superbad", "anio": 2007, "rating": 7.6},
    {"titulo": "The Hangover", "anio": 2009, "rating": 7.7},
]

# Presentación de la interfaz de consola
SEPARATOR_CHAR = "="
SEPARATOR_WIDTH = 60
MENU_DELAY_SECONDS = 1
SUMMARY_MAX_LENGTH = 200
