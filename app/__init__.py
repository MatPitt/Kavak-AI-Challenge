from flask import Flask
from flask_cors import CORS
from app.core.config import Config
from app.api.routes import api
from app.api.whatsapp import whatsapp
from app.core.logger import app_logger

def create_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    
    # Configurar la aplicación
    app.config.from_object(Config)
    
    # Habilitar CORS
    CORS(app)
    
    # Registrar blueprints
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(whatsapp, url_prefix='/whatsapp')
    
    app_logger.info("Application initialized successfully")
    
    return app 