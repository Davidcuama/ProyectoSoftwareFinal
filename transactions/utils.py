"""
Utilidades para la aplicación de transacciones.
"""
from .models import Category


def create_default_categories(user):
    """
    Crea categorías por defecto para un nuevo usuario.
    
    Args:
        user: Instancia de User para el cual crear las categorías
    """
    # Categorías de Ingresos
    income_categories = [
        {'name': 'Salario', 'icon': 'fas fa-briefcase', 'color': '#28a745', 'transaction_type': 'income'},
        {'name': 'Freelance', 'icon': 'fas fa-laptop-code', 'color': '#17a2b8', 'transaction_type': 'income'},
        {'name': 'Inversiones', 'icon': 'fas fa-chart-line', 'color': '#ffc107', 'transaction_type': 'income'},
        {'name': 'Otros Ingresos', 'icon': 'fas fa-money-bill-wave', 'color': '#6c757d', 'transaction_type': 'income'},
    ]
    
    # Categorías de Gastos
    expense_categories = [
        {'name': 'Alimentación', 'icon': 'fas fa-utensils', 'color': '#dc3545', 'transaction_type': 'expense'},
        {'name': 'Transporte', 'icon': 'fas fa-car', 'color': '#007bff', 'transaction_type': 'expense'},
        {'name': 'Vivienda', 'icon': 'fas fa-home', 'color': '#6610f2', 'transaction_type': 'expense'},
        {'name': 'Servicios', 'icon': 'fas fa-bolt', 'color': '#fd7e14', 'transaction_type': 'expense'},
        {'name': 'Entretenimiento', 'icon': 'fas fa-film', 'color': '#e83e8c', 'transaction_type': 'expense'},
        {'name': 'Salud', 'icon': 'fas fa-heartbeat', 'color': '#dc3545', 'transaction_type': 'expense'},
        {'name': 'Educación', 'icon': 'fas fa-graduation-cap', 'color': '#20c997', 'transaction_type': 'expense'},
        {'name': 'Ropa', 'icon': 'fas fa-tshirt', 'color': '#6f42c1', 'transaction_type': 'expense'},
        {'name': 'Otros Gastos', 'icon': 'fas fa-shopping-cart', 'color': '#6c757d', 'transaction_type': 'expense'},
    ]
    
    # Crear categorías de ingresos
    for cat_data in income_categories:
        Category.objects.get_or_create(
            user=user,
            name=cat_data['name'],
            defaults={
                'transaction_type': cat_data['transaction_type'],
                'icon': cat_data['icon'],
                'color': cat_data['color'],
                'is_default': True,
            }
        )
    
    # Crear categorías de gastos
    for cat_data in expense_categories:
        Category.objects.get_or_create(
            user=user,
            name=cat_data['name'],
            defaults={
                'transaction_type': cat_data['transaction_type'],
                'icon': cat_data['icon'],
                'color': cat_data['color'],
                'is_default': True,
            }
        )

