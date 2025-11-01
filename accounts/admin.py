from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at', 'updated_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user', 'role')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
