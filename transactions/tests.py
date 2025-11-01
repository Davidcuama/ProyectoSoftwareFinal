from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from .models import Transaction, Category, Budget


class TransactionModelTest(TestCase):
    """
    Pruebas unitarias para el modelo Transaction.
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Usar get_or_create para evitar conflictos con categorías existentes
        self.category, _ = Category.objects.get_or_create(
            user=self.user,
            name='Alimentación Test',
            defaults={'transaction_type': 'expense'}
        )
    
    def test_create_income_transaction(self):
        """Prueba la creación de una transacción de ingreso."""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=1000.00,
            description='Salario mensual',
            date=timezone.now().date(),
            transaction_type='income',
            category=self.category
        )
        
        self.assertEqual(transaction.amount, 1000.00)
        self.assertEqual(transaction.transaction_type, 'income')
        self.assertTrue(transaction.is_income)
        self.assertFalse(transaction.is_expense)
        self.assertEqual(transaction.user, self.user)
    
    def test_create_expense_transaction(self):
        """Prueba la creación de una transacción de gasto."""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=50.00,
            description='Compra supermercado',
            date=timezone.now().date(),
            transaction_type='expense',
            category=self.category
        )
        
        self.assertEqual(transaction.amount, 50.00)
        self.assertEqual(transaction.transaction_type, 'expense')
        self.assertTrue(transaction.is_expense)
        self.assertFalse(transaction.is_income)
        self.assertEqual(transaction.user, self.user)


class BudgetModelTest(TestCase):
    """
    Pruebas unitarias para el modelo Budget.
    """
    
    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        # Usar get_or_create para evitar conflictos con categorías existentes
        self.category, _ = Category.objects.get_or_create(
            user=self.user,
            name='Transporte Test',
            defaults={'transaction_type': 'expense'}
        )
        self.month = timezone.now().date().replace(day=1)
    
    def test_budget_creation(self):
        """Prueba la creación de un presupuesto."""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=500.00,
            month=self.month
        )
        
        self.assertEqual(budget.amount, 500.00)
        self.assertEqual(budget.user, self.user)
        self.assertEqual(budget.category, self.category)
        self.assertEqual(budget.spent, 0)  # Sin gastos aún
        self.assertEqual(budget.remaining, 500.00)
        self.assertEqual(budget.percentage_used, 0)
        self.assertFalse(budget.is_over_budget)
    
    def test_budget_spent_calculation(self):
        """Prueba el cálculo del gasto en un presupuesto."""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=500.00,
            month=self.month
        )
        
        # Crear una transacción de gasto en el mismo mes
        Transaction.objects.create(
            user=self.user,
            amount=150.00,
            description='Transporte',
            date=self.month + timedelta(days=5),
            transaction_type='expense',
            category=self.category
        )
        
        # Recargar el presupuesto para obtener los valores actualizados
        budget.refresh_from_db()
        
        self.assertEqual(budget.spent, 150.00)
        self.assertEqual(budget.remaining, 350.00)
        self.assertEqual(budget.percentage_used, 30.0)  # 150/500 * 100
        self.assertFalse(budget.is_over_budget)
        
        # Agregar más gastos para exceder el presupuesto
        Transaction.objects.create(
            user=self.user,
            amount=400.00,
            description='Más transporte',
            date=self.month + timedelta(days=10),
            transaction_type='expense',
            category=self.category
        )
        
        budget.refresh_from_db()
        self.assertEqual(budget.spent, 550.00)
        self.assertTrue(budget.is_over_budget)
        self.assertGreaterEqual(budget.percentage_used, 100)
