"""
Template tags simplificados para traducción.
"""
from django import template
from transactions.translations import get_translation

register = template.Library()


@register.simple_tag(takes_context=True)
def trans_custom(context, key):
    """
    Template tag simple para traducir texto.
    Uso: {% trans_custom "Dashboard" %}
    """
    lang = context.get('current_language', 'es')
    return get_translation(key, lang)


@register.simple_tag(takes_context=True)
def trans(context, key):
    """Alias para trans_custom."""
    return trans_custom(context, key)


@register.simple_tag(takes_context=True)
def translate_type(context, transaction_type):
    """
    Traduce tipos de transacción.
    Uso: {% translate_type category.get_transaction_type_display %}
    """
    lang = context.get('current_language', 'es')
    
    # Mapeo simple de tipos
    types = {
        'Ingreso': 'Ingreso' if lang == 'es' else 'Income',
        'Gasto': 'Gasto' if lang == 'es' else 'Expense',
        'Ambos': 'Ambos' if lang == 'es' else 'Both',
        'Income': 'Ingreso' if lang == 'es' else 'Income',
        'Expense': 'Gasto' if lang == 'es' else 'Expense',
        'Both': 'Ambos' if lang == 'es' else 'Both',
    }
    
    return types.get(transaction_type, transaction_type)


@register.inclusion_tag('transactions/language_selector.html', takes_context=True)
def language_selector(context):
    """Template tag para el selector de idioma."""
    return {
        'current_language': context.get('current_language', 'es'),
        'languages': [('es', 'Español'), ('en', 'English')]
    }

