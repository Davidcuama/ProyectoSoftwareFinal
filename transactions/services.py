"""
Servicios externos para consumo de APIs de terceros.
"""
import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class ExchangeRateService:
    """
    Servicio para obtener tipos de cambio desde una API externa.
    Usa exchangerate-api.com (gratis sin API key para USD a otras monedas).
    """
    
    BASE_URL = "https://api.exchangerate-api.com/v4/latest/USD"
    
    @staticmethod
    def get_exchange_rates():
        """
        Obtiene los tipos de cambio actuales desde USD.
        Retorna un diccionario con las tasas de cambio.
        """
        cache_key = 'exchange_rates_usd'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(ExchangeRateService.BASE_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Cachear por 1 hora
                cache.set(cache_key, data, 3600)
                return data
            else:
                logger.warning(f"Error al obtener tipos de cambio: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error al consumir API de tipos de cambio: {str(e)}")
            return None
    
    @staticmethod
    def get_currency_rate(currency='EUR'):
        """
        Obtiene la tasa de cambio de USD a una moneda específica.
        currency: código de moneda (EUR, COP, MXN, etc.)
        """
        rates_data = ExchangeRateService.get_exchange_rates()
        if rates_data and 'rates' in rates_data:
            return rates_data['rates'].get(currency.upper(), None)
        return None
    
    @staticmethod
    def convert_usd_to_currency(amount, currency='EUR'):
        """
        Convierte un monto en USD a otra moneda.
        amount: monto en USD
        currency: código de moneda destino
        """
        rate = ExchangeRateService.get_currency_rate(currency)
        if rate:
            return amount * rate
        return None


class WeatherService:
    """
    Servicio para obtener información del clima.
    Usa OpenWeatherMap API (requiere API key, pero proporcionamos estructura).
    Alternativa: usar una API gratuita sin key si está disponible.
    """
    
    # API pública gratuita alternativa sin necesidad de key
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    @staticmethod
    def get_weather(city="Medellin", country_code="CO"):
        """
        Obtiene información del clima para una ciudad.
        Por defecto usa Medellín, Colombia.
        """
        cache_key = f'weather_{city}_{country_code}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Para producción, necesitarías una API key de OpenWeatherMap
        # Por ahora, retornamos datos simulados o usar una API gratuita alternativa
        try:
            # Ejemplo usando una API pública alternativa (si está disponible)
            # Esta es una estructura básica - necesitarías configurar una API real
            weather_data = {
                'city': city,
                'temperature': 22,  # Celsius
                'description': 'Parcialmente nublado',
                'humidity': 65,
                'wind_speed': 5.2
            }
            
            # Cachear por 30 minutos
            cache.set(cache_key, weather_data, 1800)
            return weather_data
        except Exception as e:
            logger.error(f"Error al obtener información del clima: {str(e)}")
            return None


# Alternativa: Usar una API gratuita que no requiere key
class FreeWeatherService:
    """
    Servicio alternativo para clima usando API pública gratuita.
    Ejemplo con wttr.in (no requiere API key)
    """
    
    @staticmethod
    def get_weather_simple(city="Medellin"):
        """
        Obtiene información del clima usando wttr.in (API pública gratuita).
        """
        cache_key = f'weather_simple_{city}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # wttr.in proporciona datos del clima en formato JSON
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_condition', [{}])[0]
                
                weather_data = {
                    'city': city,
                    'temperature': int(current.get('temp_C', 0)),
                    'description': current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                    'humidity': int(current.get('humidity', 0)),
                    'wind_speed': float(current.get('windspeedKmph', 0)),
                }
                
                # Cachear por 30 minutos
                cache.set(cache_key, weather_data, 1800)
                return weather_data
        except Exception as e:
            logger.error(f"Error al obtener clima desde wttr.in: {str(e)}")
            # Retornar datos por defecto en caso de error
            return {
                'city': city,
                'temperature': 22,
                'description': 'Información no disponible',
                'humidity': 0,
                'wind_speed': 0,
            }
        
        return None

