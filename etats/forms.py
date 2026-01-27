"""
Formulaires pour la gestion des états
"""
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import EtatGenerique, ConfigurationEtat
from accounts.models import Service
from demandes.models import NatureEconomique
from banques.models import Banque, CompteBancaire


class EtatSelectionForm(forms.Form):
    """Formulaire pour la sélection et configuration d'un état"""
    
    type_etat = forms.ChoiceField(
        choices=EtatGenerique.TYPE_ETAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'type_etat_select'}),
        label="Type d'état"
    )
    
    titre = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Titre de l'état"
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Description"
    )
    
    # Période
    periodicite = forms.ChoiceField(
        choices=EtatGenerique.PERIODICITE_CHOICES,
        initial='PERSONNALISE',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'periodicite_select'}),
        label="Périodicité"
    )
    
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date de début"
    )
    
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date de fin"
    )
    
    # Filtres
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '4'}),
        label="Services"
    )
    
    natures_economiques = forms.ModelMultipleChoiceField(
        queryset=NatureEconomique.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '4'}),
        label="Natures économiques"
    )
    
    banques = forms.ModelMultipleChoiceField(
        queryset=Banque.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '4'}),
        label="Banques"
    )
    
    comptes_bancaires = forms.ModelMultipleChoiceField(
        queryset=CompteBancaire.objects.filter(actif=True),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '4'}),
        label="Comptes bancaires"
    )
    
    # Options de génération
    format_sortie = forms.ChoiceField(
        choices=[
            ('PDF', 'PDF uniquement'),
            ('EXCEL', 'Excel uniquement'),
            ('LES_DEUX', 'PDF et Excel'),
        ],
        initial='PDF',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Format de sortie"
    )
    
    inclure_details = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Inclure les détails complets"
    )
    
    inclure_graphiques = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Inclure les graphiques (si disponible)"
    )
    
    tri_par = forms.ChoiceField(
        choices=[
            ('date', 'Date'),
            ('montant', 'Montant'),
            ('reference', 'Référence'),
            ('service', 'Service'),
        ],
        initial='date',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Trier par"
    )
    
    ordre_tri = forms.ChoiceField(
        choices=[
            ('asc', 'Ascendant'),
            ('desc', 'Descendant'),
        ],
        initial='desc',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Ordre de tri"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Valeurs par défaut pour la période
        if not self.data.get('date_debut') and not self.data.get('date_fin'):
            today = timezone.now().date()
            self.fields['date_debut'].initial = today.replace(1)
            self.fields['date_fin'].initial = today
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin:
            if date_debut > date_fin:
                raise ValidationError("La date de début doit être antérieure à la date de fin.")
            
            # Vérifier que la période n'est pas trop longue (limite à 1 an)
            if (date_fin - date_debut).days > 365:
                raise ValidationError("La période ne peut pas dépasser 1 an.")
        
        return cleaned_data
    
    def appliquer_periodicite(self):
        """Applique automatiquement les dates selon la périodicité sélectionnée"""
        periodicite = self.cleaned_data.get('periodicite')
        today = timezone.now().date()
        
        if periodicite == 'JOURNALIER':
            self.cleaned_data['date_debut'] = today
            self.cleaned_data['date_fin'] = today
        elif periodicite == 'HEBDOMADAIRE':
            # Semaine en cours (lundi au dimanche)
            from datetime import timedelta
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            self.cleaned_data['date_debut'] = start_of_week
            self.cleaned_data['date_fin'] = end_of_week
        elif periodicite == 'MENSUEL':
            # Mois en cours
            self.cleaned_data['date_debut'] = today.replace(1)
            # Dernier jour du mois
            if today.month == 12:
                next_month = today.replace(today.year + 1, 1, 1)
            else:
                next_month = today.replace(today.year, today.month + 1, 1)
            self.cleaned_data['date_fin'] = next_month - timezone.timedelta(days=1)
        elif periodicite == 'TRIMESTRIEL':
            # Trimestre en cours
            quarter = (today.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            self.cleaned_data['date_debut'] = today.replace(start_month, 1)
            if quarter == 4:
                end_date = today.replace(today.year + 1, 1, 1) - timezone.timedelta(days=1)
            else:
                end_date = today.replace(today.year, start_month + 3, 1) - timezone.timedelta(days=1)
            self.cleaned_data['date_fin'] = end_date
        elif periodicite == 'ANNUEL':
            # Année en cours
            self.cleaned_data['date_debut'] = today.replace(1, 1)
            self.cleaned_data['date_fin'] = today.replace(12, 31)


class FiltresAvancesForm(forms.Form):
    """Formulaire pour les filtres avancés spécifiques à chaque type d'état"""
    
    STATUT_CHOICES = [
        ('', 'Tous'),
        ('EN_ATTENTE', 'En attente'),
        ('VALIDEE_DG', 'Validée DG'),
        ('VALIDEE_DF', 'Validée DF'),
        ('PAYEE', 'Payée'),
        ('REJETEE', 'Rejetée'),
    ]
    
    DEVISE_CHOICES = [
        ('', 'Toutes'),
        ('USD', 'USD'),
        ('CDF', 'CDF'),
    ]
    
    # Filtres pour les demandes
    statut_demande = forms.ChoiceField(
        choices=STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Statut des demandes"
    )
    
    devise = forms.ChoiceField(
        choices=DEVISE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Devise"
    )
    
    montant_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="Montant minimum"
    )
    
    montant_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="Montant maximum"
    )
    
    # Filtres pour les recettes
    source_recette = forms.ChoiceField(
        choices=[
            ('', 'Toutes'),
            ('DROITS_ADMINISTRATIFS', 'Droits administratifs'),
            ('REDEVANCES', 'Redevances'),
            ('PARTICIPATIONS', 'Participations'),
            ('AUTRES', 'Autres'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Source de recette"
    )
    
    # Filtres pour les dépenses
    code_depense = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Code de dépense"
    )
    
    # Filtres pour les paiements
    inclure_paiements_partiels = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Inclure les paiements partiels"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        montant_min = cleaned_data.get('montant_min')
        montant_max = cleaned_data.get('montant_max')
        
        if montant_min and montant_max:
            if montant_min > montant_max:
                raise ValidationError("Le montant minimum doit être inférieur au montant maximum.")
        
        return cleaned_data
