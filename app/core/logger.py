import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Configura un logger con manejadores para consola y archivo.
    
    Args:
        name (str): Nombre del logger
        log_file (str, opcional): Ruta al archivo de log. Si es None, los logs solo irán a la consola
        level (int, opcional): Nivel de logging. Por defecto es logging.INFO
    
    Returns:
        logging.Logger: Instancia de logger configurada
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Crear formateadores
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # Crear manejador de consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Crear manejador de archivo si se proporciona log_file
    if log_file:
        # Crear directorio de logs si no existe
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Crear manejador de archivo rotativo (10MB por archivo, máximo 5 archivos)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Crear logger de aplicación
app_logger = setup_logger(
    'kavak_app',
    log_file='logs/app.log',
    level=logging.INFO
)

# Crear logger de errores
error_logger = setup_logger(
    'kavak_errors',
    log_file='logs/errors.log',
    level=logging.ERROR
)

# Crear logger de API
api_logger = setup_logger(
    'kavak_api',
    log_file='logs/api.log',
    level=logging.INFO
)

# Crear logger de WhatsApp
whatsapp_logger = setup_logger(
    'kavak_whatsapp',
    log_file='logs/whatsapp.log',
    level=logging.INFO
) 