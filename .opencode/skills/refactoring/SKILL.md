---
name: refactoring
description: Refactorizar codigo Python con malas practicas
---

# Refactoring

Skill genérica y reutilizable: eliminar malas prácticas del código
Python y mejorar su estructura sin cambiar el comportamiento observable.

**Las instrucciones completas están en `instrucciones.md` de esta misma
carpeta: léelo antes de aplicar cambios y síguelo paso a paso.**

Puntos cubiertos por esa guía:

1. Buscar y eliminar variables globales
2. Reemplazar wildcard imports por imports específicos
3. Convertir concatenación de strings a f-strings
4. Agregar type hints a funciones
5. Separar responsabilidades en módulos
6. Eliminar código duplicado
7. Reemplazar bare except por excepciones específicas
8. Crear dataclasses para modelos de datos
9. Implementar inyección de dependencias

Uso recomendado: pequeños pasos verificables (`py_compile`, tests,
linters) tras cada cambio; nunca mezclar refactorización con cambios de
comportamiento.
