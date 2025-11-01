from rest_framework import serializers
from .models import Transaction, Category, Budget, SavingsGoal


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para el modelo Category."""
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'transaction_type', 'transaction_type_display', 'color', 'icon']
        read_only_fields = ['id']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Transaction."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    detail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'description', 'date', 'transaction_type',
            'transaction_type_display', 'category', 'category_name',
            'category_color', 'detail_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_detail_url(self, obj):
        """Retorna la URL para ver los detalles de la transacción."""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/transactions/{obj.id}/update/')
        return f'/transactions/{obj.id}/update/'


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Budget."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    percentage_used = serializers.FloatField(read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'category_color',
            'amount', 'month', 'spent', 'remaining',
            'percentage_used', 'is_over_budget', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'spent', 'remaining', 'percentage_used', 'is_over_budget']


class SavingsGoalSerializer(serializers.ModelSerializer):
    """Serializer para el modelo SavingsGoal."""
    percentage_completed = serializers.FloatField(read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    daily_saving_needed = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = SavingsGoal
        fields = [
            'id', 'name', 'target_amount', 'current_amount',
            'target_date', 'description', 'icon', 'color',
            'is_achieved', 'percentage_completed', 'remaining_amount',
            'days_remaining', 'daily_saving_needed', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'percentage_completed',
            'remaining_amount', 'days_remaining', 'daily_saving_needed'
        ]

