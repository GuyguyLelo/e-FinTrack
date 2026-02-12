from django.urls import path
from . import views
from . import views_rapports
from . import views_tableau_general
from . import views_etats_feuilles
from . import views_test
from . import views_test_simple
from . import views_test_fixe

app_name = 'tableau_bord_feuilles'

urlpatterns = [
    path('', views.tableau_bord_feuilles, name='tableau_bord_feuilles'),
    path('operations/', views.detail_operations, name='detail_operations'),
    
    # Rapports PDF
    path('rapports/', views_rapports.RapportFeuilleSelectionView.as_view(), name='rapport_selection'),
    path('rapports/recette/pdf/', views_rapports.RapportRecetteFeuillePDFView.as_view(), name='rapport_recette_pdf'),
    path('rapports/depense/pdf/', views_rapports.RapportDepenseFeuillePDFView.as_view(), name='rapport_depense_pdf'),
    
    # Tableau général
    path('tableau-general/', views_tableau_general.TableauGeneralFeuillesView.as_view(), name='tableau_general'),
    path('tableau-general/pdf/', views_tableau_general.TableauGeneralPDFView.as_view(), name='tableau_general_pdf'),
    
    # États feuilles (logique états)
    path('preview-etats/', views_etats_feuilles.EtatsFeuillesPreviewView.as_view(), name='preview_etats'),
    path('generer-etats/', views_etats_feuilles.EtatsFeuillesGenererView.as_view(), name='generer_etats'),
    
    # Nouveaux rapports synthétiques et regroupés
    path('rapports/synthese/pdf/', views_etats_feuilles.RapportSynthesePDFView.as_view(), name='rapport_synthese_pdf'),
    path('rapports/groupe/pdf/', views_etats_feuilles.RapportGroupePDFView.as_view(), name='rapport_groupe_pdf'),
    
    # Tests
    path('test-donnees/', views_test.TestDonneesView.as_view(), name='test_donnees'),
    path('test-simple/', views_test_simple.TestSimpleView.as_view(), name='test_simple'),
    path('test-fixe/', views_test_fixe.TestFixeView.as_view(), name='test_fixe'),
]
