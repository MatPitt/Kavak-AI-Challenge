import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Configuración de OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-3.5-turbo"
    
    # Configuración de Twilio
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Configuración de la aplicación
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    
    # Configuración de financiamiento
    INTEREST_RATE = 0.10  # 10%
    MIN_TERM = 36  # 3 años en meses
    MAX_TERM = 72  # 6 años en meses
    #Es un poco redudante en el caso de los valores del financiamiento pero es muestra de tener valores en el archivo config para facil acceso y edicion
     
    # Rutas de archivos
    CATALOG_PATH = "data/sample_caso_ai_engineer.csv" 