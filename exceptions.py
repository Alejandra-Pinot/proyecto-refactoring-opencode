# Excepciones personalizadas de la aplicación
class AppError(Exception):
    """Base de excepciones de la aplicación"""


class ApiError(AppError):
    """Error de llamada a OMDB/TVMaze (red o cuerpo no JSON)"""


class DataImportError(AppError):
    """Error al leer/parsear el JSON de importación"""


class DataExportError(AppError):
    """Error al escribir el JSON de exportación"""
