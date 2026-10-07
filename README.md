# Proyecto de Refactoring - Películas y Series

Proyecto educativo con malas prácticas intencionales para practicar refactoring.

## Objetivo

Conectar a APIs de películas: OMDB utiliza `OMDB_API_KEY` como variable de entorno y TVMaze no requiere API key. El código está intencionalmente lleno de malas prácticas para que los estudiantes practiquen refactoring.

## Malas Prácticas Incluidas

### Arquitectura
- Variables globales en todas partes
- Sin separación de responsabilidades
- Sin principio SOLID
- Archivos de configuración excesivos (~60+ archivos `*_config.py`)

### Código
- Sin type hints
- Sin manejo de errores adecuado
- `from api_movies import *` (wildcard import)
- Strings hardcodeados
- Duplicación de código extrema
- Sin documentación
- `bare except:` clauses
- Argumentos mutables por defecto

### Estructura
- ~100 archivos Python en un solo directorio
- Múltiples implementaciones del mismo módulo (logger.py, log_manager.py)
- Configuración de caché de API con ~50+ archivos `api_cache_*_config.py`
- Sin tests unitarios
- Sin requirements.txt
- Sin virtual environment

### Seguridad
- Contraseñas en texto plano
- Sin validación de entrada
- Sin logging con módulo `logging`

## APIs Utilizadas

- **OMDB API**: requiere configurar la variable de entorno `OMDB_API_KEY`
- **TVMaze API**: pública, sin key

## Cómo Ejecutar

```bash
export OMDB_API_KEY=<tu_clave_omdb>
python main.py
```

## Cómo Refactorizar

1. Eliminar variables globales
2. Separar responsabilidades en módulos claros
3. Agregar type hints
4. Implementar manejo de errores
5. Crear tests unitarios
6. Eliminar código duplicado
7. Usar f-strings en lugar de concatenación
8. Implementar inyección de dependencias
9. Seguir principios SOLID
10. Reducir archivos de configuración
