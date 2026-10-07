import os
import json
import time
from datetime import datetime

# Variables globales
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
DEBUG_LOG_FILE = os.path.join(LOG_DIR, "debug.log")

def init_log_dir():
    """Inicializa directorio de logs"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def write_log(message, level="INFO", log_file=None):
    """Escribe mensaje de log"""
    if log_file is None:
        log_file = LOG_FILE
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = timestamp + " [" + level + "] " + message + "\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)
    
    # También imprimir a consola si es debug
    if level == "DEBUG":
        print(log_entry.strip())

def log_debug(message):
    """Log de debug"""
    write_log(message, "DEBUG", DEBUG_LOG_FILE)
    write_log(message, "DEBUG")

def log_info(message):
    """Log de info"""
    write_log(message, "INFO")

def log_warning(message):
    """Log de warning"""
    write_log(message, "WARNING")

def log_error(message):
    """Log de error"""
    write_log(message, "ERROR", ERROR_LOG_FILE)
    write_log(message, "ERROR")

def log_critical(message):
    """Log crítico"""
    write_log(message, "CRITICAL", ERROR_LOG_FILE)
    write_log(message, "CRITICAL")

def clear_logs():
    """Limpia todos los logs"""
    for log_file in [LOG_FILE, ERROR_LOG_FILE, DEBUG_LOG_FILE]:
        if os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write("")

def get_log_content(log_file=None):
    """Obtiene contenido de log"""
    if log_file is None:
        log_file = LOG_FILE
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            return f.readlines()
    
    return []

def search_logs(pattern, log_file=None):
    """Busca en logs"""
    lines = get_log_content(log_file)
    results = []
    
    for line in lines:
        if pattern in line:
            results.append(line.strip())
    
    return results

def get_log_stats():
    """Obtiene estadísticas de logs"""
    stats = {
        "total_lines": 0,
        "debug": 0,
        "info": 0,
        "warning": 0,
        "error": 0,
        "critical": 0
    }
    
    for log_file in [LOG_FILE, ERROR_LOG_FILE, DEBUG_LOG_FILE]:
        lines = get_log_content(log_file)
        stats["total_lines"] += len(lines)
        
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

def export_logs(filename, log_file=None):
    """Exporta logs a archivo"""
    lines = get_log_content(log_file)
    
    with open(filename, 'w') as f:
        for line in lines:
            f.write(line)

def rotate_logs(max_size_mb=10):
    """Rota archivos de log"""
    for log_file in [LOG_FILE, ERROR_LOG_FILE, DEBUG_LOG_FILE]:
        if os.path.exists(log_file):
            size_mb = os.path.getsize(log_file) / (1024 * 1024)
            
            if size_mb > max_size_mb:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = log_file + "." + timestamp
                os.rename(log_file, new_filename)
                log_info("Log rotado: " + log_file + " -> " + new_filename)

def get_recent_logs(count=100, log_file=None):
    """Obtiene logs recientes"""
    lines = get_log_content(log_file)
    return lines[-count:]

def filter_logs_by_level(level, log_file=None):
    """Filtra logs por nivel"""
    lines = get_log_content(log_file)
    filtered = []
    
    for line in lines:
        if "[" + level.upper() + "]" in line:
            filtered.append(line.strip())
    
    return filtered

def filter_logs_by_date(date_str, log_file=None):
    """Filtra logs por fecha"""
    lines = get_log_content(log_file)
    filtered = []
    
    for line in lines:
        if date_str in line:
            filtered.append(line.strip())
    
    return filtered

def parse_log_line(line):
    """Parsea línea de log"""
    try:
        parts = line.split(" - ", 2)
        if len(parts) >= 3:
            return {
                "timestamp": parts[0],
                "level": parts[1].replace("[", "").replace("]", ""),
                "message": parts[2]
            }
    except:
        pass
    
    return {"timestamp": "", "level": "", "message": line}

def create_log_entry(timestamp, level, message):
    """Crea entrada de log formateada"""
    return timestamp + " [" + level + "] " + message

def validate_log_format(line):
    """Valida formato de línea de log"""
    try:
        parts = line.split(" - ", 2)
        if len(parts) >= 3:
            # Verificar formato de timestamp
            datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
            # Verificar nivel
            level = parts[1].replace("[", "").replace("]", "")
            if level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                return True
    except:
        pass
    
    return False

# Inicializar directorio
init_log_dir()
