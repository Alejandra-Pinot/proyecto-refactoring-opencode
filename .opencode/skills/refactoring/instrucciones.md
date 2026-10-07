# Skill: Refactoring

## Propósito

Eliminar malas prácticas del código Python y mejorar su estructura sin
cambiar el comportamiento observable del programa.

## Cuándo usarla (y cuándo no)

- Usar cuando: el código tiene variables globales, imports wildcard,
  `except:` vacíos, strings concatenados con `+`, funciones sin type
  hints, duplicación evidente o módulos que hacen demasiadas cosas.
- No usar cuando: se necesita cambiar el comportamiento (eso es
  refactorización + feature), o cuando no hay tests que protejan el
  cambio. Si no hay tests, proponerlos primero.

Regla de oro: **un refactor por paso, ejecutar la verificación tras cada
paso, y no mezclar cambios de estilo con cambios de diseño.**

## Proceso paso a paso

### 1. Buscar y eliminar variables globales

- Localizar: `global x`, `x = ...` a nivel de módulo que se muta en
  funciones, y lecturas de ese módulo desde otros módulos.
- Sustituir por: estado encapsulado en una clase, en un objeto que se
  pasa como parámetro, o en un módulo cuya función sea devolver el
  estado (sin reasignaciones externas).
- Mantener una única fuente de verdad: si el estado vive en dos
  sitios, unificarlo.

```python
# Antes
CONTADOR = 0

def incrementar():
    global CONTADOR
    CONTADOR += 1

# Después
class Contador:
    def __init__(self) -> None:
        self.valor = 0

    def incrementar(self) -> None:
        self.valor += 1
```

### 2. Reemplazar wildcard imports por imports específicos

- Buscar `from modulo import *`.
- Sustituir por los nombres realmente usados, o `import modulo` y usar
  `modulo.funcion()`.
- Ayuda: activar/revisar las advertencias de flake8 (`F403`, `F405`) o
  ejecutar `python3 -W error -c "import modulo"` para detectar conflictos.

```python
# Antes
from utils import *

# Después
from utils import validar_email, formatear_fecha
```

### 3. Convertir concatenación de strings a f-strings

- Buscar `+` entre strings, `%` y `.format()` en código Python 3.6+.
- Convertir a f-strings; conservar `"".join(...)` para unir colecciones
  (rendimiento y claridad).

```python
# Antes
saludo = "Hola, " + nombre + " (" + str(edad) + ")"

# Después
saludo = f"Hola, {nombre} ({edad})"
```

### 4. Agregar type hints a funciones

- Añadir tipos en parámetros y valor de retorno de todas las funciones
  públicas; `-> None` para procedimientos.
- Para valores desconocidos usar `Optional[X]` / `X | None`, no `Any`
  como primer recurso.
- Verificar con `python3 -m mypy <paquete>` si mypy está disponible; si
  no, al menos revisar que los hints sean coherentes.

```python
def buscar(consulta: str, limite: int = 10) -> list[str]:
    ...
```

### 5. Separar responsabilidades en módulos

- Regla: un módulo con una razón para cambiar (capa, dominio o
  infraestructura).
- Separar: lógica de negocio vs acceso a datos vs entrada/salida vs
  configuración.
- Señal de alerta: un módulo que importa de casi todos los demás, o
  funciones con más de ~3 responsabilidades.

```python
# Antes
def procesar():       # valida + consulta API + guarda + imprime
    ...

# Después
validacion.py   → validar()
cliente_api.py  → consultar()
almacenamiento.py → guardar()
presentacion.py → mostrar()
```

### 6. Eliminar código duplicado (DRY)

- Detectar bloques casi idénticos (mismo código, distintos datos).
- Extraer a una función/parametrizar; si la duplicación es entre
  capas, introducir una abstracción compartida.
- No abstraer en exceso: regla de tres y claridad por encima.

```python
# Antes: dos copias casi iguales
# Después: una función parametrizada
def total(items: list[Item], tasa: float) -> float:
    ...
```

### 7. Reemplazar bare except por excepciones específicas

- Buscar `except:` y `except Exception:` que silencian errores.
- Capturar la excepción concreta del dominio (`ValueError`,
  `KeyError`, `OSError`, `json.JSONDecodeError`, `requests.RequestException`).
- Si el error se propaga, encadenar: `raise MiError(...) from e`.
- Si se ignora deliberadamente, dejar comentario del porqué y registrar.

```python
# Antes
try:
    dato = json.load(archivo)
except:
    pass

# Después
try:
    dato = json.load(archivo)
except json.JSONDecodeError as e:
    raise DatosInvalidos(f"JSON ilegible en {ruta}") from e
```

### 8. Crear dataclasses para modelos de datos

- Sustituir diccionarios ad-hoc por `@dataclass` (o `NamedTuple` si el
  modelo es inmutable) cuando el dato tiene forma fija.
- Beneficios: validación en `__post_init__`, inmutabilidad con
  `frozen=True`, `__eq__`/`__repr__` gratis, hints completos.

```python
# Antes
usuario = {"nombre": "ana", "edad": 30}

# Después
from dataclasses import dataclass

@dataclass(frozen=True)
class Usuario:
    nombre: str
    edad: int
```

### 9. Implementar inyección de dependencias

- Regla: el módulo no crea sus dependencias caras (cliente HTTP,
  base de datos, reloj, filesystem); las recibe como parámetro o
  constructor.
- No hace falta framework: basta con recibir objetos con contrato
  claro (funciones o Protocol/ABC).
- Ventaja: testeabilidad (se inyectan dobles) y sustituibilidad.

```python
# Antes
class Servicio:
    def ejecutar(self) -> None:
        cliente = ClienteHTTP()   # dependencia creada dentro

# Después
class Servicio:
    def __init__(self, cliente: ClienteHTTP) -> None:
        self._cliente = cliente

    def ejecutar(self) -> None:
        self._cliente.get(...)
```

## Ejemplo integrado de secuencia recomendada

1. Asegurar cobertura de tests (o escribir los mínimos que fijen el
   comportamiento actual).
2. Wildcard imports → imports específicos.
3. Type hints en las funciones tocadas.
4. Duplicados → funciones extraídas.
5. Bare except → excepciones concretas con `from e`.
6. Strings → f-strings.
7. Globals → estado encapsulado / DI.
8. Diccionarios de datos → dataclasses.
9. Reagrupar módulos por responsabilidad.

## Verificación

```bash
python3 -m py_compile $(git ls-files '*.py' 2>/dev/null || find . -name '*.py' -not -path '*/__pycache__/*')
python3 -m pytest -q                 # si hay suite
python3 -m mypy .                    # si mypy está configurado
python3 -m flake8 .                  # si flake8 está configurado
grep -rn "import \*" --include='*.py' . | grep -v __pycache__
grep -rn "^global \|    global " --include='*.py' .
grep -rn "except:" --include='*.py' .
```

Comprobación de comportamiento: la salida observable (CLI, API,
archivos) debe ser idéntica antes y después.

## Errores comunes

- Refactorizar sin tests: introduce regresiones invisibles.
- Mezclar renombrado + cambio de diseño en un mismo paso.
- Crear dataclasses donde un simple `NamedTuple` o dict basta.
- DI con frameworks innecesarios cuando basta un parámetro.
- `except Exception` como sustituto del bare except sin más detalle.
- Abstraer demasiado pronto (regla de tres).
- Dejar código muerto "por si acaso": eliminarlo.
