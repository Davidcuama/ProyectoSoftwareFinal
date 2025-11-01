"""
Vistas para mostrar datos consumidos de servicios externos.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .external_service_consumer import ExternalServiceConsumer


@login_required
def external_items_view(request):
    """
    Vista para mostrar items consumidos del servicio del equipo precedente.
    Esta vista crea una nueva ruta como se especifica en el entregable.
    """
    items = []
    using_mock = False
    
    # Si está en modo desarrollo y no hay URL configurada, usar datos mock
    if settings.DEBUG and not settings.EXTERNAL_SERVICE_BASE_URL:
        try:
            from .mock_service import MOCK_DATA
            items = MOCK_DATA
            using_mock = True
            messages.info(
                request, 
                "⚠️ <strong>Modo Prueba:</strong> Usando datos de prueba (mock). "
                "Configura EXTERNAL_SERVICE_BASE_URL en settings.py para usar datos reales del equipo precedente."
            )
        except ImportError:
            pass
    
    # Si no estamos usando mock, intentar obtener datos reales
    if not using_mock:
        items = ExternalServiceConsumer.get_external_items()
        
        if not items:
            messages.info(
                request,
                "No hay datos disponibles del servicio externo. "
                "Asegúrate de configurar la URL del servicio del equipo precedente en settings.py "
                "(EXTERNAL_SERVICE_BASE_URL)."
            )
    
    context = {
        'items': items,
        'has_data': len(items) > 0,
        'using_mock': using_mock,
    }
    
    return render(request, 'transactions/external_items.html', context)

