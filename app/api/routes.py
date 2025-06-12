from flask import Blueprint, request, jsonify
from app.services.chat_service import ChatService
from app.services.car_recommendation import CarRecommendationService
from app.services.financing_service import FinancingService
from app.core.logger import api_logger, error_logger

# Inicializar servicios
chat_service = ChatService()
car_service = CarRecommendationService()
financing_service = FinancingService()

# Crear Blueprint
api = Blueprint('api', __name__)

@api.route('/chat', methods=['POST'])
def chat():
    """Endpoint para el chat con el asistente virtual."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            api_logger.warning("Invalid chat request: missing message")
            return jsonify({'error': 'Se requiere un mensaje'}), 400

        api_logger.info(f"Processing chat request: {data['message'][:100]}...")
        response = chat_service.get_response(data['message'], data.get('context'))
        api_logger.info("Chat response generated successfully")
        return jsonify({'response': response})

    except Exception as e:
        error_logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Endpoint para obtener recomendaciones de autos."""
    try:
        data = request.get_json()
        if not data:
            api_logger.warning("Invalid recommendations request: missing preferences")
            return jsonify({'error': 'Se requieren preferencias'}), 400

        api_logger.info(f"Processing car recommendations request: {data}")
        recommendations = car_service.get_recommendations(data)
        api_logger.info(f"Found {len(recommendations)} recommendations")
        return jsonify({'recommendations': recommendations})

    except Exception as e:
        error_logger.error(f"Error in recommendations endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api.route('/car/<int:car_id>', methods=['GET'])
def get_car_details(car_id):
    """Endpoint para obtener detalles de un auto específico."""
    try:
        api_logger.info(f"Fetching details for car ID: {car_id}")
        car_details = car_service.get_car_details(car_id)
        if not car_details:
            api_logger.warning(f"Car not found with ID: {car_id}")
            return jsonify({'error': 'Auto no encontrado'}), 404

        api_logger.info(f"Successfully retrieved details for car ID: {car_id}")
        return jsonify(car_details)

    except Exception as e:
        error_logger.error(f"Error in car details endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api.route('/financing', methods=['POST'])
def calculate_financing():
    """Endpoint para calcular planes de financiamiento."""
    try:
        data = request.get_json()
        required_fields = ['car_price', 'down_payment', 'term_months']
        
        if not all(field in data for field in required_fields):
            api_logger.warning(f"Invalid financing request: missing required fields. Data: {data}")
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        api_logger.info(f"Calculating financing for: {data}")
        financing = financing_service.calculate_amortization_schedule(
            data['car_price'],
            data['down_payment'],
            data['term_months']
        )

        if not financing:
            api_logger.warning("Failed to calculate financing")
            return jsonify({'error': 'Error al calcular el financiamiento'}), 400

        api_logger.info("Financing calculation completed successfully")
        return jsonify(financing)

    except Exception as e:
        error_logger.error(f"Error in financing endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500 