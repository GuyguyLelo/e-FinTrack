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
    # Feuille RECETTES (structure Excel)
    path('feuille/', views.RecetteFeuilleListView.as_view(), name='feuille_liste'),
    path('feuille/creer/', views.RecetteFeuilleCreateView.as_view(), name='feuille_creer'),
    path('feuille/<int:pk>/', views.RecetteFeuilleDetailView.as_view(), name='feuille_detail'),
    path('feuille/<int:pk>/modifier/', views.RecetteFeuilleUpdateView.as_view(), name='feuille_modifier'),
]

