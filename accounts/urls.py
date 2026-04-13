"""
URLs pour l'authentification
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .dashboard_views import SmartDashboardView

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Dashboard intelligent RBAC
    path('dashboard/', SmartDashboardView.as_view(), name='smart_dashboard'),
    
    # URLs pour la gestion des services
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/ajouter/', views.ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/modifier/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('services/<int:pk>/supprimer/', views.ServiceDeleteView.as_view(), name='service_delete'),
    
    # URLs pour la gestion des utilisateurs
    path('utilisateurs/', views.UserListView.as_view(), name='user_list'),
    path('utilisateurs/ajouter/', views.UserCreateView.as_view(), name='user_create'),
    path('utilisateurs/<int:pk>/modifier/', views.UserUpdateView.as_view(), name='user_update'),
    path('utilisateurs/<int:pk>/details/', views.UserDetailView.as_view(), name='user_detail'),
    path('utilisateurs/<int:pk>/supprimer/', views.UserDeleteView.as_view(), name='user_delete'),
]

