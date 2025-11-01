from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    TransactionViewSet, CategoryViewSet,
    BudgetViewSet, SavingsGoalViewSet
)

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'savings-goals', SavingsGoalViewSet, basename='savings-goal')

urlpatterns = [
    path('', include(router.urls)),
]

