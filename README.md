# Kavak Commercial Bot

Un asistente virtual inteligente para la venta de autos seminuevos, desarrollado como prueba de concepto. El chatbot utiliza OpenAI para procesar lenguaje natural y proporciona recomendaciones personalizadas basadas en un catálogo real de vehículos.

## Características

- Integración con WhatsApp a través de Twilio
- Procesamiento de lenguaje natural con OpenAI GPT-3.5
- Catálogo de autos con información detallada
- Sistema de recomendación de vehículos
- Logging detallado para monitoreo y debugging

## Estructura del Proyecto

```
app/
├── core/           # Componentes core del sistema
│   ├── config.py   # Configuración centralizada
│   └── logger.py   # Sistema de logging
├── api/            # Endpoints y rutas de la API
└── services/       # Servicios de negocio
    ├── chat_service.py
    ├── car_recommendation.py
    └── financing_service.py
```

## Endpoints

### Chat Service
- **POST** `/api/chat`
  - Procesa mensajes del usuario y devuelve respuestas del chatbot
  - Body: `{"message": "string", "conversation_history": []}`

### WhatsApp Webhook
- **POST** `/api/whatsapp/webhook`
  - Endpoint para recibir mensajes de WhatsApp
  - Configurado para trabajar con Twilio

## Configuración

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd kavak
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```env
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
FLASK_DEBUG=True
FLASK_SECRET_KEY=your_secret_key
```

5. Asegurarse de que el archivo de catálogo esté presente:
- Verificar que el archivo `data/sample_caso_ai_engineer.csv` existe
- El archivo debe contener las columnas requeridas: stock_id, make, model, year, price, km, version

## Ejecución

1. Iniciar el servidor:
```bash
python run.py
```

2. El servidor estará disponible en `http://localhost:8080`

## Ejemplo de Uso

### Probar el Chat Service

```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué autos Toyota tienes disponibles?",
    "conversation_history": []
  }'
```

## Notas Adicionales

- El sistema utiliza un catálogo de muestra con autos seminuevos
- Las recomendaciones se basan en el presupuesto, marca, modelo y año
- El chatbot mantiene el contexto de la conversación para recomendaciones más precisas
- Los logs se guardan en la carpeta `logs/` para monitoreo y debugging

## Mejoras Futuras

- Implementar autenticación y autorización
- Agregar más criterios de búsqueda y filtrado
- Mejorar el sistema de recomendaciones
- Implementar caché para optimizar rendimiento
- Agregar tests automatizados
- Implementar CI/CD
