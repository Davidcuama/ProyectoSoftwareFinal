"""
Servicio mock para pruebas locales.
Simula la respuesta del equipo precedente cuando no hay URL configurada.
"""

MOCK_DATA = [
    {
        "id": 1,
        "name": "Producto de Prueba 1",
        "title": "Producto de Prueba 1",
        "description": "Este es un producto de ejemplo para probar el consumo de servicios externos. Simula datos del equipo precedente.",
        "detail": "Este es un producto de ejemplo para probar el consumo de servicios externos.",
        "url": "http://localhost:8000/transactions/"
    },
    {
        "id": 2,
        "name": "Producto de Prueba 2",
        "title": "Producto de Prueba 2",
        "description": "Otro producto de ejemplo para testing del sistema de consumo de servicios.",
        "detail": "Otro producto de ejemplo para testing del sistema.",
        "url": "http://localhost:8000/transactions/"
    },
    {
        "id": 3,
        "name": "Producto de Prueba 3",
        "title": "Producto de Prueba 3",
        "description": "Tercer producto de prueba. Cuando tengas la URL real del equipo precedente, estos datos serán reemplazados.",
        "detail": "Tercer producto de prueba para verificar la funcionalidad.",
        "url": "http://localhost:8000/transactions/"
    },
    {
        "id": 4,
        "name": "Servicio de Ejemplo",
        "title": "Servicio de Ejemplo",
        "description": "Este item demuestra cómo se verán los datos del equipo precedente cuando se configure la URL real.",
        "detail": "Item de ejemplo para demostración.",
        "url": "http://localhost:8000/transactions/"
    }
]

