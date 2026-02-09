from django.urls import path
from . import views
from . import views_rapports

app_name = 'tableau_bord_feuilles'

urlpatterns = [
    path('', views.tableau_bord_feuilles, name='tableau_bord_feuilles'),
    path('operations/', views.detail_operations, name='detail_operations'),
    
    # Rapports PDF
    path('rapports/', views_rapports.RapportFeuilleSelectionView.as_view(), name='rapport_selection'),
    path('rapports/recette/pdf/', views_rapports.RapportRecetteFeuillePDFView.as_view(), name='rapport_recette_pdf'),
    path('rapports/depense/pdf/', views_rapports.RapportDepenseFeuillePDFView.as_view(), name='rapport_depense_pdf'),
]
