"""
URLs pour la gestion des recettes
"""
from django.urls import path
from . import views

app_name = 'recettes'

urlpatterns = [
    path('', views.RecetteListView.as_view(), name='liste'),
    path('creer/', views.RecetteCreateView.as_view(), name='creer'),
    path('<int:pk>/', views.RecetteDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.RecetteUpdateView.as_view(), name='modifier'),
    path('<int:pk>/valider/', views.RecetteValidationView.as_view(), name='valider'),
    path('charger-comptes/', views.load_comptes, name='load_comptes'),
]

