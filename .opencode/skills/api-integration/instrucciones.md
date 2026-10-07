# Skill: API Integration

## Propósito

Conectar a APIs REST de forma robusta y mantenible: un cliente
reutilizable por API, errores claros, caché y reintentos controlados,
sin exponer credenciales.

## Cuándo usarla (y cuándo no)

- Usar cuando: se añade un cliente HTTP contra una API externa, o un
  cliente existente no tiene timeouts, caché, reintentos o manejo de
  errores uniforme.
- No usar cuando: no hay red involucrada (lógica pura) o solo se
  necesita una llamada puntual descartable. Aun así, aplicar al menos
  timeout, credencial por variable de entorno y manejo de errores.

Arquitectura recomendada:

```
cliente_api.py   → transporte HTTP (una clase por API)
servicio.py      → lógica de negocio (usa el cliente)
caché.py         → almacén de respuestas (opcional)
modelos.py       → dataclasses o modelos pydantic de las respuestas
config.py        → URLs base, timeouts, claves desde variables de entorno
```

## Proceso paso a paso

### 1. Crear clientes para cada API

- Una clase/función por API, con la URL base en configuración.
- Exponer métodos de dominio (`buscar_pelicula`, `listar_series`), no
  un `get(url)` genérico que escape a las capas superiores.
- Inyectar la sesión HTTP o el `requests.get` para poder testear sin
  red.

```python
# cliente_peliculas.py
import os
import requests

class ClientePeliculas:
    BASE_URL = "https://api.example.com/v1"

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout
        self._api_key = os.getenv("API_KEY_PELICULAS", "")
        if not self._api_key:
            raise ConfiguracionError("Falta la variable de entorno API_KEY_PELICULAS")

    def buscar(self, titulo: str) -> dict:
        return self._get("/buscar", params={"t": titulo})

    def _get(self, ruta: str, params: dict | None = None) -> dict:
        ...
```

### 2. Implementar caché de respuestas

- Clave: método + parámetros normalizados (minúsculas, sin credenciales).
- TTL configurable; cachear también resultados vacíos para evitar
  ataques de repetición.
- Invalidación: TTL, límite de tamaño (LRU) o invalidación explícita
  tras mutaciones.
- Nunca cachear respuestas de error.

```python
from dataclasses import dataclass, field
import time

@dataclass
class CacheTTL:
    ttl: float = 300.0
    _datos: dict[str, tuple[float, object]] = field(default_factory=dict, repr=False)

    def obtener(self, clave: str):
        entrada = self._datos.get(clave)
        if not entrada:
            return None
        expira, valor = entrada
        if time.monotonic() > expira:
            self._datos.pop(clave, None)
            return None
        return valor

    def guardar(self, clave: str, valor: object) -> None:
        self._datos[clave] = (time.monotonic() + self.ttl, valor)
```

### 3. Agregar reintentos con backoff exponencial

- Reintentar solo errores transitorios: timeouts, 5xx, conexiones
  caídas. Nunca reintentar 4xx de validación.
- Backoff exponencial con jitter: espera `min(base * 2**intento, tope)`
  + aleatorio pequeño para evitar sincronización de clientes.
- Límite de intentos (p. ej. 3) y respetar `Retry-After` si viene.
- No reintentar dentro de la capa de negocio; el cliente lo hace.

```python
import random
import time

def reintentar(func, intentos: int = 3, base: float = 0.5, tope: float = 8.0):
    ultimo_error = None
    for intento in range(intentos):
        try:
            return func()
        except ErroresTransitorios as e:
            ultimo_error = e
            espera = min(base * (2 ** intento), tope) + random.uniform(0, 0.25)
            time.sleep(espera)
    raise ultimo_error
```

### 4. Manejar rate limiting

- Respetar `429` y el header `Retry-After` (segundos o fecha HTTP).
- Límite local de tasa (p. ej. token bucket o contador por ventana)
  para no provocar el límite del servidor.
- Exponer un error de dominio claro (`RateLimitError`) con el tiempo de
  espera; el llamador decide si espera o falla.

```python
if respuesta.status_code == 429:
    espera = float(respuesta.headers.get("Retry-After", "1"))
    raise RateLimitError(f"Límite de peticiones alcanzado; esperar {espera}s")
```

### 5. Validar respuestas con pydantic o dataclasses

- La respuesta JSON nunca se asume correcta: validar estructura y
  tipos antes de devolverla.
- Opción ligera (stdlib): dataclasses con conversión y comprobación en
  `__post_init__`.
- Opción con librería: pydantic (`BaseModel`) si el proyecto ya lo
  depende.
- Si el payload no cumple, lanzar `RespuestaInvalida` (no devolver
  `None` silencioso).

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Pelicula:
    titulo: str
    anio: int

    def __post_init__(self) -> None:
        if self.anio < 1888:
            raise ValueError(f"Año inválido: {self.anio}")

def parsear(data: dict) -> Pelicula:
    try:
        return Pelicula(titulo=data["titulo"], anio=int(data["anio"]))
    except (KeyError, TypeError, ValueError) as e:
        raise RespuestaInvalida("Payload inesperado de la API") from e
```

### 6. Logging de requests y responses

- Registrar: método, URL (sin query de credenciales), status, duración,
  intento y número de elementos recibido.
- Nivel: DEBUG para detalle, WARNING para reintentos/429, ERROR para
  fallo definitivo.
- **Nunca** registrar claves, tokens, cabeceras de autorización ni
  cookies. Filtrar parámetros sensibles antes de formatear.
- Log con `logging` estándar, no `print`.

```python
params_visibles = {k: v for k, v in params.items() if k.lower() not in {"apikey", "token", "key"}}
logger.debug("GET %s params=%s status=%s", url, params_visibles, status)
```

### 7. Timeouts configurables

- Siempre: `timeout=(conectar, leer)` o escalar. Un timeout global
  procedente de configuración.
- Valores por defecto razonables (p. ej. 5s/15s) y sobrescritura por
  entorno.
- Sin timeout, una petición colgada bloquea el proceso entero.

```python
import os

TIMEOUT = float(os.getenv("API_TIMEOUT", "10"))
respuesta = requests.get(url, params=params, timeout=TIMEOUT)
```

### 8. Manejo de errores HTTP

- Mapear fallos de red/HTTP a excepciones de dominio propias
  (`ApiError`, `TimeoutError`, `RateLimitError`, `RespuestaInvalida`)
  heredadas de una base común (`AppError`).
- Encadenar la causa: `raise ApiError(msg) from e`.
- Distinguir: error de transporte (no hay respuesta) vs error HTTP
  (respuesta con 4xx/5xx) vs error de contrato (JSON inválido).
- El mensaje no debe contener credenciales.

```python
try:
    respuesta = requests.get(url, timeout=timeout)
except requests.exceptions.RequestException as e:
    raise ApiError(f"Error de conexión con {url}") from e

if respuesta.status_code >= 400:
    raise ApiError(f"HTTP {respuesta.status_code} desde {url}")

try:
    return respuesta.json()
except ValueError as e:
    raise RespuestaInvalida(f"Respuesta no JSON desde {url}") from e
```

### 9. Separación cliente / servicio / caché y claves en entorno

- El cliente solo habla HTTP; el servicio aplica la lógica de negocio y
  decide cuándo cachear.
- URLs base, timeouts y claves en configuración/variables de entorno;
  nunca literales en el código ni en el repositorio.
- Documentar en `.env.example` las variables requeridas con placeholders.

## Verificación

```bash
python3 -m py_compile <cliente>.py
python3 -m pytest -q                      # tests con mocks: sin red
python3 -c "import cliente; print('ok')"
grep -rn "apikey\|api_key" --include='*.py' . | grep -v os.getenv   # sin claves literales
```

- Probar el caso de error: sin credencial, con timeout, con 404 y con
  respuesta no JSON.
- Comprobar en logs que no aparece ninguna credencial.

## Errores comunes

- Timeout por defecto de la librería (o ninguno) → bloqueos.
- Reintentar en bucle los 4xx de validación.
- Cachear errores o respuestas con credenciales.
- Loguear la URL completa con `?apikey=...`.
- Devolver `None` en todos los errores y perder el motivo.
- Un cliente genérico `get(url)` usado por toda la aplicación.
- Ignorar `Retry-After` y provocar bloqueo por rate limit.
