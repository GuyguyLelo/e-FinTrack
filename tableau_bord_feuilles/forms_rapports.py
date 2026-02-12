from django import forms
from demandes.models import NatureEconomique
from accounts.models import Service
from banques.models import Banque


class RapportFeuilleSelectionForm(forms.Form):
    """Formulaire pour la sélection des rapports feuilles"""
    
    # Type d'état
    type_etat = forms.ChoiceField(
        choices=[
            ('', '-- Sélectionner --'),
            ('DEPENSE_FEUILLE', 'État des Dépenses'),
            ('RECETTE_FEUILLE', 'État des Recettes'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Type d'État"
    )
    
    # Type de rapport
    type_rapport = forms.ChoiceField(
        choices=[
            ('DETAILLE', 'Rapport Détaillé'),
            ('GROUPE', 'Rapport Regroupé'),
            ('SYNTHESE', 'Rapport Synthétique'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Type de Rapport",
        initial='DETAILLE'
    )
    
    # Critère de regroupement
    critere_groupement = forms.ChoiceField(
        choices=[
            ('nature', 'Par Nature Économique'),
            ('service', 'Par Service Bénéficiaire'),
            ('banque', 'Par Banque'),
            ('mois', 'Par Mois'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Regrouper par",
        required=False
    )
    
    # Filtres temporels
    annee = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Année",
        required=False
    )
    
    mois = forms.ChoiceField(
        choices=[
            ('', 'Toutes'),
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Mois",
        required=False
    )
    
    # Champs séparés pour dépenses
    annee_depenses = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Année",
        required=False
    )
    
    mois_depenses = forms.ChoiceField(
        choices=[
            ('', 'Toutes'),
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Mois",
        required=False
    )
    
    # Champs séparés pour recettes
    annee_recettes = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Année",
        required=False
    )
    
    mois_recettes = forms.ChoiceField(
        choices=[
            ('', 'Toutes'),
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Mois",
        required=False
    )
    
    # Filtres dépenses
    natures_depenses = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Natures Économiques",
        required=False
    )
    
    services_depenses = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Services Bénéficiaires",
        required=False
    )
    
    banques_depenses = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Banques",
        required=False
    )
    
    montant_min_depenses = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant CDF Min",
        required=False
    )
    
    montant_max_depenses = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant CDF Max",
        required=False
    )
    
    observation_depenses = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mot-clé...'}),
        label="Recherche Observation",
        required=False
    )
    
    # Filtres recettes
    banques_recettes = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Banques",
        required=False
    )
    
    libelle_recettes = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mot-clé...'}),
        label="Recherche Libellé",
        required=False
    )
    
    montant_min_recettes = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant CDF Min",
        required=False
    )
    
    montant_max_recettes = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant CDF Max",
        required=False
    )
    
    montant_usd_min_recettes = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant USD Min",
        required=False
    )
    
    montant_usd_max_recettes = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        label="Montant USD Max",
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        annees_disponibles = kwargs.pop('annees_disponibles', [])
        super().__init__(*args, **kwargs)
        
        # Préparer les choix d'années
        annee_choices = [('', 'Toutes')] + [(str(annee), str(annee)) for annee in annees_disponibles]
        
        # Mettre à jour les choix d'années pour tous les champs
        self.fields['annee'].choices = annee_choices
        self.fields['annee_depenses'].choices = annee_choices
        self.fields['annee_recettes'].choices = annee_choices
        
        # Préparer les choices pour les champs de modèles avec option "Toutes"
        nature_choices = [('', 'Toutes')] + [(str(n.pk), f"{n.titre} ({n.code})") for n in NatureEconomique.objects.all()]
        service_choices = [('', 'Toutes')] + [(str(s.pk), s.nom_service) for s in Service.objects.all()]
        banque_choices = [('', 'Toutes')] + [(str(b.pk), b.nom_banque) for b in Banque.objects.all()]
        
        # Mettre à jour les choices pour les champs dépenses
        self.fields['natures_depenses'].choices = nature_choices
        self.fields['services_depenses'].choices = service_choices
        self.fields['banques_depenses'].choices = banque_choices
        
        # Mettre à jour les choices pour les champs recettes
        self.fields['banques_recettes'].choices = banque_choices
