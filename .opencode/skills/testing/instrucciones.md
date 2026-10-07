# Skill: Testing

## Propósito

Crear tests automáticos con pytest que validen el comportamiento del
código, con cobertura medible y sin depender de servicios externos.

## Cuándo usarla (y cuándo no)

- Usar cuando: se escribe código nuevo, se corrige un bug (primero el
  test que lo reproduce) o se quiere cubrir código sin tests.
- No usar cuando: se pide únicamente refactorizar sin verificar, o
  cuando no está permitido añadir archivos de test. Nunca crear tests
  artificiales solo para subir la cobertura.

## Estructura de tests/ con pytest

```
pytest.ini                 # testpaths, pythonpath, addopts, markers
tests/
    __init__.py
    conftest.py            # fixtures compartidos y aislamiento de estado
    unit/
        __init__.py
        conftest.py        # bloqueo de red (los unitarios no navegan)
        test_<modulo>_service.py
        test_<cliente_api>.py
    integration/
        __init__.py
        test_<api>_real.py # con skipif si falta credencial
```

`pytest.ini` mínimo (los flags de cobertura van en el comando, no aquí):

```ini
[pytest]
testpaths = tests
pythonpath = .
addopts = -ra --strict-markers
markers =
    unit: tests unitarios, sin acceso a Internet
    integration: tests de integración con APIs reales
```

Convenciones:

- Un test = un comportamiento; nombre `test_<qué>_cuando_<condición>`.
- Los tests importan el código por el paquete (`from servicios import
  buscar`), no por rutas relativas.
- Ejecutar siempre con el mismo intérprete del proyecto.

## Tests unitarios para servicios

- Cubren la lógica de negocio con todas las dependencias externas
  reemplazadas (API, filesystem, reloj, terminal).
- Sin red: bloquear el transporte HTTP en el `conftest` de `unit/`.

```python
# tests/unit/conftest.py
import pytest
import requests

@pytest.fixture(autouse=True)
def sin_internet(monkeypatch):
    def bloqueado(*args, **kwargs):
        raise AssertionError("Los tests unitarios no deben acceder a Internet")
    monkeypatch.setattr(requests.sessions.Session, "request", bloqueado)
```

- Aislar el estado mutable global: fixture que limpia antes y restaura
  después de cada test (los tests no pueden verse entre sí).

```python
# tests/conftest.py
@pytest.fixture(autouse=True)
def estado_limpio(almacen):
    copia = almacen.listar()
    almacen.limpiar()
    yield
    almacen.restaurar(copia)
```

## Mock de APIs externas con pytest-mock

- `pytest-mock` aporta la fixture `mocker` (envoltorio de `unittest.mock`).
- Reemplazar la llamada en el nivel correcto: el método del módulo bajo
  test, no la librería entera, cuando sea posible.

```python
def test_buscar_devuelve_la_pelicula(mocker, cliente):
    mocker.patch.object(cliente, "_get", return_value={"titulo": "Ejemplo"})
    resultado = cliente.buscar("ejemplo")
    assert resultado["titulo"] == "Ejemplo"

def test_timeout_se_convierte_en_error_de_dominio(mocker, cliente):
    mocker.patch.object(cliente, "_get", side_effect=ApiError("timeout"))
    with pytest.raises(ApiError):
        cliente.buscar("ejemplo")
```

- Para lo sin framework: `monkeypatch.setattr(modulo, "funcion", fake)`.
- Las respuestas falsas deben ser estructuralmente fieles a la API real
  (mismas claves), pero sin datos volátiles.

## Fixtures para datos de prueba

- Datos mínimos y locales en fixtures; nada de producción.
- Compartir construcciones en `conftest.py`; una fixture por concepto.
- `tmp_path` para archivos; nunca escribir en el repositorio.

```python
@pytest.fixture
def pelicula():
    return {"titulo": "Ejemplo", "anio": 2020, "rating": 7.5}
```

## Parametrización de tests

- Cuando varían solo los datos de entrada/espera, parametrizar en vez
  de copiar el test.

```python
@pytest.mark.parametrize("entrada,esperado", [
    ("", False),
    ("  ", False),
    ("correo@ejemplo.com", True),
])
def test_es_correo_valido(entrada, esperado):
    assert es_correo_valido(entrada) is esperado
```

- IDs legibles: `@pytest.mark.parametrize(..., ids=["vacio", "blancos", "ok"])`.

## Coverage con pytest-cov

```bash
python3 -m pytest --cov=paquete --cov-report=term-missing --cov-fail-under=80
```

- Flags en el comando (o en un alias), no necesariamente en `addopts`.
- Interpretar el informe: mirar **líneas faltantes** y cubrir
  comportamiento real, nunca añadir tests decorativos para el número.
- Si el umbral no se alcanza: listar módulos/líneas faltantes y añadir
  solo pruebas significativas; **no excluir módulos ni bajar el umbral
  a escondida**.

## Tests de integración

- Van en `tests/integration/`, marcados como `integration`.
- Usan los componentes reales (API real, base real) pero con datos
  estables (IDs públicos fijos) y asserts estructurales
  (claves/estructura, no valores volátiles).

```python
pytestmark = pytest.mark.skipif(
    not os.getenv("API_KEY_X", "").strip(),
    reason="API_KEY_X no configurada",
)

def test_listado_devuelve_estructura():
    datos = cliente.listar()
    assert isinstance(datos, list)
    assert all("id" in d for d in datos)
```

- Si falta la credencial → **skip**, nunca fallar.
- Ejecutar aparte: `pytest -m integration`, `pytest -m unit`.

## Patrón Arrange-Act-Assert

Cada test en tres bloques claros, sin lógica extra en el act:

```python
def test_eliminar_quita_el_elemento(pelicula):        # nombre: qué+cuándo
    almacen = Almacen()                               # Arrange
    almacen.agregar(pelicula)

    almacen.eliminar(pelicula["titulo"])              # Act

    assert almacen.listar() == []                     # Assert
```

- Un assert principal por test (varios solo si validan lo mismo).
- Sin `if`/bucles dentro del test; los errores deben aparecer siempre.
- Usar `pytest.raises` para errores esperados:

```python
with pytest.raises(DatosInvalidos):
    parsear({"anio": "no-numero"})
```

## Verificación

```bash
python3 -m pytest -q                    # suite completa
python3 -m pytest -m unit -q            # solo unitarios (sin red)
python3 -m pytest -m integration        # solo integración (red real)
python3 -m pytest --cov=paquete --cov-report=term-missing --cov-fail-under=80
```

## Errores comunes

- Tests dependientes del orden o de estado global no limpiado.
- Unitarios que navegan a Internet → suite lenta y frágil.
- Mockear demasiado: el test deja de probar el código real.
- Asserts sobre valores volátiles (fechas, orden de diccionario, datos
  externos cambiantes).
- Añadir tests solo por cobertura sin comportamiento que validar.
- `except:` en tests que oculta fallos; usar `pytest.raises`.
- Fijar credenciales reales en fixtures o en el repositorio.
