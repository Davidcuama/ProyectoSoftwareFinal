from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction, Category, Tag, Budget, SavingsGoal, RecurringTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'transaction_type', 'color_display', 'icon', 'is_default', 'created_at']
    list_filter = ['transaction_type', 'is_default', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; width: 20px; height: 20px; display: inline-block; border-radius: 3px;"></span> {}',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color_display', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; width: 20px; height: 20px; display: inline-block; border-radius: 3px;"></span> {}',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount', 'category', 'date', 'description_short', 'created_at']
    list_filter = ['transaction_type', 'date', 'category', 'created_at', 'user']
    search_fields = ['description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'transaction_type', 'amount', 'category')
        }),
        ('Detalles', {
            'fields': ('description', 'date', 'tags', 'recurring_transaction')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Descripción'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category', 'recurring_transaction').prefetch_related('tags')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'month', 'spent_display', 'percentage_used_display', 'is_over_budget_display']
    list_filter = ['month', 'created_at', 'user']
    search_fields = ['category__name', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'spent_display', 'percentage_used_display']
    date_hierarchy = 'month'
    
    def spent_display(self, obj):
        return f"${obj.spent:.2f}"
    spent_display.short_description = 'Gastado'
    
    def percentage_used_display(self, obj):
        percentage = obj.percentage_used
        color = 'red' if percentage > 100 else 'orange' if percentage > 80 else 'green'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, percentage
        )
    percentage_used_display.short_description = '% Usado'
    
    def is_over_budget_display(self, obj):
        if obj.is_over_budget:
            return format_html('<span style="color: red;">⚠ Excedido</span>')
        return format_html('<span style="color: green;">✓ Dentro</span>')
    is_over_budget_display.short_description = 'Estado'


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'target_amount', 'current_amount', 'percentage_completed_display', 'target_date', 'is_achieved']
    list_filter = ['is_achieved', 'target_date', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'percentage_completed_display', 'remaining_amount_display']
    
    def percentage_completed_display(self, obj):
        return f"{obj.percentage_completed:.1f}%"
    percentage_completed_display.short_description = '% Completado'
    
    def remaining_amount_display(self, obj):
        return f"${obj.remaining_amount:.2f}"
    remaining_amount_display.short_description = 'Restante'


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'transaction_type', 'amount', 'frequency', 'next_occurrence', 'is_active']
    list_filter = ['transaction_type', 'frequency', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'next_occurrence'
