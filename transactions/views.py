from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Q, F
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import json

from .models import Transaction, Category, Tag, Budget, SavingsGoal, RecurringTransaction
from .forms import (
    TransactionForm, CategoryForm, TagForm, BudgetForm, 
    SavingsGoalForm, RecurringTransactionForm
)
from .services import ExchangeRateService, FreeWeatherService
# Importar vista externa (se importa al final para evitar dependencias circulares)
# from .external_views import external_items_view


class TransactionListView(LoginRequiredMixin, ListView):
    """
    Vista para listar transacciones del usuario con filtros.
    """
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filtros
        transaction_type = self.request.GET.get('type')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        search = self.request.GET.get('search')
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        if search:
            queryset = queryset.filter(description__icontains=search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction_types'] = Transaction.TRANSACTION_TYPES
        
        # Estadísticas rápidas
        total_income = Transaction.objects.filter(
            user=self.request.user, 
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_expenses = Transaction.objects.filter(
            user=self.request.user, 
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        context['total_income'] = total_income
        context['total_expenses'] = total_expenses
        context['balance'] = total_income - total_expenses
        
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear nuevas transacciones.
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:transaction_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Transacción creada exitosamente.')
        return super().form_valid(form)


class TransactionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vista para editar transacciones existentes.
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:transaction_list')
    
    def test_func(self):
        transaction = self.get_object()
        return transaction.user == self.request.user
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Transacción actualizada exitosamente.')
        return super().form_valid(form)


class TransactionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Vista para eliminar transacciones.
    """
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions:transaction_list')
    
    def test_func(self):
        transaction = self.get_object()
        return transaction.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Transacción eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


@login_required
def export_transactions(request):
    """
    Vista para exportar transacciones a CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transacciones.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Fecha', 'Tipo', 'Monto', 'Descripción'])
    
    # Aplicar filtros si existen
    queryset = Transaction.objects.filter(user=request.user)
    
    transaction_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if transaction_type:
        queryset = queryset.filter(transaction_type=transaction_type)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    
    for transaction in queryset:
        writer.writerow([
            transaction.date.strftime('%d/%m/%Y'),
            transaction.get_transaction_type_display(),
            transaction.amount,
            transaction.description
        ])
    
    return response


@login_required
def export_report(request, format_type='pdf'):
    """
    Vista para generar reportes en PDF o Excel usando Inversión de Dependencias.
    format_type: 'pdf' o 'excel'
    """
    from .report_generators import ReportGeneratorFactory
    
    # Obtener transacciones del usuario con filtros opcionales
    queryset = Transaction.objects.filter(user=request.user).select_related('category').order_by('-date')
    
    # Aplicar filtros si existen
    transaction_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    category_id = request.GET.get('category')
    
    if transaction_type:
        queryset = queryset.filter(transaction_type=transaction_type)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    
    try:
        # Usar Factory para obtener el generador correcto (Inversión de Dependencias)
        generator = ReportGeneratorFactory.get_generator(format_type)
        
        # Generar nombre del archivo
        from django.utils import timezone
        filename = f"reporte_transacciones_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generar el reporte
        return generator.generate(queryset, filename)
    except ValueError as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('transactions:transaction_list')


@login_required
def transaction_stats_api(request):
    """
    API para obtener estadísticas de transacciones para gráficos.
    """
    # Obtener parámetros
    period = request.GET.get('period', 'month')  # month, year
    months = int(request.GET.get('months', 6))
    
    # Calcular fechas
    end_date = timezone.now().date()
    if period == 'month':
        start_date = end_date - timedelta(days=30 * months)
    else:  # year
        start_date = end_date - timedelta(days=365 * months)
    
    # Obtener datos
    transactions = Transaction.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    )
    
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
    
    return JsonResponse({
        'monthly_data': monthly_data,
    })


# ========== VISTAS PARA CATEGORÍAS ==========

class CategoryListView(LoginRequiredMixin, ListView):
    """Vista para listar categorías del usuario."""
    model = Category
    template_name = 'transactions/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('transaction_type', 'name')


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear categorías."""
    model = Category
    form_class = CategoryForm
    template_name = 'transactions/category_form.html'
    success_url = reverse_lazy('transactions:category_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Categoría creada exitosamente.')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para editar categorías."""
    model = Category
    form_class = CategoryForm
    template_name = 'transactions/category_form.html'
    success_url = reverse_lazy('transactions:category_list')
    
    def test_func(self):
        category = self.get_object()
        return category.user == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada exitosamente.')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar categorías."""
    model = Category
    template_name = 'transactions/category_confirm_delete.html'
    success_url = reverse_lazy('transactions:category_list')
    
    def test_func(self):
        category = self.get_object()
        return category.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Categoría eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ========== VISTAS PARA ETIQUETAS ==========

class TagListView(LoginRequiredMixin, ListView):
    """Vista para listar etiquetas del usuario."""
    model = Tag
    template_name = 'transactions/tag_list.html'
    context_object_name = 'tags'
    
    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user).order_by('name')


class TagCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear etiquetas."""
    model = Tag
    form_class = TagForm
    template_name = 'transactions/tag_form.html'
    success_url = reverse_lazy('transactions:tag_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Etiqueta creada exitosamente.')
        return super().form_valid(form)


class TagUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para editar etiquetas."""
    model = Tag
    form_class = TagForm
    template_name = 'transactions/tag_form.html'
    success_url = reverse_lazy('transactions:tag_list')
    
    def test_func(self):
        tag = self.get_object()
        return tag.user == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Etiqueta actualizada exitosamente.')
        return super().form_valid(form)


class TagDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar etiquetas."""
    model = Tag
    template_name = 'transactions/tag_confirm_delete.html'
    success_url = reverse_lazy('transactions:tag_list')
    
    def test_func(self):
        tag = self.get_object()
        return tag.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Etiqueta eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ========== VISTAS PARA PRESUPUESTOS ==========

class BudgetListView(LoginRequiredMixin, ListView):
    """Vista para listar presupuestos del usuario."""
    model = Budget
    template_name = 'transactions/budget_list.html'
    context_object_name = 'budgets'
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category').order_by('-month', 'category__name')


class BudgetCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear presupuestos."""
    model = Budget
    form_class = BudgetForm
    template_name = 'transactions/budget_form.html'
    success_url = reverse_lazy('transactions:budget_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Presupuesto creado exitosamente.')
        return super().form_valid(form)


class BudgetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para editar presupuestos."""
    model = Budget
    form_class = BudgetForm
    template_name = 'transactions/budget_form.html'
    success_url = reverse_lazy('transactions:budget_list')
    
    def test_func(self):
        budget = self.get_object()
        return budget.user == self.request.user
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Presupuesto actualizado exitosamente.')
        return super().form_valid(form)


class BudgetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar presupuestos."""
    model = Budget
    template_name = 'transactions/budget_confirm_delete.html'
    success_url = reverse_lazy('transactions:budget_list')
    
    def test_func(self):
        budget = self.get_object()
        return budget.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Presupuesto eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ========== VISTAS PARA METAS DE AHORRO ==========

class SavingsGoalListView(LoginRequiredMixin, ListView):
    """Vista para listar metas de ahorro del usuario."""
    model = SavingsGoal
    template_name = 'transactions/savings_goal_list.html'
    context_object_name = 'goals'
    
    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user).order_by('-created_at')


class SavingsGoalCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear metas de ahorro."""
    model = SavingsGoal
    form_class = SavingsGoalForm
    template_name = 'transactions/savings_goal_form.html'
    success_url = reverse_lazy('transactions:savings_goal_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Meta de ahorro creada exitosamente.')
        return super().form_valid(form)


class SavingsGoalUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para editar metas de ahorro."""
    model = SavingsGoal
    form_class = SavingsGoalForm
    template_name = 'transactions/savings_goal_form.html'
    success_url = reverse_lazy('transactions:savings_goal_list')
    
    def test_func(self):
        goal = self.get_object()
        return goal.user == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Meta de ahorro actualizada exitosamente.')
        return super().form_valid(form)


class SavingsGoalDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar metas de ahorro."""
    model = SavingsGoal
    template_name = 'transactions/savings_goal_confirm_delete.html'
    success_url = reverse_lazy('transactions:savings_goal_list')
    
    def test_func(self):
        goal = self.get_object()
        return goal.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Meta de ahorro eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


@login_required
def add_to_savings_goal(request, goal_id):
    """Vista para agregar dinero a una meta de ahorro."""
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            # Convertir a Decimal para trabajar correctamente con DecimalField
            amount = Decimal(str(amount))
            if amount > 0:
                # Actualizar usando F() para evitar problemas de concurrencia
                SavingsGoal.objects.filter(id=goal_id).update(
                    current_amount=F('current_amount') + amount
                )
                # Refrescar el objeto desde la base de datos
                goal.refresh_from_db()
                
                # Verificar si se alcanzó la meta
                if goal.current_amount >= goal.target_amount:
                    goal.current_amount = goal.target_amount
                    goal.is_achieved = True
                    goal.save()
                
                messages.success(request, f'Se agregaron ${amount:.2f} a la meta "{goal.name}".')
            else:
                messages.error(request, 'El monto debe ser mayor a 0.')
        except (ValueError, TypeError, Exception) as e:
            messages.error(request, 'Monto inválido.')
    
    return redirect('transactions:savings_goal_list')


# ========== VISTAS PARA TRANSACCIONES RECURRENTES ==========

class RecurringTransactionListView(LoginRequiredMixin, ListView):
    """Vista para listar transacciones recurrentes del usuario."""
    model = RecurringTransaction
    template_name = 'transactions/recurring_transaction_list.html'
    context_object_name = 'recurring_transactions'
    
    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user).select_related('category').order_by('next_occurrence')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context


class RecurringTransactionCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear transacciones recurrentes."""
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = 'transactions/recurring_transaction_form.html'
    success_url = reverse_lazy('transactions:recurring_transaction_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.next_occurrence = form.cleaned_data['start_date']
        messages.success(self.request, 'Transacción recurrente creada exitosamente.')
        return super().form_valid(form)


class RecurringTransactionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para editar transacciones recurrentes."""
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = 'transactions/recurring_transaction_form.html'
    success_url = reverse_lazy('transactions:recurring_transaction_list')
    
    def test_func(self):
        recurring = self.get_object()
        return recurring.user == self.request.user
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Transacción recurrente actualizada exitosamente.')
        return super().form_valid(form)


class RecurringTransactionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Vista para eliminar transacciones recurrentes."""
    model = RecurringTransaction
    template_name = 'transactions/recurring_transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions:recurring_transaction_list')
    
    def test_func(self):
        recurring = self.get_object()
        return recurring.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Transacción recurrente eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


@login_required
def process_recurring_transactions(request, recurring_id):
    """Vista para procesar manualmente una transacción recurrente."""
    recurring = get_object_or_404(RecurringTransaction, id=recurring_id, user=request.user)
    
    if recurring.is_active and recurring.next_occurrence <= timezone.now().date():
        transaction = recurring.create_transaction()
        messages.success(request, f'Transacción "{transaction.description}" creada exitosamente.')
    else:
        messages.warning(request, 'Esta transacción recurrente no está lista para ser procesada.')
    
    return redirect('transactions:recurring_transaction_list')


@login_required
def toggle_recurring_transaction(request, recurring_id):
    """Vista para activar/desactivar una transacción recurrente."""
    recurring = get_object_or_404(RecurringTransaction, id=recurring_id, user=request.user)
    recurring.is_active = not recurring.is_active
    recurring.save()
    
    status = 'activada' if recurring.is_active else 'desactivada'
    messages.success(request, f'Transacción recurrente {status} exitosamente.')
    
    return redirect('transactions:recurring_transaction_list')
