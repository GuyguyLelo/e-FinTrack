"""
URLs pour l'authentification
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # URLs pour la gestion des services
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/ajouter/', views.ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/modifier/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('services/<int:pk>/supprimer/', views.ServiceDeleteView.as_view(), name='service_delete'),
]

