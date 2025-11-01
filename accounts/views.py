from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction, models
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.translation import activate
from django.conf import settings

from .models import UserProfile
from .decorators import admin_required


def toggle_language(request):
    """
    Vista simple para cambiar el idioma.
    """
    # Obtener el idioma actual de la sesión
    current_lang = request.session.get('django_language', 'es')
    
    # Alternar entre español e inglés
    if current_lang == 'es' or current_lang == 'es-ES' or current_lang[:2] == 'es':
        new_lang = 'en'
    else:
        new_lang = 'es'
    
    # Guardar en la sesión
    request.session['django_language'] = new_lang
    
    # Activar el idioma
    activate(new_lang)
    
    # Redirigir a la misma página o a la página que viene en 'next'
    next_url = request.GET.get('next', request.POST.get('next', '/'))
    return redirect(next_url)


def register(request):
    """
    Vista para registro de nuevos usuarios.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Autenticar al usuario
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, '¡Cuenta creada exitosamente! Bienvenido a tu gestor de finanzas.')
            return redirect('dashboard:dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """
    Vista para mostrar y editar el perfil del usuario.
    """
    if request.method == 'POST':
        # Aquí se podría agregar lógica para actualizar el perfil
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('accounts:profile')
    
    # Estadísticas del usuario
    from transactions.models import Transaction
    from django.db.models import Sum, Count
    
    user = request.user
    
    # Estadísticas generales
    total_transactions = Transaction.objects.filter(user=user).count()
    
    # Última actividad
    last_transaction = Transaction.objects.filter(user=user).order_by('-created_at').first()
    
    context = {
        'total_transactions': total_transactions,
        'last_transaction': last_transaction,
        'member_since': user.date_joined,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password(request):
    """
    Vista para cambiar la contraseña del usuario.
    """
    if request.method == 'POST':
        from django.contrib.auth.forms import PasswordChangeForm
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Actualizar la sesión para evitar que el usuario sea desconectado
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('accounts:profile')
    else:
        from django.contrib.auth.forms import PasswordChangeForm
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


# ===== VISTAS DE ADMINISTRACIÓN =====

@admin_required
def admin_dashboard(request):
    """
    Dashboard principal para administradores.
    """
    # Estadísticas generales
    total_users = User.objects.count()
    total_admins = UserProfile.objects.filter(role='admin').count()
    total_regular_users = UserProfile.objects.filter(role='user').count()
    
    # Usuarios recientes
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Estadísticas de transacciones
    from transactions.models import Transaction
    total_transactions = Transaction.objects.count()
    total_income = Transaction.objects.filter(transaction_type='income').aggregate(
        total=Sum('amount')
    )['total'] or 0
    total_expenses = Transaction.objects.filter(transaction_type='expense').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'total_users': total_users,
        'total_admins': total_admins,
        'total_regular_users': total_regular_users,
        'recent_users': recent_users,
        'total_transactions': total_transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


class UserListView(LoginRequiredMixin, ListView):
    """
    Vista para listar todos los usuarios (solo administradores).
    """
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('accounts:login')
        
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('dashboard:dashboard')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = User.objects.all().select_related('profile')
        
        # Filtros
        search = self.request.GET.get('search')
        role = self.request.GET.get('role')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        if role:
            queryset = queryset.filter(profile__role=role)
        
        return queryset.order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_choices'] = UserProfile.ROLE_CHOICES
        return context


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Vista para editar usuarios (solo administradores).
    """
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'profile') and 
                self.request.user.profile.is_admin)
    
    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.object.profile
        context['role_choices'] = UserProfile.ROLE_CHOICES
        return context


@admin_required
def update_user_role(request, user_id):
    """
    Vista para actualizar el rol de un usuario.
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['user', 'admin']:
            user.profile.role = new_role
            user.profile.save()
            messages.success(request, f'Rol de {user.username} actualizado a {user.profile.get_role_display()}.')
        else:
            messages.error(request, 'Rol inválido.')
    
    return redirect('accounts:user_update', pk=user_id)


@admin_required
def toggle_user_status(request, user_id):
    """
    Vista para activar/desactivar usuarios.
    """
    user = get_object_or_404(User, id=user_id)
    
    # No permitir desactivar al propio usuario
    if user == request.user:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
        return redirect('accounts:user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'activado' if user.is_active else 'desactivado'
    messages.success(request, f'Usuario {user.username} {status} exitosamente.')
    
    return redirect('accounts:user_list')


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Vista para eliminar usuarios (solo administradores).
    """
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'profile') and 
                self.request.user.profile.is_admin)
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        
        # No permitir eliminar al propio usuario
        if user == request.user:
            messages.error(request, 'No puedes eliminar tu propia cuenta.')
            return redirect('accounts:user_list')
        
        messages.success(request, f'Usuario {user.username} eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)
