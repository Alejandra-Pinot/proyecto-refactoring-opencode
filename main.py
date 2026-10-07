# Punto de entrada de la aplicación
import logging
import sys

from config import CONFIG
from ui.menu import menu_principal


def setup_logging() -> None:
    """Configura logging estándar (stdout; sin fichero)"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


# Programa principal
if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido")
        sys.exit(0)
    except Exception as e:
        logger.exception("Error inesperado")
        print(f"Error inesperado: {e}")
        sys.exit(1)
