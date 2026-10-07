---
name: testing
description: Crear tests con pytest
---

# Testing

Skill genérica y reutilizable: crear tests automáticos con pytest para
validar el código de cualquier proyecto Python.

**Las instrucciones completas están en `instrucciones.md` de esta misma
carpeta: léelo antes de escribir o ampliar tests.**

Puntos cubiertos por esa guía:

1. Estructura de `tests/` con pytest (`pytest.ini`, `unit/`,
   `integration/`, conftest)
2. Tests unitarios para servicios (sin red, con aislamiento de estado)
3. Mock de APIs externas con pytest-mock
4. Fixtures para datos de prueba
5. Parametrización de tests
6. Coverage con pytest-cov
7. Tests de integración (reales, con `skipif` si falta credencial)
8. Patrón Arrange-Act-Assert
9. Buenas prácticas: markers, ejecución separada unit/integration, sin
   tests artificiales para inflar cobertura

Nota: pytest y pytest-cov se usan si el proyecto ya los incluye en sus
dependencias; esta skill no añade dependencias por sí sola.
