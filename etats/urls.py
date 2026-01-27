"""
URLs pour l'application etats
"""
from django.urls import path
from . import views

app_name = 'etats'

urlpatterns = [
    # Liste des états
    path('', views.EtatListView.as_view(), name='liste'),
    
    # Création et génération
    path('selection/', views.EtatCreateView.as_view(), name='selection'),
    path('preview/', views.EtatPreviewView.as_view(), name='preview'),
    path('create/', views.EtatCreateAjaxView.as_view(), name='create_ajax'),
    path('generer/<int:pk>/', views.EtatGenererView.as_view(), name='generer'),
    
    # Détails et téléchargement
    path('detail/<int:pk>/', views.EtatDetailView.as_view(), name='detail'),
    path('telecharger/<int:pk>/<str:format_file>/', views.EtatTelechargerView.as_view(), name='telecharger'),
]
