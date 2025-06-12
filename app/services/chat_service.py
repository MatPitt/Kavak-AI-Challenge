import openai
from app.core.config import Config
from app.core.logger import app_logger, error_logger
from app.services.car_recommendation import CarRecommendationService

class ChatService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.car_service = CarRecommendationService()
        self.system_prompt = """Eres un asistente virtual de Kavak, especializado en la venta de autos seminuevos. Tu objetivo es ayudar a los clientes a encontrar el auto ideal y guiarlos en el proceso de compra.

        Tienes acceso a un catálogo de autos con la siguiente información:
        - ID de stock
        - Kilometraje
        - Precio
        - Marca
        - Modelo
        - Año
        - Versión
        - Características (Bluetooth, CarPlay)
        - Dimensiones (largo, ancho, altura)

        Instrucciones:
        1. Mantén el contexto de la conversación. No repitas saludos ni pidas información que el cliente ya proporcionó.
        2. Usa la información del catálogo para hacer recomendaciones precisas y relevantes.
        3. Sé profesional, claro y amable. Evita repeticiones innecesarias o mensajes largos.
        4. Haz preguntas útiles que ayuden a afinar las recomendaciones.
        5. Recomienda autos concretos del catálogo, incluyendo sus detalles específicos.
        6. Responde exclusivamente sobre autos, Kavak y opciones de financiamiento.
        7. Ignora mensajes irrelevantes (temas políticos, bromas, lenguaje ofensivo, etc.).
        8. Si no tienes certeza sobre algo, dilo con claridad. No inventes información.

        Recuerda:
        - Es importante que menciones quien eres y que haces si hay un mensaje de saludo o introductorio, si la pregunta es especifica solo saluda, menciona que eres de Kavak y continua con la respuesta
        - No repitas saludos en cada mensaje
        - Mantén la conversación fluida y natural
        - Enfócate en ayudar al cliente a encontrar su auto ideal
        - Usa la información del catálogo para dar respuestas precisas"""

        app_logger.info("ChatService initialized with OpenAI model: %s", self.model)

    def _extract_preferences(self, message):
        """
        Extrae preferencias de búsqueda del mensaje del usuario.
        
        Args:
            message (str): Mensaje del usuario
            
        Returns:
            dict: Preferencias extraídas
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """Extrae preferencias de búsqueda de autos del mensaje. 
                    Responde en formato JSON con las siguientes claves si están presentes:
                    - budget: presupuesto máximo (número)
                    - brand: marca del auto (string)
                    - model: modelo del auto (string)
                    - year_min: año mínimo (número)
                    - year_max: año máximo (número)
                    Si no hay preferencias, devuelve un objeto vacío."""},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            preferences = eval(response.choices[0].message.content)
            return preferences
        except Exception as e:
            error_logger.error("Error extracting preferences: %s", str(e))
            return {}

    def _format_car_info(self, cars):
        """
        Formatea la información de los autos para el prompt.
        
        Args:
            cars (list): Lista de autos
            
        Returns:
            str: Información formateada
        """
        if not cars:
            return ""
            
        info = "\nAutos encontrados:\n"
        for car in cars:
            info += f"- {car['make']} {car['model']} {car['year']} ({car['version']})\n"
            info += f"  Precio: ${car['price']:,.2f}\n"
            info += f"  Kilometraje: {car['km']:,} km\n"
            if car.get('bluetooth') == 'Sí':
                info += "  Incluye Bluetooth\n"
            if car.get('car_play') == 'Sí':
                info += "  Incluye CarPlay\n"
            info += "\n"
        return info

    def get_response(self, user_message, conversation_history=None):
        """
        Obtiene una respuesta del modelo de OpenAI, manteniendo el historial de la conversación.
        
        Args:
            user_message (str): El mensaje del usuario.
            conversation_history (list, optional): Lista de mensajes anteriores en la conversación.
                                                 Cada mensaje es un dict: {"role": "user/assistant", "content": "..."}
                                                 
        Returns:
            str: La respuesta del modelo.
        """
        try:
            app_logger.info("Processing user message: %s", user_message[:100])
            
            # Extraer preferencias de búsqueda
            preferences = self._extract_preferences(user_message)
            
            # Buscar autos según preferencias
            cars = []
            if preferences:
                cars = self.car_service.get_recommendations(preferences)
            
            # Preparar información de autos para el prompt
            cars_info = self._format_car_info(cars)
            
            # Inicializar mensajes con el prompt del sistema
            messages = [
                {"role": "system", "content": self.system_prompt + cars_info}
            ]
            
            # Agregar historial de conversación si existe
            if conversation_history:
                # Asegurarse de que el historial no sea demasiado largo
                if len(conversation_history) > 10:
                    conversation_history = conversation_history[-10:]
                    app_logger.debug("Truncated conversation history to last 10 messages")
                messages.extend(conversation_history)
            
            # Agregar el mensaje actual del usuario
            messages.append({"role": "user", "content": user_message})
            
            # Crear la respuesta
            app_logger.debug("Sending request to OpenAI API")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                presence_penalty=0.6,  # Penaliza la repetición de temas
                frequency_penalty=0.6  # Penaliza la repetición de palabras
            )
            
            bot_response = response.choices[0].message.content.strip()
            app_logger.info("Successfully generated response from OpenAI")
            return bot_response
            
        except Exception as e:
            error_logger.error("Error in ChatService: %s", str(e), exc_info=True)
            return "Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, intenta de nuevo más tarde."