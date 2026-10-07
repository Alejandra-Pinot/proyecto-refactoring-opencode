# Configuración central del programa (Fase 2)
# Reemplaza a los archivos *_config.py como única fuente de configuración.
# El mismo objeto dict es compartido por config.py, api_movies.py y main.py:
# las mutaciones en el menú de configuración deben seguir siendo visibles
# en hacer_request (no copiar este dict).

CONFIG = {
    "debug": True,
    "verbose": True,
    "timeout": 30,
    "max_retries": 3,
}
