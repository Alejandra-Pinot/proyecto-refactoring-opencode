---
name: api-integration
description: Integrar APIs REST en Python
---

# API Integration

Skill genérica y reutilizable: conectar a APIs REST de forma robusta y
mantenible en cualquier proyecto Python.

**Las instrucciones completas están en `instrucciones.md` de esta misma
carpeta: léelo antes de diseñar o modificar un cliente de API.**

Puntos cubiertos por esa guía:

1. Crear clientes para cada API
2. Implementar caché de respuestas
3. Agregar reintentos con backoff exponencial
4. Manejar rate limiting
5. Validar respuestas con pydantic o dataclasses
6. Logging de requests y responses (nunca con credenciales)
7. Timeouts configurables
8. Manejo de errores HTTP con excepciones de dominio
9. Separación cliente/servicio/caché y claves en variables de entorno

Nota: esas técnicas se documentan aquí como instrucciones; aplicarlas
solo cuando el proyecto lo requiera y sus dependencias lo permitan.
