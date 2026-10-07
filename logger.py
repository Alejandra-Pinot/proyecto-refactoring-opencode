import json
import os
import time
from datetime import datetime

# Variables globales
LOG_FILE = "app.log"
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

def log_message(message, level="INFO"):
    """Escribe mensaje a archivo y consola"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = timestamp + " [" + level + "] " + message
    
    # Escribir a archivo
    with open(LOG_FILE, 'a') as f:
        f.write(formatted_message + "\n")
    
    # Imprimir a consola si debug
    if LOG_LEVEL == "DEBUG":
        print(formatted_message)

def log_debug(message):
    """Log de debug"""
    log_message(message, "DEBUG")

def log_info(message):
    """Log de info"""
    log_message(message, "INFO")

def log_warning(message):
    """Log de warning"""
    log_message(message, "WARNING")

def log_error(message):
    """Log de error"""
    log_message(message, "ERROR")

def log_critical(message):
    """Log crítico"""
    log_message(message, "CRITICAL")

def clear_log():
    """Limpia archivo de log"""
    with open(LOG_FILE, 'w') as f:
        f.write("")

def get_log_lines():
    """Obtiene líneas del log"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return f.readlines()
    return []

def search_log(pattern):
    """Busca en log sin regex"""
    lines = get_log_lines()
    results = []
    for line in lines:
        if pattern in line:
            results.append(line)
    return results

def export_log(filename):
    """Exporta log"""
    lines = get_log_lines()
    with open(filename, 'w') as f:
        for line in lines:
            f.write(line)

def get_log_stats():
    """Obtiene estadísticas del log"""
    lines = get_log_lines()
    stats = {
        "total": len(lines),
        "debug": 0,
        "info": 0,
        "warning": 0,
        "error": 0,
        "critical": 0
    }
    
    for line in lines:
        if "[DEBUG]" in line:
            stats["debug"] += 1
        elif "[INFO]" in line:
            stats["info"] += 1
        elif "[WARNING]" in line:
            stats["warning"] += 1
        elif "[ERROR]" in line:
            stats["error"] += 1
        elif "[CRITICAL]" in line:
            stats["critical"] += 1
    
    return stats

def format_log_entry(timestamp, level, message):
    """Formatea entrada de log"""
    return timestamp + " [" + level + "] " + message

def parse_log_line(line):
    """Parsea línea de log sin validación"""
    parts = line.split(" - ", 2)
    return {
        "timestamp": parts[0],
        "level": parts[1].replace("[", "").replace("]", ""),
        "message": parts[2]
    }

def filter_log_by_level(level):
    """Filtra log por nivel"""
    lines = get_log_lines()
    filtered = []
    for line in lines:
        if "[" + level + "]" in line:
            filtered.append(line)
    return filtered

def filter_log_by_date(date_str):
    """Filtra log por fecha"""
    lines = get_log_lines()
    filtered = []
    for line in lines:
        if date_str in line:
            filtered.append(line)
    return filtered

def rotate_log(max_size_mb=10):
    """Rota archivo de log"""
    if os.path.exists(LOG_FILE):
        size_mb = os.path.getsize(LOG_FILE) / (1024 * 1024)
        if size_mb > max_size_mb:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = LOG_FILE + "." + timestamp
            os.rename(LOG_FILE, new_filename)
            log_info("Log rotado a: " + new_filename)
