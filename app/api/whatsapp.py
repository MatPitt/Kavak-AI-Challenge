from flask import Blueprint, request, jsonify
from twilio.rest import Client
from app.core.config import Config
from app.services.chat_service import ChatService
from app.services.car_recommendation import CarRecommendationService
from app.services.financing_service import FinancingService
from app.core.logger import whatsapp_logger, error_logger

# Inicializar servicios
chat_service = ChatService()
car_service = CarRecommendationService()
financing_service = FinancingService()

# Inicializar cliente de Twilio
twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

# Crear Blueprint
whatsapp = Blueprint('whatsapp', __name__)

# Diccionario para almacenar el contexto de conversación por número
conversation_contexts = {}

def send_whatsapp_message(to_number, message):
    """Envía un mensaje de WhatsApp usando Twilio."""
    try:
        whatsapp_logger.info(f"Sending WhatsApp message to {to_number}")
        message = twilio_client.messages.create(
            from_=f'whatsapp:{Config.TWILIO_PHONE_NUMBER}',
            body=message,
            to=to_number
        )
        whatsapp_logger.info(f"Message sent successfully. SID: {message.sid}")
        return message.sid
    except Exception as e:
        error_logger.error(f"Error sending WhatsApp message: {str(e)}", exc_info=True)
        return None

@whatsapp.route('/webhook', methods=['POST'])
def webhook():
    """Webhook para recibir mensajes de WhatsApp."""
    try:
        # Obtener datos del mensaje
        message_body = request.values.get('Body', '')
        from_number = request.values.get('From', '')
        
        whatsapp_logger.info(f"Received WhatsApp message from {from_number}: {message_body[:100]}...")
        
        # Obtener el contexto de la conversación para este número
        conversation_history = conversation_contexts.get(from_number, [])
        
        # Procesar el mensaje con el asistente virtual
        response = chat_service.get_response(message_body, conversation_history)
        whatsapp_logger.info("Generated response for WhatsApp message")
        
        # Actualizar el contexto de la conversación
        if response:
            # Agregar el mensaje del usuario al historial
            conversation_history.append({
                "role": "user",
                "content": message_body
            })
            
            # Agregar la respuesta del asistente al historial
            conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Mantener solo los últimos 10 mensajes
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]
            
            # Actualizar el contexto
            conversation_contexts[from_number] = conversation_history
            
            # Enviar respuesta
            send_whatsapp_message(from_number, response)
        
        return jsonify({'status': 'success'})

    except Exception as e:
        error_logger.error(f"Error in WhatsApp webhook: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
