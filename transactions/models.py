from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import datetime, timedelta


class Category(models.Model):
    """
    Modelo para categorías de transacciones.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Ingreso'),
        ('expense', 'Gasto'),
        ('both', 'Ambos'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name='categories')
    name = models.CharField(max_length=100, verbose_name="Nombre")
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        default='expense',
        verbose_name="Tipo de transacción"
    )
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Color")
    icon = models.CharField(max_length=50, default='fas fa-tag', verbose_name="Icono")
    is_default = models.BooleanField(default=False, verbose_name="Categoría predefinida")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']
        unique_together = [['name', 'user']]
    
    def __str__(self):
        return f"{self.name} ({self.get_transaction_type_display()})"


class Tag(models.Model):
    """
    Modelo para etiquetas de transacciones.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name='tags')
    name = models.CharField(max_length=50, verbose_name="Nombre")
    color = models.CharField(max_length=7, default='#6c757d', verbose_name="Color")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    
    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
        ordering = ['name']
        unique_together = [['name', 'user']]
    
    def __str__(self):
        return self.name


class Transaction(models.Model):
    """
    Modelo base para transacciones (ingresos y gastos).
    """
    TRANSACTION_TYPES = [
        ('income', 'Ingreso'),
        ('expense', 'Gasto'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name='transactions')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name="Monto"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    date = models.DateField(default=timezone.now, verbose_name="Fecha")
    transaction_type = models.CharField(
        max_length=10, 
        choices=TRANSACTION_TYPES,
        verbose_name="Tipo de transacción"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Categoría",
        related_name='transactions'
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Etiquetas", related_name='transactions')
    recurring_transaction = models.ForeignKey(
        'RecurringTransaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Transacción recurrente",
        related_name='instances'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.description[:30]}"
    
    @property
    def is_income(self):
        """Retorna True si es un ingreso."""
        return self.transaction_type == 'income'
    
    @property
    def is_expense(self):
        """Retorna True si es un gasto."""
        return self.transaction_type == 'expense'


class Budget(models.Model):
    """
    Modelo para presupuestos mensuales por categoría.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name='budgets')
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        verbose_name="Categoría",
        related_name='budgets',
        limit_choices_to={'transaction_type': 'expense'}
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        verbose_name="Monto del presupuesto"
    )
    month = models.DateField(verbose_name="Mes del presupuesto")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"
        ordering = ['-month', 'category__name']
        unique_together = [['user', 'category', 'month']]
    
    def __str__(self):
        return f"{self.category.name} - {self.month.strftime('%B %Y')} - {self.amount}"
    
    @property
    def spent(self):
        """Calcula el total gastado en esta categoría para el mes."""
        start_date = self.month.replace(day=1)
        if self.month.month == 12:
            end_date = self.month.replace(year=self.month.year + 1, month=1, day=1)
        else:
            end_date = self.month.replace(month=self.month.month + 1, day=1)
        
        total = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_type='expense',
            date__gte=start_date,
            date__lt=end_date
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        return total
    
    @property
    def remaining(self):
        """Calcula el monto restante del presupuesto."""
        return self.amount - self.spent
    
    @property
    def percentage_used(self):
        """Calcula el porcentaje utilizado del presupuesto."""
        if self.amount == 0:
            return 0
        return min(100, (self.spent / self.amount) * 100)
    

    @property
    def percentage_used_css(self):
        """Valor formateado para usar en CSS/atributos (usar punto decimal, no localizado)."""
        if self.amount == 0:
            return "0%"
        val = min(100, (self.spent / self.amount) * 100)
        try:
            # Asegurar un string con punto decimal y 1 decimal y añadir '%'
            return format(float(val), '.1f') + '%'
        except Exception:
            return str(val) + '%'
    

    @property
    def is_over_budget(self):
        """Retorna True si se excedió el presupuesto."""
        return self.spent > self.amount


class SavingsGoal(models.Model):
    """
    Modelo para metas de ahorro.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name='savings_goals')
    name = models.CharField(max_length=100, verbose_name="Nombre de la meta")
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Monto objetivo"
    )
    current_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Monto actual"
    )
    target_date = models.DateField(verbose_name="Fecha objetivo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    icon = models.CharField(max_length=50, default='fas fa-piggy-bank', verbose_name="Icono")
    color = models.CharField(max_length=7, default='#28a745', verbose_name="Color")
    is_achieved = models.BooleanField(default=False, verbose_name="Meta alcanzada")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Meta de Ahorro"
        verbose_name_plural = "Metas de Ahorro"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.current_amount}/{self.target_amount}"
    
    @property
    def percentage_completed(self):
        """Calcula el porcentaje completado de la meta."""
        if self.target_amount == 0:
            return 0
        return min(100, (self.current_amount / self.target_amount) * 100)
    
    @property
    def percentage_completed_css(self):
        """Valor formateado para usar en CSS/atributos (usar punto decimal, no localizado)."""
        if self.target_amount == 0:
            return "0%"
        val = min(100, (self.current_amount / self.target_amount) * 100)
        try:
            # Devolver con punto decimal y sufijo % para usar directamente en CSS
            return format(float(val), '.1f') + '%'
        except Exception:
            return str(val) + '%'

    @property
    def remaining_amount(self):
        """Calcula el monto restante para alcanzar la meta."""
        return max(0, self.target_amount - self.current_amount)
    
    @property
    def days_remaining(self):
        """Calcula los días restantes hasta la fecha objetivo."""
        delta = self.target_date - timezone.now().date()
        return max(0, delta.days)
    
    @property
    def daily_saving_needed(self):
        """Calcula el ahorro diario necesario para alcanzar la meta."""
        days = self.days_remaining
        if days == 0:
            return self.remaining_amount
        return self.remaining_amount / days if days > 0 else 0


class RecurringTransaction(models.Model):
    """
    Modelo para transacciones recurrentes.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('biweekly', 'Quincenal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", related_name='recurring_transactions')
    name = models.CharField(max_length=100, verbose_name="Nombre")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Monto"
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=Transaction.TRANSACTION_TYPES,
        verbose_name="Tipo de transacción"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoría",
        related_name='recurring_transactions'
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        verbose_name="Frecuencia"
    )
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    description = models.TextField(blank=True, verbose_name="Descripción")
    next_occurrence = models.DateField(verbose_name="Próxima ocurrencia")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Transacción Recurrente"
        verbose_name_plural = "Transacciones Recurrentes"
        ordering = ['next_occurrence']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"
    
    def calculate_next_occurrence(self):
        """Calcula la próxima fecha de ocurrencia."""
        if self.next_occurrence < timezone.now().date():
            base_date = timezone.now().date()
        else:
            base_date = self.next_occurrence
        
        if self.frequency == 'daily':
            return base_date + timedelta(days=1)
        elif self.frequency == 'weekly':
            return base_date + timedelta(weeks=1)
        elif self.frequency == 'biweekly':
            return base_date + timedelta(weeks=2)
        elif self.frequency == 'monthly':
            # Agregar un mes
            if base_date.month == 12:
                return base_date.replace(year=base_date.year + 1, month=1)
            else:
                return base_date.replace(month=base_date.month + 1)
        elif self.frequency == 'quarterly':
            # Agregar 3 meses
            if base_date.month <= 9:
                return base_date.replace(month=base_date.month + 3)
            else:
                return base_date.replace(year=base_date.year + 1, month=base_date.month - 9)
        elif self.frequency == 'yearly':
            return base_date.replace(year=base_date.year + 1)
        
        return base_date
    
    def create_transaction(self):
        """Crea una instancia de transacción basada en esta recurrencia."""
        transaction = Transaction.objects.create(
            user=self.user,
            amount=self.amount,
            description=self.description or self.name,
            date=self.next_occurrence,
            transaction_type=self.transaction_type,
            category=self.category,
            recurring_transaction=self
        )
        
        # Actualizar la próxima ocurrencia
        self.next_occurrence = self.calculate_next_occurrence()
        
        # Desactivar si se alcanzó la fecha de fin
        if self.end_date and self.next_occurrence > self.end_date:
            self.is_active = False
        
        self.save()
        return transaction
