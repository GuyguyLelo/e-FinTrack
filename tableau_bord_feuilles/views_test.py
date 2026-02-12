from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from demandes.models import DepenseFeuille
from recettes.models import RecetteFeuille

class TestDonneesView(LoginRequiredMixin, View):
    """Vue pour tester les données existantes"""
    
    def get(self, request, *args, **kwargs):
        # Vérifier les données dans les deux tables
        total_depenses = DepenseFeuille.objects.count()
        total_recettes = RecetteFeuille.objects.count()
        
        # Prendre quelques exemples
        exemples_depenses = DepenseFeuille.objects.all()[:5]
        exemples_recettes = RecetteFeuille.objects.all()[:5]
        
        context = {
            'total_depenses': total_depenses,
            'total_recettes': total_recettes,
            'exemples_depenses': exemples_depenses,
            'exemples_recettes': exemples_recettes,
        }
        
        return render(request, 'tableau_bord_feuilles/test_donnees.html', context)
