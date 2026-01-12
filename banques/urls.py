"""
URLs pour la gestion des banques
"""
from django.urls import path
from . import views

app_name = 'banques'

urlpatterns = [
    path('', views.BanqueListView.as_view(), name='liste'),
    path('creer/', views.BanqueCreateView.as_view(), name='creer'),
    path('<int:pk>/', views.BanqueDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.BanqueUpdateView.as_view(), name='modifier'),
    
    path('comptes/', views.CompteBancaireListView.as_view(), name='comptes_liste'),
    path('comptes/creer/', views.CompteBancaireCreateView.as_view(), name='compte_creer'),
    path('comptes/<int:pk>/', views.CompteBancaireDetailView.as_view(), name='compte_detail'),
    path('comptes/<int:pk>/modifier/', views.CompteBancaireUpdateView.as_view(), name='compte_modifier'),
]

