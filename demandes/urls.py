"""
URLs pour la gestion des demandes de paiement
"""
from django.urls import path
from . import views

app_name = 'demandes'

urlpatterns = [
    path('', views.DemandePaiementListView.as_view(), name='liste'),
    path('creer/', views.DemandePaiementCreateView.as_view(), name='creer'),
    path('<int:pk>/', views.DemandePaiementDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.DemandePaiementUpdateView.as_view(), name='modifier'),
    path('<int:pk>/valider/', views.DemandePaiementValidationView.as_view(), name='valider'),
    path('releves/', views.ReleveDepenseListView.as_view(), name='releves_liste'),
    path('releves/pdf/', views.ReleveDepensePDFView.as_view(), name='releve_pdf'),
    path('releves/excel/', views.ReleveDepenseExcelView.as_view(), name='releve_excel'),
    path('releves/reimprimer/pdf/', views.ReleveDepenseReprintPDFView.as_view(), name='releve_reprint_pdf'),
    path('releves/crees/', views.ReleveDepenseListCreatedView.as_view(), name='releves_crees_liste'),
    path('releves/<int:pk>/', views.ReleveDepenseDetailView.as_view(), name='releve_detail'),
    path('releves/<int:pk>/pdf/', views.ReleveDepenseGenererPDFView.as_view(), name='releve_generer_pdf'),
    path('releves/<int:pk>/ajouter-demandes/', views.ReleveDepenseAjouterDemandesView.as_view(), name='releve_ajouter_demandes'),
    path('releves/<int:pk>/valider-depenses/', views.ReleveDepenseValiderDepensesView.as_view(), name='releve_valider_depenses'),
    path('cheques/pdf/', views.ChequePDFView.as_view(), name='cheque_pdf'),
    path('releves/creer/', views.ReleveDepenseCreateView.as_view(), name='releve_creer'),
    path('releves/generer/', views.ReleveDepenseAutoCreateView.as_view(), name='releve_generer'),
    path('depenses/', views.DepenseListView.as_view(), name='depenses_liste'),
    path('depenses/creer/', views.DepenseCreateView.as_view(), name='depense_creer'),
    path('depenses/<int:pk>/', views.DepenseDetailView.as_view(), name='depense_detail'),
    path('depenses/<int:pk>/modifier/', views.DepenseUpdateView.as_view(), name='depense_modifier'),
    path('nomenclatures/', views.get_nomenclatures_by_year, name='nomenclatures_by_year'),
    path('natures/', views.NatureEconomiqueListView.as_view(), name='nature_liste'),
    path('natures/creer/', views.NatureEconomiqueCreateView.as_view(), name='nature_creer'),
    path('natures/<int:pk>/', views.NatureEconomiqueDetailView.as_view(), name='nature_detail'),
    path('natures/<int:pk>/modifier/', views.NatureEconomiqueUpdateView.as_view(), name='nature_modifier'),
    
    # URLs pour les paiements
    path('paiements/', views.PaiementListView.as_view(), name='paiement_liste'),
    path('paiements/creer/', views.PaiementCreateView.as_view(), name='paiement_create'),
    path('paiements/<int:pk>/', views.PaiementDetailView.as_view(), name='paiement_detail'),
    path('paiements/releve/', views.PaiementParReleveView.as_view(), name='paiement_par_releve'),
    path('paiements/releve/<int:pk>/', views.PaiementReleveDetailView.as_view(), name='paiement_releve_detail'),
    
    # URLs API
    path('api/demande/<int:pk>/reste-a-payer/', views.DemandeResteAPayerView.as_view(), name='demande_reste_a_payer_api'),
]
