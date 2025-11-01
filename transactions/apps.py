from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'
    
    def ready(self):
        """
        Inicialización de la app cuando Django está listo.
        Configura automáticamente el servicio externo desde settings.
        """
        from django.conf import settings
        from .external_service_consumer import ExternalServiceConsumer
        
        # Configurar URL del servicio externo si está definida en settings
        if hasattr(settings, 'EXTERNAL_SERVICE_BASE_URL') and settings.EXTERNAL_SERVICE_BASE_URL:
            ExternalServiceConsumer.set_base_url(settings.EXTERNAL_SERVICE_BASE_URL)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Servicio externo configurado: {settings.EXTERNAL_SERVICE_BASE_URL}")