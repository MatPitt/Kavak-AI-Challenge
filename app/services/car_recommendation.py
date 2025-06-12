import pandas as pd
import os
from app.core.config import Config
from app.core.logger import app_logger, error_logger

class CarRecommendationService:
    def __init__(self):
        self.catalog = None
        app_logger.info("Initializing CarRecommendationService")
        self.load_catalog()

    def load_catalog(self):
        """Carga el catálogo de autos desde el archivo CSV."""
        try:
            # Obtener la ruta absoluta del archivo
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            catalog_path = os.path.join(base_dir, Config.CATALOG_PATH)
            
            app_logger.info("Loading car catalog from: %s", catalog_path)
            
            if not os.path.exists(catalog_path):
                error_logger.error("Catalog file not found at: %s", catalog_path)
                raise FileNotFoundError(f"Catalog file not found at: {catalog_path}")
            
            # Cargar el catálogo y convertir tipos de datos
            self.catalog = pd.read_csv(catalog_path)
            
            # Convertir columnas numéricas
            numeric_columns = ['price', 'km', 'year']
            for col in numeric_columns:
                if col in self.catalog.columns:
                    self.catalog[col] = pd.to_numeric(self.catalog[col], errors='coerce')
            
            app_logger.info("Successfully loaded catalog with %d cars", len(self.catalog))
            
            # Verificar que el catálogo tenga datos
            if self.catalog.empty:
                error_logger.error("Catalog file is empty")
                raise ValueError("Catalog file is empty")
                
            # Verificar columnas requeridas
            required_columns = ['make', 'model', 'year', 'price', 'km', 'version']
            missing_columns = [col for col in required_columns if col not in self.catalog.columns]
            if missing_columns:
                error_logger.error("Missing required columns in catalog: %s", missing_columns)
                raise ValueError(f"Missing required columns in catalog: {missing_columns}")
                
        except Exception as e:
            error_logger.error("Error loading car catalog: %s", str(e), exc_info=True)
            self.catalog = pd.DataFrame()
            app_logger.warning("Initialized empty catalog due to loading error")

    def get_recommendations(self, preferences):
        """
        Obtiene recomendaciones de autos basadas en las preferencias del usuario.
        
        Args:
            preferences (dict): Diccionario con las preferencias del usuario
                Ejemplo: {
                    'budget': 500000,
                    'brand': 'Toyota',
                    'model': 'Corolla',
                    'year_min': 2018,
                    'year_max': 2023
                }
        
        Returns:
            list: Lista de autos recomendados
        """
        try:
            app_logger.info("Getting car recommendations with preferences: %s", preferences)
            
            if self.catalog.empty:
                app_logger.warning("No recommendations possible: catalog is empty")
                return []

            # Crear una copia del catálogo para no modificar el original
            filtered_catalog = self.catalog.copy()

            # Filtrar por presupuesto
            if 'budget' in preferences and preferences['budget']:
                try:
                    budget = float(preferences['budget'])
                    filtered_catalog = filtered_catalog[filtered_catalog['price'] <= budget]
                    app_logger.debug("Filtered by budget: %f", budget)
                except (ValueError, TypeError) as e:
                    app_logger.warning("Invalid budget value: %s", preferences['budget'])

            # Filtrar por marca
            if 'brand' in preferences and preferences['brand']:
                try:
                    brand = str(preferences['brand']).lower()
                    filtered_catalog = filtered_catalog[
                        filtered_catalog['make'].str.lower().str.contains(brand, na=False)
                    ]
                    app_logger.debug("Filtered by brand: %s", brand)
                except Exception as e:
                    app_logger.warning("Error filtering by brand: %s", str(e))

            # Filtrar por modelo
            if 'model' in preferences and preferences['model']:
                try:
                    model = str(preferences['model']).lower()
                    filtered_catalog = filtered_catalog[
                        filtered_catalog['model'].str.lower().str.contains(model, na=False)
                    ]
                    app_logger.debug("Filtered by model: %s", model)
                except Exception as e:
                    app_logger.warning("Error filtering by model: %s", str(e))

            # Filtrar por año
            if 'year_min' in preferences and preferences['year_min']:
                try:
                    year_min = int(preferences['year_min'])
                    filtered_catalog = filtered_catalog[filtered_catalog['year'] >= year_min]
                    app_logger.debug("Filtered by min year: %d", year_min)
                except (ValueError, TypeError) as e:
                    app_logger.warning("Invalid year_min value: %s", preferences['year_min'])

            if 'year_max' in preferences and preferences['year_max']:
                try:
                    year_max = int(preferences['year_max'])
                    filtered_catalog = filtered_catalog[filtered_catalog['year'] <= year_max]
                    app_logger.debug("Filtered by max year: %d", year_max)
                except (ValueError, TypeError) as e:
                    app_logger.warning("Invalid year_max value: %s", preferences['year_max'])

            # Ordenar por precio
            recommendations = filtered_catalog.sort_values('price').head(5)
            app_logger.info("Found %d recommendations", len(recommendations))

            return recommendations.to_dict('records')

        except Exception as e:
            error_logger.error("Error getting car recommendations: %s", str(e), exc_info=True)
            return []

    def get_car_details(self, car_id):
        """
        Obtiene los detalles de un auto específico.
        
        Args:
            car_id: ID del auto
            
        Returns:
            dict: Detalles del auto
        """
        try:
            app_logger.info("Getting details for car ID: %d", car_id)
            
            if self.catalog.empty:
                app_logger.warning("No car details possible: catalog is empty")
                return None

            car = self.catalog[self.catalog['stock_id'] == car_id]
            if car.empty:
                app_logger.warning("Car not found with ID: %d", car_id)
                return None

            app_logger.info("Successfully retrieved details for car ID: %d", car_id)
            return car.iloc[0].to_dict()
            
        except Exception as e:
            error_logger.error("Error getting car details: %s", str(e), exc_info=True)
            return None 