"""
Formulaires pour la gestion des banques
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Banque, CompteBancaire


class BanqueForm(forms.ModelForm):
    class Meta:
        model = Banque
        fields = ['nom_banque', 'code_swift', 'adresse', 'email', 'telephone', 'active']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('nom_banque', css_class='col-md-6'),
                Column('code_swift', css_class='col-md-6'),
            ),
            'adresse',
            Row(
                Column('email', css_class='col-md-6'),
                Column('telephone', css_class='col-md-6'),
            ),
            'active',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )


class CompteBancaireForm(forms.ModelForm):
    class Meta:
        model = CompteBancaire
        fields = ['banque', 'intitule_compte', 'numero_compte', 'devise', 
                  'solde_initial', 'date_ouverture', 'actif']
        widgets = {
            'date_ouverture': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('banque', css_class='col-md-6'),
                Column('devise', css_class='col-md-6'),
            ),
            Row(
                Column('intitule_compte', css_class='col-md-6'),
                Column('numero_compte', css_class='col-md-6'),
            ),
            Row(
                Column('solde_initial', css_class='col-md-6'),
                Column('date_ouverture', css_class='col-md-6'),
            ),
            'actif',
            Submit('submit', 'Enregistrer', css_class='btn btn-primary')
        )

