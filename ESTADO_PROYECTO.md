# Estado del proyecto - Refactoring Películas y Series

## Estado actual

Fases 1, 2, 3, 4, 5 y 6 completadas y validadas.

Proyecto finalizado: código refactorizado, seguro y con suite de tests
(176 tests, cobertura 100% sobre el flujo de producción).

---

## Fase 1 - Análisis

Completada.

Se realizó:
- Identificación de variables globales.
- Mapeo de dependencias.
- Identificación de código duplicado.
- Identificación de bare except y manejo deficiente de errores.
- Revisión de archivos *_config.py sin uso.

---

## Fase 2 - Refactorización inicial

Completada.

Cambios principales:
- Creación de config.py.
- Creación de constants.py.
- Eliminación de imports wildcard.
- Uso de f-strings.
- Incorporación de type hints.
- Eliminación de 88 archivos *_config.py que no participaban en el flujo de la aplicación.

La aplicación continuó funcionando después de los cambios.

---

## Fase 3 - Separación por capas

Completada y validada.

Arquitectura actual:

main
  ↓
ui
  ↓
services
  ↓
api

Estructura creada:

api/
- omdb.py
- tvmaze.py

services/
- movie_service.py
- series_service.py

models/
- movie.py
- series.py

ui/
- menu.py
- display.py

main.py quedó como punto de entrada.

api_movies.py fue eliminado después de verificar la migración.

OMDB y TVMaze permanecen independientes.

El estado mutable de películas permanece centralizado en movie_service.py.

Validaciones realizadas:
- py_compile OK.
- OMDB OK.
- TVMaze OK.
- Favoritos OK.
- Historial OK.
- Caché OK.
- Estado compartido OK.

---

## Fase 4 - Excepciones y logging

COMPLETADA Y VALIDADA.

Se creó:

exceptions.py

Excepciones:

- AppError
- ApiError
- DataImportError
- DataExportError

### Manejo de API

api/omdb.py y api/tvmaze.py:

- requests.exceptions.RequestException se transforma en ApiError.
- ValueError al procesar response.json() se transforma en ApiError.
- Se conserva la excepción original mediante:

raise ApiError(...) from e

No se agregó:
- raise_for_status()
- reintentos
- nuevas dependencias.

### Bare except

Se eliminaron los 10 bare except del flujo principal.

ui/display.py:
- 9 bare except reemplazados por except KeyError.

ui/menu.py:
- bare except de funcion_importar reemplazado por DataImportError.

Los bare except existentes en archivos huérfanos quedaron fuera del alcance de esta fase.

### Logging

Se utiliza logging de la librería estándar.

Los 5 print DEBUG fueron reemplazados:

api/omdb.py:
- Haciendo request.
- Status code.

api/tvmaze.py:
- Haciendo request.
- Status code.

services/movie_service.py:
- Usando cache.

Se mantiene:

CONFIG["debug"]
CONFIG["verbose"]

Los toggles continúan funcionando dinámicamente.

Los mensajes de interfaz continúan utilizando print.

logger.exception se utiliza únicamente donde corresponde manejar el error:
- ui/menu.py para DataImportError.
- main.py como red final para errores inesperados.

No se duplica el logging durante la propagación.

---

## Validaciones manuales de Fase 4

### OMDB

Búsqueda:

forest

Resultado:
The Forest (2016)

Request realizado correctamente.

### Caché

Se volvió a buscar:

forest

Resultado:

DEBUG services.movie_service: Usando cache para forest

No se realizó una segunda petición a OMDB.

### TVMaze

Búsqueda de serie realizada correctamente.

Se seleccionó una serie y se obtuvieron sus detalles mediante TVMaze.

### Manejo de error de importación

Se intentó importar:

archivo_que_no_existe

Flujo comprobado:

FileNotFoundError
→ DataImportError
→ ui.menu captura el error
→ logger.exception registra el traceback
→ se muestra "Error al importar archivo"

La aplicación continuó funcionando después del error.

---

## Validaciones automáticas Fase 4

- py_compile: OK.
- Bare except en flujo principal: 0.
- print DEBUG en api/ y services/: 0.
- except Exception permitido únicamente en main.py como red final.
- requirements.txt sin cambios.
- OMDB OK.
- TVMaze OK.
- Caché OK.
- Importación/exportación OK.
- debug/verbose OK.

---

## Fase 5 - Seguridad

COMPLETADA Y VALIDADA.

Requisitos cumplidos:
1. API key de OMDB movida a variable de entorno.
2. Datos hardcodeados sensibles eliminados del código.
3. Validación de entradas añadida.

### Credencial OMDB

- constants.py: se eliminó API_KEY_OMDB (literal hardcodeado).
- api/omdb.py: lee OMDB_API_KEY con os.getenv (librería estándar, sin dependencias).
- api/omdb.py: si la variable falta o está vacía, hace raise ApiError
  antes de hacer la petición.
- ui/menu.py: funcion_buscar_pelicula y funcion_buscar_actor capturan ese
  ApiError con logger.error (sin traceback) + print y continúan al menú.
  La aplicación NO se cierra y TVMaze/funciones locales siguen operativas.
- No se creó ninguna excepción nueva.

### Fuga de credencial en logs (resuelta)

- Las peticiones OMDB pasan a construirse con params, no con f-string en la URL.
- logger.debug y los mensajes de ApiError ya no incluyen la clave.
- Nunca se registra el valor de OMDB_API_KEY.

### Archivos nuevos

- .env.example (solo con OMDB_API_KEY=<tu_clave_omdb>).
- No se creó ningún .env con claves reales.

### Validación de entradas (ui/menu.py)

- Timeout: únicamente entero >= 1; entrada inválida conserva
  CONFIG["timeout"] y no cierra la aplicación.
- Índices de película/serie/favorita: isdigit() → isdecimal()
  (evita ValueError con caracteres como ²).
- Título, actor, serie y género vacíos: mensaje de validación y sin petición.
- Respuestas s/n: acepta "s" y "si" (strip + lower); resto = NO.
- Nombres de archivo: se rechazan vacíos, "/" y "\".
  Extensión .json y manejo de DataImportError/DataExportError sin cambios.
- Menú de configuración: opción desconocida muestra "Opción inválida";
  la opción 0 sigue significando volver (sin mensaje).
- Menú principal: 12 opciones intactas, sin cambios.

### README

- Se eliminó la documentación de la key literal.
- Se explica que OMDB requiere OMDB_API_KEY como variable de entorno
  y que TVMaze no requiere API key.

### Fuera de alcance de la Fase 5 (documentado)

- Archivos huérfanos (incluidas copias de la key y contraseñas en texto plano).
- Captura adicional de DataExportError.
- Limpieza de código muerto (API_KEY_TMDB, BASE_URL_TMDB, USUARIO_LOGUEADO).
- Fase 6 (tests, pytest, coverage).

---

## Validaciones de Fase 5

### Automáticas

- py_compile del flujo principal: OK.
- Valor literal de la key en el flujo + README: 0 coincidencias.
- La clave no aparece en logs ni en mensajes de error durante la ejecución.
- Bare except en el flujo principal: 0.
- except Exception únicamente en main.py como red final.
- requirements.txt sin cambios (solo se agregó `os`, estándar).
- Menú principal: 12 opciones.
- No existe .env con claves reales; .env.example solo con placeholder.

### Manuales (con y sin OMDB_API_KEY)

- Arranque con variable: OK. Sin variable: menú operativo.
- OMDB con la clave desde entorno: búsqueda correcta.
- Sin la clave: "Error: Falta la variable de entorno OMDB_API_KEY",
  sin traceback, la app continúa.
- TVMaze sin credenciales: búsqueda y detalle correctos.
- Caché: segunda búsqueda sin petición ("Usando cache").
- Timeout inválido (abc, 0, -5): conserva el valor previo.
- Timeout válido (45): aplicado y funcional.
- Selecciones no numéricas/fuera de rango: sin cierre de aplicación.
- Entradas vacías (título, actor, serie, género, archivo): mensaje sin petición.
- Export/import válido: idéntico al comportamiento previo.
- Export con "../salida" o vacío: rechazado, sin escribir fuera del directorio.
- Import de archivo inexistente: DataImportError capturado, app continúa.
- Favoritas, historial y estadísticas: sin regresiones.
- Géneros: acción, comedia y desconocido (fallback) sin cambios.

---

## Fase 6 - Testing (pytest + coverage)

COMPLETADA Y VALIDADA.

Plan aprobado con las decisiones D1-D11:

- D1: pytest>=8.0 y pytest-cov>=5.0 añadidos a requirements.txt.
- D2: mismo intérprete (Python 3.12.8); sin .venv.
- D3: tests de ui/display.py, ui/menu.py y main.py incluidos.
- D4: tests unitarios de api/omdb.py y api/tvmaze.py con mocks,
  separados de la integración real.
- D5: pytest.ini en la raíz (testpaths=tests, pythonpath=.,
  addopts="-ra --strict-markers"; los flags de coverage NO van en addopts).
- D6: markers unit e integration (asignados por carpeta en conftest).
- D7: flags de coverage explícitos en el comando.
- D8: estructura tests/ con unit/ e integration/.
- D9: este archivo se actualiza solo al final, tras las validaciones.
- D10: test_main.py arranca main.py con runpy sin modificarlo.
- D11: asserts estructurales/estables en integración.

Ajuste de seguridad: el valor de OMDB_API_KEY nunca se imprimió, copió,
ni hardcodeó en tests, comandos, documentación, logs ni reportes.

### Estructura creada

pytest.ini
tests/
  __init__.py
  conftest.py            (aislamiento de estado mutable y de CONFIG)
  unit/
    __init__.py
    conftest.py          (barrera de red: ninguna petición real)
    test_movie_service.py
    test_series_service.py
    test_omdb.py
    test_tvmaze.py
    test_display.py
    test_menu.py
    test_main.py
  integration/
    __init__.py
    test_omdb_api.py     (skipif si falta OMDB_API_KEY → SKIPPED)
    test_tvmaze_api.py

Archivos modificados:
- requirements.txt (pytest>=8.0, pytest-cov>=5.0)
- ESTADO_PROYECTO.md (solo este documento, al final)

Código de producción: NO modificado en la Fase 6.
Archivos huérfanos: NO tocados.

### Recuento de tests (176 en total)

- tests/unit: 163
  - test_menu 70, test_movie_service 39, test_omdb 17, test_tvmaze 13,
    test_display 12, test_series_service 8, test_main 4
- tests/integration: 13
  - test_omdb_api 7, test_tvmaze_api 6

Resultado por defecto (sin variable de entorno):
169 passed, 7 skipped, 0 failed.
Los 7 skipped son los de OMDB cuando OMDB_API_KEY no está definida.

---

## Validaciones de Fase 6 (las 20 del plan)

1. py_compile de producción: OK.
2. Suite completa: 169 passed, 7 skipped, 0 failed.
3. Solo unitarios: 163 passed.
4. Solo integración: 6 passed (TVMaze) + 7 skipped (OMDB sin clave).
5. Unitarios sin Internet: OK. Barrera en tests/unit/conftest.py
   (Session.request bloqueada) + ejecución con proxies muertos.
6. OMDB con OMDB_API_KEY: 7 passed (API real; la clave se aportó en
   tiempo de ejecución, sin imprimirla ni escribirla).
7. OMDB sin OMDB_API_KEY: 7 SKIPPED, 0 FAILED.
8. TVMaze integración: 6 passed (API real).
9. Pruebas de ApiError: 16 passed.
10. Caché: 10 passed.
11. Favoritos: 14 passed.
12. Historial: 10 passed.
13. Estadísticas: 4 passed.
14. Importación/exportación: 18 passed.
15. Aislamiento de estado: OK (fixtures autouse; ejecución cruzada
    menú → servicios y de restauración de CONFIG).
16. Cobertura: 100% (516 sentencias, 0 perdidas) con el comando
    --cov-fail-under=80. Sin excluir ni manipular la medición.
17. Ninguna credencial real en archivos nuevos/modificados: OK
    (comprobación en memoria contra el valor de referencia, sin mostrarlo).
18. requirements.txt coherente: 4 líneas, todas satisfechas;
    pip check sin problemas.
19. Arranque normal de main.py: OK (menú → 12 → "¡Hasta luego!").
20. Sin regresiones de Fases 1-5: OK (bare except 0, except Exception
    solo en main.py, constants.py sin API_KEY_OMDB, getenv presente,
    12 opciones de menú, validaciones de Fase 5 intactas, búsquedas
    con y sin clave funcionando).

### Comando de cobertura (flags explícitos, fuera de addopts)

python3 -m pytest --cov=api --cov=services --cov=ui --cov=main --cov=config --cov=constants --cov=exceptions --cov=models --cov-report=term-missing --cov-fail-under=80

---

# ESTADO FINAL

Fases 1 a 6 completadas y validadas.

Próximos pasos opcionales (fuera del alcance actual, documentados en
Fase 5): archivos huérfanos, captura de DataExportError y limpieza de
código muerto (API_KEY_TMDB, BASE_URL_TMDB, USUARIO_LOGUEADO).