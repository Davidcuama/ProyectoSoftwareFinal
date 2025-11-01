"""
Consumidor de servicios externos de otros equipos.
Este módulo se encarga de consumir APIs de equipos precedentes.
"""
import requests
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class ExternalServiceConsumer:
    """
    Clase base para consumir servicios de otros equipos.
    Debe configurarse con la URL del servicio del equipo precedente.
    """
    
    # TODO: Configurar la URL del servicio del equipo precedente
    # Ejemplo: "https://api-equipo-previo.example.com/api/"
    BASE_URL = None
    
    @classmethod
    def set_base_url(cls, url):
        """Configura la URL base del servicio externo."""
        cls.BASE_URL = url
    
    @staticmethod
    def fetch_external_data(endpoint, timeout=10):
        """
        Obtiene datos de un servicio externo.
        
        Args:
            endpoint: Endpoint del servicio (ej: 'products/', 'students/')
            timeout: Tiempo máximo de espera en segundos
        
        Returns:
            dict o list con los datos obtenidos, o None si hay error
        """
        if not ExternalServiceConsumer.BASE_URL:
            logger.warning("Base URL del servicio externo no configurada")
            return None
        
        cache_key = f'external_service_{endpoint}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            url = f"{ExternalServiceConsumer.BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                # Cachear por 5 minutos
                cache.set(cache_key, data, 300)
                return data
            else:
                logger.warning(f"Error al consumir servicio externo: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error al consumir servicio externo: {str(e)}")
            return None
    
    @staticmethod
    def get_external_items(endpoint='items/'):
        """
        Obtiene una lista de items desde el servicio externo.
        Este método es genérico y puede adaptarse según la estructura del servicio.
        
        Args:
            endpoint: Endpoint del servicio
        
        Returns:
            list: Lista de items o lista vacía si hay error
        """
        data = ExternalServiceConsumer.fetch_external_data(endpoint)
        
        if data:
            # Intentar diferentes estructuras comunes de respuesta
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Buscar campos comunes
                for key in ['items', 'data', 'results', 'products', 'students']:
                    if key in data:
                        return data[key]
                # Si no hay clave específica, retornar el diccionario como lista
                return [data]
        
        return []

