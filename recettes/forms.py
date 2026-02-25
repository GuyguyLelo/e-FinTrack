"""
Formulaires pour la gestion des recettes
"""
from datetime import datetime
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from decimal import Decimal
from .models import Recette, SourceRecette, RecetteFeuille
from banques.models import Banque, CompteBancaire


class RecetteForm(forms.ModelForm):
    class Meta:
        model = Recette
        fields = ['banque', 'source_recette', 'description', 
                 'montant_usd', 'montant_cdf', 'date_encaissement', 'piece_jointe']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'date_encaissement': forms.DateInput(attrs={'type': 'date'}),
            'piece_jointe': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
            'montant_usd': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'montant_cdf': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'source_recette': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Initialiser les sources par défaut si nécessaire
        SourceRecette.get_sources_par_defaut()
        
        # Filtrer les sources actives
        self.fields['source_recette'].queryset = SourceRecette.objects.filter(active=True)
        self.fields['source_recette'].empty_label = "Sélectionner une source de recette"
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('banque', css_class='col-md-6'),
                Column('source_recette', css_class='col-md-6'),
            ),
            Row(
                Column('date_encaissement', css_class='col-md-6'),
                Column(css_class='col-md-6'),  # Espace vide pour l'alignement
            ),
            'description',
            Row(
                Column('montant_usd', css_class='col-md-6'),
                Column('montant_cdf', css_class='col-md-6'),
            ),
            'piece_jointe',
            Submit('submit', 'Enregistrer la recette', css_class='btn btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        montant_usd = cleaned_data.get('montant_usd', Decimal('0.00'))
        montant_cdf = cleaned_data.get('montant_cdf', Decimal('0.00'))
        
        # Vérifier qu'au moins un montant est renseigné
        if montant_usd <= 0 and montant_cdf <= 0:
            raise forms.ValidationError(
                'Vous devez renseigner au moins un montant (USD ou CDF).'
            )
        
        return cleaned_data


# Mois pour la feuille recettes (structure Excel) – noms en français
MOIS_FEUILLE = [
    (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'), (5, 'Mai'), (6, 'Juin'),
    (7, 'Juillet'), (8, 'Août'), (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre'),
]


class RecetteFeuilleForm(forms.ModelForm):
    """Formulaire correspondant à la feuille RECETTES (MOIS, ANNEE, DATE, LIBELLE, BANQUE, MONTANT FC, MONTANT $us)."""
    class Meta:
        model = RecetteFeuille
        fields = ['mois', 'annee', 'date', 'libelle_recette', 'banque', 'montant_fc', 'montant_usd']
        widgets = {
            'mois': forms.Select(choices=MOIS_FEUILLE, attrs={'class': 'form-select'}),
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'libelle_recette': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'banque': forms.Select(attrs={'class': 'form-select'}),
            'montant_fc': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'montant_usd': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mois'].choices = MOIS_FEUILLE
        self.fields['banque'].queryset = Banque.objects.filter(active=True).order_by('nom_banque')
        self.fields['banque'].empty_label = "Sélectionner une banque"
        
        # Rendre le champ annee en lecture seule
        self.fields['annee'].widget.attrs['readonly'] = True
        
        # Pour le mois, on va le rendre caché et afficher la valeur en lecture seule
        self.fields['mois'].widget = forms.HiddenInput()
        
        # Ajouter un champ d'affichage pour le mois (non lié au modèle)
        self.fields['mois_display'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control'})
        )
        
        # Pré-remplir le champ d'affichage avec la valeur du mois
        if self.initial.get('mois'):
            mois_dict = dict(MOIS_FEUILLE)
            mois_value = self.initial.get('mois')
            self.fields['mois_display'].initial = mois_dict.get(mois_value, '')
        
        # Le champ date reste modifiable mais sera pré-rempli avec la période en cours

    def clean_annee(self):
        annee = self.cleaned_data.get('annee')
        if annee is not None:
            if annee < 1990 or annee > 2100:
                raise forms.ValidationError('L\'année doit être entre 1990 et 2100.')
        return annee

    def clean(self):
        cleaned_data = super().clean()
        montant_fc = cleaned_data.get('montant_fc') or Decimal('0.00')
        montant_usd = cleaned_data.get('montant_usd') or Decimal('0.00')
        if montant_fc <= 0 and montant_usd <= 0:
            raise forms.ValidationError('Renseignez au moins un montant (FC ou $us).')

        # La date doit correspondre au mois et à l'année saisis
        date_val = cleaned_data.get('date')
        mois_val = cleaned_data.get('mois')
        annee_val = cleaned_data.get('annee')
        if date_val is not None and mois_val is not None and annee_val is not None:
            if date_val.month != mois_val or date_val.year != annee_val:
                raise forms.ValidationError({
                    'date': 'La date doit correspondre au mois et à l\'année choisis (mois {} / année {}).'.format(mois_val, annee_val)
                })
        return cleaned_data

