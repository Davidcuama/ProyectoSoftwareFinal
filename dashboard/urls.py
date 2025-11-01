from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
]
