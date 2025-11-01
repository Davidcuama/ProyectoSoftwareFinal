from django import forms
from django.utils import timezone
from django.db import models
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
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-tag'
            })
        }


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
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                user=user,
                transaction_type__in=['expense', 'both']
            )


class SavingsGoalForm(forms.ModelForm):
    """Formulario para crear y editar metas de ahorro."""
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
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-piggy-bank'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }


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
