"""
URLs pour le rapprochement bancaire
"""
from django.urls import path
from . import views

app_name = 'rapprochements'

urlpatterns = [
    path('', views.RapprochementBancaireListView.as_view(), name='liste'),
    path('creer/', views.RapprochementBancaireCreateView.as_view(), name='creer'),
    path('<int:pk>/', views.RapprochementBancaireDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.RapprochementBancaireUpdateView.as_view(), name='modifier'),
    path('<int:pk>/calculer/', views.RapprochementBancaireCalculerView.as_view(), name='calculer'),
    path('<int:pk>/valider/', views.RapprochementBancaireValidationView.as_view(), name='valider'),
    path('charger-comptes/', views.load_comptes, name='load_comptes'),
]

