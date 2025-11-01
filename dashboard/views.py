from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.http import JsonResponse

from transactions.models import Transaction, Category, Budget, SavingsGoal, RecurringTransaction
from transactions.services import ExchangeRateService, FreeWeatherService


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista principal del dashboard con estadísticas y gráficos.
    """
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Estadísticas generales
        total_income = Transaction.objects.filter(
            user=user, 
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_expenses = Transaction.objects.filter(
            user=user, 
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        balance = total_income - total_expenses
        
        # Estadísticas del mes actual
        current_month = timezone.now().date().replace(day=1)
        next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        month_income = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__gte=current_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_expenses = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__gte=current_month,
            date__lt=next_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_balance = month_income - month_expenses
        
        # Transacciones recientes
        recent_transactions = Transaction.objects.filter(
            user=user
        ).select_related('category').prefetch_related('tags').order_by('-date', '-created_at')[:10]
        
        # Presupuestos del mes actual
        current_month = timezone.now().date().replace(day=1)
        current_budgets = Budget.objects.filter(
            user=user,
            month=current_month
        ).select_related('category')
        
        # Metas de ahorro activas
        active_savings_goals = SavingsGoal.objects.filter(
            user=user,
            is_achieved=False
        ).order_by('target_date')[:5]
        
        # Transacciones recurrentes próximas
        upcoming_recurring = RecurringTransaction.objects.filter(
            user=user,
            is_active=True
        ).select_related('category').order_by('next_occurrence')[:5]
        
        # Gastos por categoría del mes
        category_expenses = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__gte=current_month,
            date__lt=next_month,
            category__isnull=False
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount')
        ).order_by('-total')[:10]
        
        # Datos para gráficos
        chart_data = self.get_chart_data(user)
        
        from django.utils import timezone as tz
        today = tz.now().date()
        
        # Obtener información de servicios externos
        weather_data = FreeWeatherService.get_weather_simple("Medellin")
        exchange_rates = ExchangeRateService.get_exchange_rates()
        usd_to_cop = ExchangeRateService.get_currency_rate('COP') if exchange_rates else None
        
        context.update({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance,
            'month_income': month_income,
            'month_expenses': month_expenses,
            'month_balance': month_balance,
            'recent_transactions': recent_transactions,
            'current_budgets': current_budgets,
            'active_savings_goals': active_savings_goals,
            'upcoming_recurring': upcoming_recurring,
            'category_expenses': category_expenses,
            'chart_data': json.dumps(chart_data),
            'today': today,
            'weather_data': weather_data,
            'usd_to_cop': usd_to_cop,
        })
        
        return context
    
    def get_chart_data(self, user):
        """
        Genera datos para los gráficos del dashboard.
        """
        # Obtener datos de los últimos 6 meses
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=180)
        
        transactions = Transaction.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).select_related('category')
        
        # Datos para gráfico de línea (ingresos vs gastos por mes)
        monthly_data = {}
        for transaction in transactions:
            month_key = transaction.date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'income': 0, 'expense': 0}
            
            if transaction.transaction_type == 'income':
                monthly_data[month_key]['income'] += float(transaction.amount)
            else:
                monthly_data[month_key]['expense'] += float(transaction.amount)
        
        # Datos para gráfico de torta (gastos por categoría - TODOS los meses, no solo el actual)
        # Obtener todos los gastos con categoría de los últimos 6 meses
        category_data = {}
        category_expenses_qs = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__gte=start_date,
            date__lte=end_date,
            category__isnull=False
        ).select_related('category')
        
        for transaction in category_expenses_qs:
            cat_name = transaction.category.name
            if cat_name not in category_data:
                category_data[cat_name] = {
                    'amount': 0,
                    'color': transaction.category.color
                }
            category_data[cat_name]['amount'] += float(transaction.amount)
        
        # Convertir category_data a formato simple para el gráfico
        category_expenses = {}
        for cat_name, cat_info in category_data.items():
            category_expenses[cat_name] = cat_info['amount']
        
        return {
            'monthly_data': monthly_data,
            'category_data': category_data,
            'category_expenses': category_expenses,  # Agregar formato simple para el gráfico
        }


@login_required
def dashboard_stats_api(request):
    """
    API para obtener estadísticas del dashboard en tiempo real.
    """
    user = request.user
    
    # Estadísticas del mes actual
    current_month = timezone.now().date().replace(day=1)
    next_month = (current_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    month_income = Transaction.objects.filter(
        user=user,
        transaction_type='income',
        date__gte=current_month,
        date__lt=next_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    month_expenses = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        date__gte=current_month,
        date__lt=next_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    return JsonResponse({
        'month_income': float(month_income),
        'month_expenses': float(month_expenses),
        'month_balance': float(month_income - month_expenses),
    })
