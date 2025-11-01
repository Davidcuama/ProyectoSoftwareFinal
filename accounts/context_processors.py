"""
Context processor simplificado para idioma.
"""
def language_context(request):
    """Context processor que lee el idioma de la sesión."""
    # Intentar leer de la sesión primero
    lang = request.session.get('django_language', None)
    
    # Si no está en sesión, usar LANGUAGE_CODE del request (procesado por LocaleMiddleware)
    if not lang and hasattr(request, 'LANGUAGE_CODE'):
        lang = request.LANGUAGE_CODE
    
    # Si aún no hay nada, usar el default
    if not lang:
        lang = 'es'
    
    # Normalizar: solo tomar los primeros 2 caracteres (es, en)
    if isinstance(lang, str):
        lang = lang[:2].lower()
    else:
        lang = 'es'
    
    # Asegurar que sea válido
    if lang not in ['es', 'en']:
        lang = 'es'
    
    return {
        'current_language': lang,
        'is_spanish': lang == 'es',
        'is_english': lang == 'en',
    }

