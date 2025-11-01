from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('toggle-language/', views.toggle_language, name='toggle_language'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Rutas de administración
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.UserListView.as_view(), name='user_list'),
    path('admin/users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('admin/users/<int:user_id>/update-role/', views.update_user_role, name='update_user_role'),
    path('admin/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('admin/users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
]
