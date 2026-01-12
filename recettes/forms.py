"""
Formulaires pour la gestion des recettes
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from decimal import Decimal
from .models import Recette
from banques.models import Banque, CompteBancaire


class RecetteForm(forms.ModelForm):
    class Meta:
        model = Recette
        fields = ['banque', 'compte_bancaire', 'source_recette', 'description', 
                 'montant_usd', 'montant_cdf', 'date_encaissement', 'piece_jointe']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'date_encaissement': forms.DateInput(attrs={'type': 'date'}),
            'piece_jointe': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
            'montant_usd': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'montant_cdf': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les comptes selon la banque sélectionnée
        if 'banque' in self.data:
            banque_id = self.data.get('banque')
            if banque_id:
                self.fields['compte_bancaire'].queryset = CompteBancaire.objects.filter(
                    banque_id=banque_id, actif=True
                )
        elif self.instance and self.instance.banque_id:
            self.fields['compte_bancaire'].queryset = CompteBancaire.objects.filter(
                banque=self.instance.banque, actif=True
            )
        else:
            self.fields['compte_bancaire'].queryset = CompteBancaire.objects.none()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('banque', css_class='col-md-6'),
                Column('compte_bancaire', css_class='col-md-6'),
            ),
            Row(
                Column('source_recette', css_class='col-md-6'),
                Column('date_encaissement', css_class='col-md-6'),
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
        banque = cleaned_data.get('banque')
        compte_bancaire = cleaned_data.get('compte_bancaire')
        montant_usd = cleaned_data.get('montant_usd', Decimal('0.00'))
        montant_cdf = cleaned_data.get('montant_cdf', Decimal('0.00'))
        
        if banque and compte_bancaire:
            if compte_bancaire.banque != banque:
                raise forms.ValidationError(
                    'Le compte bancaire sélectionné n\'appartient pas à la banque choisie.'
                )
        
        # Vérifier qu'au moins un montant est renseigné
        if montant_usd <= 0 and montant_cdf <= 0:
            raise forms.ValidationError(
                'Vous devez renseigner au moins un montant (USD ou CDF).'
            )
        
        return cleaned_data

