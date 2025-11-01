from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import Transaction, Category, Budget, SavingsGoal
from .serializers import (
    TransactionSerializer, CategorySerializer,
    BudgetSerializer, SavingsGoalSerializer
)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar transacciones en formato JSON.
    Proporciona información relevante de transacciones para consumo externo.
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra las transacciones del usuario autenticado."""
        user = self.request.user
        queryset = Transaction.objects.filter(user=user).select_related('category').order_by('-date', '-created_at')
        
        # Filtros opcionales
        transaction_type = self.request.query_params.get('type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Lista las transacciones del usuario con información relevante."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Información adicional
        total_income = queryset.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_expenses = queryset.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        return Response({
            'transactions': serializer.data,
            'summary': {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'balance': float(total_income - total_expenses),
                'count': queryset.count()
            },
            'filters': {
                'type': request.query_params.get('type', None),
                'category': request.query_params.get('category', None),
            }
        })


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar categorías en formato JSON.
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra las categorías del usuario autenticado."""
        return Category.objects.filter(user=self.request.user).order_by('name')


class BudgetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar presupuestos en formato JSON.
    """
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra los presupuestos del usuario autenticado."""
        user = self.request.user
        queryset = Budget.objects.filter(user=user).select_related('category').order_by('-month')
        
        # Filtro por mes opcional
        month = self.request.query_params.get('month', None)
        if month:
            queryset = queryset.filter(month__startswith=month)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def current_month(self, request):
        """Retorna los presupuestos del mes actual."""
        current_month = timezone.now().date().replace(day=1)
        budgets = Budget.objects.filter(
            user=request.user,
            month=current_month
        ).select_related('category')
        
        serializer = self.get_serializer(budgets, many=True)
        
        total_budget = budgets.aggregate(total=Sum('amount'))['total'] or 0
        total_spent = sum(budget.spent for budget in budgets)
        
        return Response({
            'budgets': serializer.data,
            'summary': {
                'total_budget': float(total_budget),
                'total_spent': float(total_spent),
                'remaining': float(total_budget - total_spent),
                'month': current_month.strftime('%Y-%m')
            }
        })


class SavingsGoalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar metas de ahorro en formato JSON.
    """
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra las metas de ahorro del usuario autenticado."""
        queryset = SavingsGoal.objects.filter(user=self.request.user).order_by('-created_at')
        
        # Filtro por estado
        is_achieved = self.request.query_params.get('achieved', None)
        if is_achieved is not None:
            is_achieved = is_achieved.lower() == 'true'
            queryset = queryset.filter(is_achieved=is_achieved)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retorna solo las metas de ahorro activas (no alcanzadas)."""
        goals = SavingsGoal.objects.filter(
            user=request.user,
            is_achieved=False
        ).order_by('target_date')
        
        serializer = self.get_serializer(goals, many=True)
        
        total_target = goals.aggregate(total=Sum('target_amount'))['total'] or 0
        total_current = goals.aggregate(total=Sum('current_amount'))['total'] or 0
        
        return Response({
            'goals': serializer.data,
            'summary': {
                'total_target': float(total_target),
                'total_current': float(total_current),
                'total_remaining': float(total_target - total_current),
                'count': goals.count()
            }
        })

