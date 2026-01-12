"""
URLs pour la gestion des relevés bancaires
"""
from django.urls import path
from . import views

app_name = 'releves'

urlpatterns = [
    path('', views.ReleveBancaireListView.as_view(), name='liste'),
    path('creer/', views.ReleveBancaireCreateView.as_view(), name='creer'),
    path('<int:pk>/', views.ReleveBancaireDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.ReleveBancaireUpdateView.as_view(), name='modifier'),
    path('<int:pk>/valider/', views.ReleveBancaireValidationView.as_view(), name='valider'),
    path('<int:pk>/mouvement/ajouter/', views.MouvementBancaireCreateView.as_view(), name='mouvement_ajouter'),
    path('mouvement/<int:pk>/supprimer/', views.MouvementBancaireDeleteView.as_view(), name='mouvement_supprimer'),
    path('charger-comptes/', views.load_comptes, name='load_comptes'),
]

