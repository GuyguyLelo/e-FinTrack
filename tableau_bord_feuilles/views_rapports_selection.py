from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.urls import reverse
from django.contrib import messages
from demandes.models import DepenseFeuille
from recettes.models import RecetteFeuille
from django.db.models import Sum, Count
from datetime import datetime

class RapportFeuilleSelectionView(LoginRequiredMixin, View):
    """Page d'intermédiaire pour sélectionner le type de rapport avec formulaire simplifié"""
    
    def get(self, request, *args, **kwargs):
        # Récupérer les paramètres du formulaire
        mois = request.GET.get('mois', '')
        annee = request.GET.get('annee', '')
        type_rapport = request.GET.get('type', '')
        selection_step = request.GET.get('selection_step', '')
        
        # Étape 1 : Sélection du type de rapport
        if not type_rapport:
            return render(request, 'tableau_bord_feuilles/rapport_feuille_selection.html', {
                'title': 'Sélection du type de rapport',
                'mois_choices': [(i, f"{i:02d} - {['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i]}") for i in range(1, 13)],
                'annees_disponibles': self._get_annees_disponibles(),
                'mois': mois,
                'annee': annee
            })
        
        # Étape 2 : Sélection de la période (mois et année)
        if type_rapport and not selection_step:
            return render(request, 'tableau_bord_feuilles/rapport_periode_selection.html', {
                'title': f'Sélection de la période - {type_rapport}',
                'type_rapport': type_rapport,
                'mois_choices': [(i, f"{i:02d} - {['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i]}") for i in range(1, 13)],
                'annees_disponibles': self._get_annees_disponibles(),
                'mois': mois,
                'annee': annee
            })
        
        # Étape 3 : Redirection vers la page de rapports avec les paramètres
        if type_rapport and selection_step == 'confirmer':
            if not mois or not annee:
                messages.error(request, "Veuillez sélectionner un mois et une année.")
                return redirect(f"{reverse('tableau_bord_feuilles:rapport_feuille_selection')}?type={type_rapport}&mois={mois}&annee={annee}")
            
            # Redirection vers la page de rapports avec les paramètres
            return redirect(f"{reverse('tableau_bord_feuilles:rapport_selection')}?type_etat={type_rapport}&mois={mois}&annee={annee}")
    
    def _get_annees_disponibles(self):
        """Récupérer les années disponibles"""
        annees_depenses = list(DepenseFeuille.objects.values_list('annee').distinct())
        annees_recettes = list(RecetteFeuille.objects.values_list('annee').distinct())
        return sorted(set(annees_depenses + annees_recettes), reverse=True)


class RapportRecettesView(LoginRequiredMixin, View):
    """Page pour générer un rapport de recettes avec paramètres mois et année par défaut"""
    
    def get(self, request, *args, **kwargs):
        # Valeurs par défaut
        current_date = datetime.now()
        default_mois = current_date.month
        default_annee = current_date.year
        
        # Récupérer les paramètres de l'URL ou utiliser les valeurs par défaut
        mois = request.GET.get('mois', str(default_mois))
        annee = request.GET.get('annee', str(default_annee))
        
        return render(request, 'tableau_bord_feuilles/rapport_recettes.html', {
            'title': 'Impression recettes',
            'type_rapport': 'RECETTE_FEUILLE',
            'mois': mois,
            'annee': annee,
            'mois_choices': [(i, f"{i:02d} - {['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i]}") for i in range(1, 13)],
            'annees_disponibles': self._get_annees_disponibles()
        })
    
    def _get_annees_disponibles(self):
        """Récupérer les années disponibles pour les recettes"""
        annees = list(RecetteFeuille.objects.values_list('annee', flat=True).distinct())
        current_year = datetime.now().year
        if current_year not in annees:
            annees.append(current_year)
        return sorted(annees, reverse=True)


class RapportDepensesView(LoginRequiredMixin, View):
    """Page pour générer un rapport de dépenses avec paramètres mois et année par défaut"""
    
    def get(self, request, *args, **kwargs):
        # Valeurs par défaut
        current_date = datetime.now()
        default_mois = current_date.month
        default_annee = current_date.year
        
        # Récupérer les paramètres de l'URL ou utiliser les valeurs par défaut
        mois = request.GET.get('mois', str(default_mois))
        annee = request.GET.get('annee', str(default_annee))
        
        return render(request, 'tableau_bord_feuilles/rapport_depenses.html', {
            'title': 'Impression dépenses',
            'type_rapport': 'DEPENSE_FEUILLE',
            'mois': mois,
            'annee': annee,
            'mois_choices': [(i, f"{i:02d} - {['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i]}") for i in range(1, 13)],
            'annees_disponibles': self._get_annees_disponibles()
        })
    
    def _get_annees_disponibles(self):
        """Récupérer les années disponibles pour les dépenses"""
        annees = list(DepenseFeuille.objects.values_list('annee', flat=True).distinct())
        current_year = datetime.now().year
        if current_year not in annees:
            annees.append(current_year)
        return sorted(annees, reverse=True)


class EtatsDepensesView(LoginRequiredMixin, View):
    """Page pour générer les états de dépenses avec boutons dynamiques"""
    
    def get(self, request, *args, **kwargs):
        return render(request, 'tableau_bord_feuilles/etats_depenses.html', {
            'title': 'États des dépenses',
            'mois_choices': [(i, f"{i:02d} - {['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i]}") for i in range(1, 13)],
            'annees_disponibles': self._get_annees_disponibles_depenses()
        })
    
    def _get_annees_disponibles_depenses(self):
        """Récupérer les années disponibles pour les dépenses"""
        annees = list(DepenseFeuille.objects.values_list('annee', flat=True).distinct())
        current_year = datetime.now().year
        if current_year not in annees:
            annees.append(current_year)
        return sorted(annees, reverse=True)


class EtatsRecettesView(LoginRequiredMixin, View):
    """Page pour générer les états de recettes avec boutons dynamiques"""
    
    def get(self, request, *args, **kwargs):
        return render(request, 'tableau_bord_feuilles/etats_recettes.html', {
            'title': 'États des recettes',
            'mois_choices': [(i, f"{i:02d} - {['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i]}") for i in range(1, 13)],
            'annees_disponibles': self._get_annees_disponibles_recettes()
        })
    
    def _get_annees_disponibles_recettes(self):
        """Récupérer les années disponibles pour les recettes"""
        annees = list(RecetteFeuille.objects.values_list('annee', flat=True).distinct())
        current_year = datetime.now().year
        if current_year not in annees:
            annees.append(current_year)
        return sorted(annees, reverse=True)
