from django import forms
from django.utils import timezone
from django.db import models
from datetime import datetime
from .models import Transaction, Category, Tag, Budget, SavingsGoal, RecurringTransaction


class TransactionForm(forms.ModelForm):
    """
    Formulario para crear y editar transacciones.
    """
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'date', 'transaction_type', 'category', 'tags']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la transacción...'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'multiple': 'multiple'
            })
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer fecha por defecto
        if not self.instance.pk:
            self.fields['date'].initial = timezone.now().date()
        
        # Filtrar categorías y tags por usuario
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['tags'].queryset = Tag.objects.filter(user=user)
            
            # Si es una edición, actualizar los querysets
            if self.instance.pk:
                transaction_type = self.instance.transaction_type
                self.fields['category'].queryset = Category.objects.filter(
                    user=user
                ).filter(
                    models.Q(transaction_type=transaction_type) | models.Q(transaction_type='both')
                )
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('El monto debe ser mayor a 0.')
        return amount
    
    def clean_date(self):
        date_value = self.cleaned_data.get('date')
        if date_value > timezone.now().date():
            raise forms.ValidationError('La fecha no puede ser futura.')
        return date_value


class CategoryForm(forms.ModelForm):
    """Formulario para crear y editar categorías."""
    
    # Iconos comunes para categorías
    ICON_CHOICES = [
        ('fas fa-tag', 'Etiqueta'),
        ('fas fa-home', 'Casa'),
        ('fas fa-utensils', 'Comida'),
        ('fas fa-car', 'Carro'),
        ('fas fa-gas-pump', 'Gasolina'),
        ('fas fa-bus', 'Transporte'),
        ('fas fa-plane', 'Viajes'),
        ('fas fa-shopping-cart', 'Compras'),
        ('fas fa-shopping-bag', 'Bolsas'),
        ('fas fa-tshirt', 'Ropa'),
        ('fas fa-mobile-alt', 'Tecnología'),
        ('fas fa-laptop', 'Laptop'),
        ('fas fa-gamepad', 'Entretenimiento'),
        ('fas fa-music', 'Música'),
        ('fas fa-film', 'Cine'),
        ('fas fa-dumbbell', 'Gimnasio'),
        ('fas fa-heartbeat', 'Salud'),
        ('fas fa-pills', 'Medicina'),
        ('fas fa-book', 'Educación'),
        ('fas fa-graduation-cap', 'Estudios'),
        ('fas fa-briefcase', 'Trabajo'),
        ('fas fa-dollar-sign', 'Dinero'),
        ('fas fa-wallet', 'Billetera'),
        ('fas fa-credit-card', 'Tarjeta'),
        ('fas fa-gift', 'Regalos'),
        ('fas fa-birthday-cake', 'Cumpleaños'),
        ('fas fa-coffee', 'Café'),
        ('fas fa-beer', 'Bebidas'),
        ('fas fa-wifi', 'Internet'),
        ('fas fa-lightbulb', 'Servicios'),
        ('fas fa-tv', 'TV'),
        ('fas fa-phone', 'Teléfono'),
        ('fas fa-umbrella', 'Seguro'),
        ('fas fa-building', 'Negocio'),
        ('fas fa-chart-line', 'Inversiones'),
        ('fas fa-hand-holding-usd', 'Ingresos'),
    ]
    
    icon = forms.ChoiceField(
        choices=ICON_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_icon_select'
        }),
        initial='fas fa-tag'
    )
    
    class Meta:
        model = Category
        fields = ['name', 'transaction_type', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando y el icono no está en las opciones, agregarlo
        if self.instance and self.instance.pk and self.instance.icon:
            current_icon = self.instance.icon
            # Verificar si el icono actual está en las opciones
            icon_values = [choice[0] for choice in self.ICON_CHOICES]
            if current_icon not in icon_values:
                # Agregar el icono actual al inicio de las opciones
                self.fields['icon'].choices = [(current_icon, f'Icono actual ({current_icon})')] + self.ICON_CHOICES


class TagForm(forms.ModelForm):
    """Formulario para crear y editar etiquetas."""
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la etiqueta'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }


class BudgetForm(forms.ModelForm):
    """Formulario para crear y editar presupuestos."""
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'month': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'month'
            })
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar formato de entrada para aceptar YYYY-MM
        self.fields['month'].input_formats = ['%Y-%m', '%Y-%m-%d']
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user,
                transaction_type__in=['expense', 'both']
            )
    
    def clean_month(self):
        """Convierte el formato YYYY-MM a una fecha completa (primer día del mes)."""
        month_value = self.cleaned_data.get('month')
        
        # Si month_value es None, dejar que Django maneje la validación
        if month_value is None:
            return month_value
        
        # Si ya es una fecha completa, retornarla
        if isinstance(month_value, datetime):
            return month_value.date()
        
        # Si es un string, intentar parsearlo
        if isinstance(month_value, str):
            # Intentar formato YYYY-MM
            try:
                parsed_date = datetime.strptime(month_value, '%Y-%m')
                # Retornar el primer día del mes
                return parsed_date.replace(day=1).date()
            except ValueError:
                # Si falla, intentar formato YYYY-MM-DD
                try:
                    return datetime.strptime(month_value, '%Y-%m-%d').date()
                except ValueError:
                    raise forms.ValidationError('Introduzca una fecha válida.')
        
        return month_value


class SavingsGoalForm(forms.ModelForm):
    """Formulario para crear y editar metas de ahorro."""
    
    # Iconos comunes para metas de ahorro
    ICON_CHOICES = [
        ('fas fa-piggy-bank', 'Alcancía'),
        ('fas fa-coins', 'Monedas'),
        ('fas fa-wallet', 'Billetera'),
        ('fas fa-dollar-sign', 'Dólar'),
        ('fas fa-money-bill-wave', 'Billete'),
        ('fas fa-gift', 'Regalo'),
        ('fas fa-home', 'Casa'),
        ('fas fa-car', 'Carro'),
        ('fas fa-plane', 'Avión'),
        ('fas fa-heart', 'Corazón'),
        ('fas fa-star', 'Estrella'),
        ('fas fa-trophy', 'Trofeo'),
        ('fas fa-graduation-cap', 'Graduación'),
        ('fas fa-briefcase', 'Maletín'),
        ('fas fa-laptop', 'Laptop'),
        ('fas fa-mobile-alt', 'Celular'),
        ('fas fa-camera', 'Cámara'),
        ('fas fa-gamepad', 'Videojuego'),
        ('fas fa-bicycle', 'Bicicleta'),
        ('fas fa-motorcycle', 'Motocicleta'),
        ('fas fa-ship', 'Barco'),
        ('fas fa-music', 'Música'),
        ('fas fa-book', 'Libro'),
        ('fas fa-dumbbell', 'Gimnasio'),
        ('fas fa-utensils', 'Comida'),
        ('fas fa-shopping-bag', 'Compras'),
        ('fas fa-gem', 'Gema'),
        ('fas fa-ring', 'Anillo'),
        ('fas fa-watch', 'Reloj'),
        ('fas fa-sun', 'Sol'),
    ]
    
    icon = forms.ChoiceField(
        choices=ICON_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_icon_select'
        }),
        initial='fas fa-piggy-bank'
    )
    
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'target_date', 'description', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la meta'
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'target_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la meta...'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando y el icono no está en las opciones, agregarlo
        if self.instance and self.instance.pk and self.instance.icon:
            current_icon = self.instance.icon
            # Verificar si el icono actual está en las opciones
            icon_values = [choice[0] for choice in self.ICON_CHOICES]
            if current_icon not in icon_values:
                # Agregar el icono actual al inicio de las opciones
                self.fields['icon'].choices = [(current_icon, f'Icono actual ({current_icon})')] + self.ICON_CHOICES


class RecurringTransactionForm(forms.ModelForm):
    """Formulario para crear y editar transacciones recurrentes."""
    class Meta:
        model = RecurringTransaction
        fields = ['name', 'amount', 'transaction_type', 'category', 'frequency', 'start_date', 'end_date', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la transacción recurrente'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción...'
            })
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        
        # Establecer fecha de inicio por defecto
        if not self.instance.pk:
            self.fields['start_date'].initial = timezone.now().date()


class TransactionFilterForm(forms.Form):
    """
    Formulario para filtrar transacciones.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('', 'Todos los tipos'),
        ('income', 'Ingresos'),
        ('expense', 'Gastos'),
    ]
    
    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en descripción...'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        
        return cleaned_data
