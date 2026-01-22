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
        self.helper.form_method = 'post'
        self.helper.form_tag = True
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
    
    def clean_numero_compte(self):
        """Valider l'unicité du numéro de compte"""
        numero_compte = self.cleaned_data.get('numero_compte')
        
        if numero_compte:
            # Vérifier l'unicité globale de numero_compte (unique=True dans le modèle)
            queryset = CompteBancaire.objects.filter(numero_compte=numero_compte)
            
            # Exclure l'instance actuelle si on est en mode modification
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError(
                    f'Un compte avec le numéro "{numero_compte}" existe déjà.'
                )
        
        return numero_compte
    
    def clean(self):
        """Validation globale du formulaire pour vérifier unique_together"""
        cleaned_data = super().clean()
        numero_compte = cleaned_data.get('numero_compte')
        banque = cleaned_data.get('banque')
        
        # Vérifier la contrainte unique_together (banque, numero_compte)
        if numero_compte and banque:
            queryset = CompteBancaire.objects.filter(
                banque=banque,
                numero_compte=numero_compte
            )
            
            # Exclure l'instance actuelle si on est en mode modification
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError({
                    'numero_compte': f'Un compte avec le numéro "{numero_compte}" existe déjà pour cette banque "{banque.nom_banque}".'
                })
        
        return cleaned_data

