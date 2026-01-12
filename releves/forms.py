"""
Formulaires pour la gestion des relevés bancaires
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset
from .models import ReleveBancaire, MouvementBancaire
from banques.models import Banque, CompteBancaire
from recettes.models import Recette
from demandes.models import DemandePaiement


class ReleveBancaireForm(forms.ModelForm):
    class Meta:
        model = ReleveBancaire
        fields = ['banque', 'compte_bancaire', 'periode_debut', 'periode_fin', 
                 'releve_pdf', 'observations']
        widgets = {
            'periode_debut': forms.DateInput(attrs={'type': 'date'}),
            'periode_fin': forms.DateInput(attrs={'type': 'date'}),
            'releve_pdf': forms.FileInput(attrs={'accept': '.pdf'}),
            'observations': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les comptes selon la banque
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
                Column('periode_debut', css_class='col-md-6'),
                Column('periode_fin', css_class='col-md-6'),
            ),
            'releve_pdf',
            'observations',
            Submit('submit', 'Enregistrer le relevé', css_class='btn btn-primary')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        periode_debut = cleaned_data.get('periode_debut')
        periode_fin = cleaned_data.get('periode_fin')
        
        if periode_debut and periode_fin:
            if periode_debut > periode_fin:
                raise forms.ValidationError(
                    'La date de début ne peut pas être postérieure à la date de fin.'
                )
        
        return cleaned_data


class MouvementBancaireForm(forms.ModelForm):
    class Meta:
        model = MouvementBancaire
        fields = ['type_mouvement', 'reference_operation', 'description', 'montant', 
                 'date_operation', 'beneficiaire_ou_source', 'lie_a_recette', 'lie_a_demande']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date_operation': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        releve = kwargs.pop('releve', None)
        super().__init__(*args, **kwargs)
        
        if releve:
            # Filtrer les recettes et demandes selon la devise du relevé
            devise = releve.devise
            self.fields['lie_a_recette'].queryset = Recette.objects.filter(
                devise=devise, valide=True
            )
            self.fields['lie_a_demande'].queryset = DemandePaiement.objects.filter(
                devise=devise, statut='PAYEE'
            )
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('type_mouvement', css_class='col-md-6'),
                Column('date_operation', css_class='col-md-6'),
            ),
            'reference_operation',
            'description',
            Row(
                Column('montant', css_class='col-md-6'),
                Column('beneficiaire_ou_source', css_class='col-md-6'),
            ),
            Row(
                Column('lie_a_recette', css_class='col-md-6'),
                Column('lie_a_demande', css_class='col-md-6'),
            ),
            Submit('submit', 'Ajouter le mouvement', css_class='btn btn-primary')
        )


class MouvementBancaireFormSet(forms.BaseInlineFormSet):
    """FormSet pour gérer plusieurs mouvements"""
    def clean(self):
        if any(self.errors):
            return
        
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                # Validations supplémentaires si nécessaire
                pass

