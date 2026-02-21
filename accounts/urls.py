"""
URLs pour l'authentification
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('login_test/', views.LoginTestView.as_view(), name='login_test'),
    path('login_test_simple/', views.LoginSimpleView.as_view(), name='login_test_simple'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('identifiants/', views.IdentifiantsView.as_view(), name='identifiants'),
]

