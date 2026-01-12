"""
Formulaires pour le rapprochement bancaire
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import RapprochementBancaire
from banques.models import Banque, CompteBancaire
from releves.models import ReleveBancaire


class RapprochementBancaireForm(forms.ModelForm):
    class Meta:
        model = RapprochementBancaire
        fields = ['banque', 'compte_bancaire', 'periode_mois', 'periode_annee', 
                 'solde_banque', 'releve_bancaire', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrer les comptes selon la banque
        if 'banque' in self.data:
            banque_id = self.data.get('banque')
            if banque_id:
                self.fields['compte_bancaire'].queryset = CompteBancaire.objects.filter(
                    banque_id=banque_id, actif=True
                )
                self.fields['releve_bancaire'].queryset = ReleveBancaire.objects.filter(
                    banque_id=banque_id, valide=True
                )
        elif self.instance and self.instance.banque_id:
            self.fields['compte_bancaire'].queryset = CompteBancaire.objects.filter(
                banque=self.instance.banque, actif=True
            )
            self.fields['releve_bancaire'].queryset = ReleveBancaire.objects.filter(
                banque=self.instance.banque, valide=True
            )
        else:
            self.fields['compte_bancaire'].queryset = CompteBancaire.objects.none()
            self.fields['releve_bancaire'].queryset = ReleveBancaire.objects.none()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('banque', css_class='col-md-6'),
                Column('compte_bancaire', css_class='col-md-6'),
            ),
            Row(
                Column('periode_mois', css_class='col-md-4'),
                Column('periode_annee', css_class='col-md-4'),
                Column('releve_bancaire', css_class='col-md-4'),
            ),
            'solde_banque',
            'commentaire',
            Submit('submit', 'Créer le rapprochement', css_class='btn btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        periode_mois = cleaned_data.get('periode_mois')
        periode_annee = cleaned_data.get('periode_annee')
        
        if periode_mois and (periode_mois < 1 or periode_mois > 12):
            raise forms.ValidationError('Le mois doit être entre 1 et 12.')
        
        if periode_annee and periode_annee < 2020:
            raise forms.ValidationError('L\'année doit être supérieure à 2020.')
        
        return cleaned_data

