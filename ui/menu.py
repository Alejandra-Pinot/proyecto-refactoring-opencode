# Menú principal y handlers de opciones
import logging
import os
import time

from config import CONFIG
from constants import MENU_DELAY_SECONDS
from exceptions import ApiError, DataImportError
from services import movie_service, series_service
from ui.display import (
    mostrar_lista_peliculas,
    mostrar_pelicula,
    mostrar_serie,
    print_header,
)

logger = logging.getLogger(__name__)


def clear_screen() -> None:
    """Limpia pantalla de forma no portable"""
    os.system('cls' if os.name == 'nt' else 'clear')


def delay(seconds: float) -> None:
    """Delay innecesario"""
    time.sleep(seconds)


def funcion_buscar_pelicula() -> None:
    """Busca película"""
    titulo = input("Ingrese el título de la película: ").strip()
    if not titulo:
        print("Título vacío")
    else:
        print("Buscando...")
        delay(MENU_DELAY_SECONDS)  # Simular carga innecesaria

        try:
            pelicula = movie_service.buscar_pelicula(titulo)
        except ApiError as e:
            logger.error("Error en búsqueda OMDB: %s", e)
            print(f"Error: {e}")
        else:
            mostrar_pelicula(pelicula)

            if pelicula is not None:
                movie_service.agregar_al_historial(pelicula)
                opcion = input("\n¿Agregar a favoritos? (s/n): ")
                if opcion.strip().lower() in ("s", "si"):
                    if movie_service.agregar_a_favoritas(pelicula):
                        print("¡Agregada a favoritos!")
                    else:
                        print("Ya está en favoritos")

    input("\nPresione Enter para continuar...")


def funcion_buscar_actor() -> None:
    """Busca actor"""
    actor = input("Ingrese el nombre del actor: ").strip()
    if not actor:
        print("Nombre de actor vacío")
    else:
        print("Buscando películas del actor...")

        try:
            peliculas = movie_service.buscar_peliculas_por_actor(actor)

            if len(peliculas) > 0:
                mostrar_lista_peliculas(peliculas)

                opcion = input("\nSeleccione una película para ver detalles (0 para volver): ")
                if opcion.isdecimal():
                    indice = int(opcion) - 1
                    if indice >= 0 and indice < len(peliculas):
                        detalles = movie_service.buscar_pelicula(peliculas[indice]["Title"])
                        mostrar_pelicula(detalles)
            else:
                print("No se encontraron películas para ese actor")
        except ApiError as e:
            logger.error("Error en búsqueda OMDB: %s", e)
            print(f"Error: {e}")

    input("\nPresione Enter para continuar...")


def funcion_buscar_series() -> None:
    """Busca series"""
    nombre = input("Ingrese el nombre de la serie: ").strip()
    if not nombre:
        print("Nombre de serie vacío")
    else:
        print("Buscando series...")

        series = series_service.buscar_series(nombre)

        if len(series) > 0:
            i = 0
            while i < len(series):
                show = series[i].get("show", {})
                print(f"{i + 1}. {show.get('name', '')} ({show.get('status', '')})")
                i += 1

            opcion = input("\nSeleccione una serie para ver detalles (0 para volver): ")
            if opcion.isdecimal():
                indice = int(opcion) - 1
                if indice >= 0 and indice < len(series):
                    id_serie = series[indice].get("show", {}).get("id")
                    detalles = series_service.obtener_detalles_serie(id_serie)
                    mostrar_serie(detalles)
        else:
            print("No se encontraron series")

    input("\nPresione Enter para continuar...")


def funcion_peliculas_populares() -> None:
    """Muestra películas populares"""
    print_header("PELÍCULAS POPULARES")
    peliculas = movie_service.obtener_peliculas_populares()
    mostrar_lista_peliculas(peliculas)
    input("\nPresione Enter para continuar...")


def funcion_buscar_por_genero() -> None:
    """Busca por género"""
    print("Géneros disponibles: acción, comedia")
    genero = input("Ingrese el género: ").strip()
    if not genero:
        print("Género vacío")
    else:
        print("Buscando...")

        peliculas = movie_service.buscar_peliculas_por_genero(genero)
        mostrar_lista_peliculas(peliculas)

    input("\nPresione Enter para continuar...")


def funcion_ver_favoritos() -> None:
    """Muestra favoritas"""
    print_header("MIS FAVORITOS")
    favoritas = movie_service.PELICULAS_FAVORITAS
    if len(favoritas) > 0:
        i = 0
        while i < len(favoritas):
            print(f"{i + 1}. {favoritas[i].get('Title', '')}")
            i += 1

        opcion = input("\n¿Desea eliminar alguna? (número o Enter para volver): ")
        if opcion.isdecimal():
            indice = int(opcion) - 1
            if indice >= 0 and indice < len(favoritas):
                titulo = favoritas[indice].get("Title")
                if movie_service.eliminar_de_favoritas(titulo):
                    print("Eliminada de favoritos")
    else:
        print("No tienes películas favoritas")

    input("\nPresione Enter para continuar...")


def funcion_ver_historial() -> None:
    """Muestra historial"""
    print_header("HISTORIAL DE BÚSQUEDAS")
    historial = movie_service.HISTORIAL_BUSQUEDAS
    if len(historial) > 0:
        i = 0
        while i < len(historial):
            print(f"{i + 1}. {historial[i]['titulo']}")
            i += 1

        opcion = input("\n¿Limpiar historial? (s/n): ")
        if opcion.strip().lower() in ("s", "si"):
            movie_service.limpiar_historial()
            print("Historial limpiado")
    else:
        print("No hay historial")

    input("\nPresione Enter para continuar...")


def funcion_estadisticas() -> None:
    """Muestra estadísticas"""
    print_header("ESTADÍSTICAS")
    stats = movie_service.obtener_estadisticas()
    print(f"Total favoritas: {stats['total_favoritas']}")
    print(f"Total historial: {stats['total_historial']}")
    input("\nPresione Enter para continuar...")


def funcion_exportar() -> None:
    """Exporta datos"""
    nombre = input("Nombre del archivo (sin extensión): ").strip()
    if not nombre:
        print("Nombre de archivo vacío")
    elif "/" in nombre or "\\" in nombre:
        print("El nombre no puede contener / ni \\")
    else:
        movie_service.exportar_a_json(nombre + ".json")
    input("\nPresione Enter para continuar...")


def funcion_importar() -> None:
    """Importa datos"""
    nombre = input("Nombre del archivo (sin extensión): ").strip()
    if not nombre:
        print("Nombre de archivo vacío")
    elif "/" in nombre or "\\" in nombre:
        print("El nombre no puede contener / ni \\")
    else:
        try:
            movie_service.importar_de_json(nombre + ".json")
        except DataImportError:
            logger.exception("Error al importar archivo")
            print("Error al importar archivo")
    input("\nPresione Enter para continuar...")


def funcion_configuracion() -> None:
    """Configuración"""
    print_header("CONFIGURACIÓN")
    print(f"1. Debug: {CONFIG['debug']}")
    print(f"2. Verbose: {CONFIG['verbose']}")
    print(f"3. Timeout: {CONFIG['timeout']}")

    opcion = input("\nSeleccione opción a cambiar (0 para volver): ")
    if opcion == "1":
        CONFIG["debug"] = not CONFIG["debug"]
        print(f"Debug ahora es: {CONFIG['debug']}")
    elif opcion == "2":
        CONFIG["verbose"] = not CONFIG["verbose"]
        print(f"Verbose ahora es: {CONFIG['verbose']}")
    elif opcion == "3":
        texto = input("Nuevo timeout: ").strip()
        if not texto.isdecimal() or int(texto) < 1:
            print("Timeout inválido: debe ser un entero >= 1")
        else:
            CONFIG["timeout"] = int(texto)
    elif opcion == "0":
        pass  # Volver al menú
    else:
        print("Opción inválida")

    input("\nPresione Enter para continuar...")


def menu_principal() -> None:
    """Menú principal"""
    while True:
        clear_screen()
        print_header("SISTEMA DE PELÍCULAS Y SERIES")
        print("1. Buscar película por título")
        print("2. Buscar por actor")
        print("3. Buscar series")
        print("4. Ver películas populares")
        print("5. Buscar por género")
        print("6. Ver favoritos")
        print("7. Ver historial")
        print("8. Ver estadísticas")
        print("9. Exportar datos")
        print("10. Importar datos")
        print("11. Configuración")
        print("12. Salir")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            funcion_buscar_pelicula()
        elif opcion == "2":
            funcion_buscar_actor()
        elif opcion == "3":
            funcion_buscar_series()
        elif opcion == "4":
            funcion_peliculas_populares()
        elif opcion == "5":
            funcion_buscar_por_genero()
        elif opcion == "6":
            funcion_ver_favoritos()
        elif opcion == "7":
            funcion_ver_historial()
        elif opcion == "8":
            funcion_estadisticas()
        elif opcion == "9":
            funcion_exportar()
        elif opcion == "10":
            funcion_importar()
        elif opcion == "11":
            funcion_configuracion()
        elif opcion == "12":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida")
            delay(MENU_DELAY_SECONDS)
