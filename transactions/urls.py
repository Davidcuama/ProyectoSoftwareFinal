from django.urls import path
from . import views
from .external_views import external_items_view

app_name = 'transactions'

urlpatterns = [
    # Transacciones
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('<int:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    
    # Exportación y API
    path('export/', views.export_transactions, name='export_transactions'),
    path('export/<str:format_type>/', views.export_report, name='export_report'),
    path('api/stats/', views.transaction_stats_api, name='transaction_stats_api'),
    
    # Categorías
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Etiquetas
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/create/', views.TagCreateView.as_view(), name='tag_create'),
    path('tags/<int:pk>/update/', views.TagUpdateView.as_view(), name='tag_update'),
    path('tags/<int:pk>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
    
    # Presupuestos
    path('budgets/', views.BudgetListView.as_view(), name='budget_list'),
    path('budgets/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<int:pk>/update/', views.BudgetUpdateView.as_view(), name='budget_update'),
    path('budgets/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
    
    # Metas de Ahorro
    path('savings-goals/', views.SavingsGoalListView.as_view(), name='savings_goal_list'),
    path('savings-goals/create/', views.SavingsGoalCreateView.as_view(), name='savings_goal_create'),
    path('savings-goals/<int:pk>/update/', views.SavingsGoalUpdateView.as_view(), name='savings_goal_update'),
    path('savings-goals/<int:pk>/delete/', views.SavingsGoalDeleteView.as_view(), name='savings_goal_delete'),
    path('savings-goals/<int:goal_id>/add/', views.add_to_savings_goal, name='add_to_savings_goal'),
    
    # Transacciones Recurrentes
    path('recurring/', views.RecurringTransactionListView.as_view(), name='recurring_transaction_list'),
    path('recurring/create/', views.RecurringTransactionCreateView.as_view(), name='recurring_transaction_create'),
    path('recurring/<int:pk>/update/', views.RecurringTransactionUpdateView.as_view(), name='recurring_transaction_update'),
    path('recurring/<int:pk>/delete/', views.RecurringTransactionDeleteView.as_view(), name='recurring_transaction_delete'),
    path('recurring/<int:recurring_id>/process/', views.process_recurring_transactions, name='process_recurring_transaction'),
    path('recurring/<int:recurring_id>/toggle/', views.toggle_recurring_transaction, name='toggle_recurring_transaction'),
    
    # Servicios externos (consumo de otros equipos)
    path('external-items/', external_items_view, name='external_items'),
]
