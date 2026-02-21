"""
URLs de test pour les comptes sans middlewares
"""
from django.urls import path
from . import views

app_name = 'accounts_test'

urlpatterns = [
    path('login_simple/', views.LoginSimpleView.as_view(), name='login_simple'),
]
