"""
Formulaires pour la gestion des demandes de paiement
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import DemandePaiement, ReleveDepense, Depense, NatureEconomique, Cheque
from accounts.models import Service
from banques.models import Banque
from datetime import datetime


class DemandePaiementForm(forms.ModelForm):
    class Meta:
        model = DemandePaiement
        fields = ['service_demandeur', 'nature_economique', 'date_demande', 'description', 'montant', 'devise', 'pieces_justificatives']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'pieces_justificatives': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png', 'class': 'form-control'}),
            'date_demande': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les services selon le rôle de l'utilisateur
        if self.user:
            if self.user.is_chef_service and self.user.service:
                # Le chef de service ne peut créer que pour son propre service
                self.fields['service_demandeur'].queryset = Service.objects.filter(pk=self.user.service.pk)
                self.fields['service_demandeur'].initial = self.user.service
                self.fields['service_demandeur'].widget.attrs['readonly'] = True
            else:
                # Les autres rôles peuvent voir tous les services
                self.fields['service_demandeur'].queryset = Service.objects.filter(actif=True)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('service_demandeur', css_class='col-md-6'),
                Column('nature_economique', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column('date_demande', css_class='col-md-6'),
                Column('devise', css_class='col-md-3'),
                Column('montant', css_class='col-md-3'),
                css_class='mb-3'
            ),
            Row(
                Column('description', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column('pieces_justificatives', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column(
                    HTML('<div class="d-flex justify-content-end gap-2">'),
                    Submit('submit', 'Enregistrer', css_class='btn btn-primary'),
                    HTML('</div>'),
                    css_class='col-12'
                ),
            ),
        )


class DemandePaiementValidationForm(forms.ModelForm):
    class Meta:
        model = DemandePaiement
        fields = ['statut', 'commentaire_rejet']
        widgets = {
            'commentaire_rejet': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('statut', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column('commentaire_rejet', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column(
                    HTML('<div class="d-flex justify-content-end gap-2">'),
                    Submit('submit', 'Valider', css_class='btn btn-success'),
                    HTML('</div>'),
                    css_class='col-12'
                ),
            ),
        )


class ReleveDepenseForm(forms.ModelForm):
    class Meta:
        model = ReleveDepense
        fields = ['periode', 'observation']
        widgets = {
            'periode': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observation': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('periode', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column('observation', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column(
                    HTML('<div class="d-flex justify-content-end gap-2">'),
                    Submit('submit', 'Enregistrer', css_class='btn btn-primary'),
                    HTML('</div>'),
                    css_class='col-12'
                ),
            ),
        )


class ReleveDepenseAutoForm(forms.Form):
    periode = forms.DateField(
        label="Période",
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        help_text="Sélectionnez le mois pour lequel générer le relevé"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('periode', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column(
                    HTML('<div class="d-flex justify-content-end gap-2">'),
                    Submit('submit', 'Générer le relevé', css_class='btn btn-primary'),
                    HTML('</div>'),
                    css_class='col-12'
                ),
            ),
        )


class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ['mois', 'annee', 'date_depense', 'date_demande', 'nomenclature', 
                  'libelle_depenses', 'montant_fc', 'montant_usd', 'observation']
        widgets = {
            'date_depense': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_demande': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'libelle_depenses': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'observation': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limiter les mois à 1-12
        self.fields['mois'].widget.attrs['min'] = 1
        self.fields['mois'].widget.attrs['max'] = 12
        
        # Limiter l'année à des valeurs raisonnables
        current_year = datetime.now().year
        self.fields['annee'].widget.attrs['min'] = 2020
        self.fields['annee'].widget.attrs['max'] = current_year + 10
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('mois', css_class='col-md-3'),
                Column('annee', css_class='col-md-3'),
                Column('date_depense', css_class='col-md-3'),
                Column('date_demande', css_class='col-md-3'),
                css_class='mb-3'
            ),
            Row(
                Column('nomenclature', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column('libelle_depenses', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column('montant_fc', css_class='col-md-6'),
                Column('montant_usd', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column('observation', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column(
                    HTML('<div class="d-flex justify-content-end gap-2">'),
                    Submit('submit', 'Enregistrer', css_class='btn btn-primary'),
                    HTML('</div>'),
                    css_class='col-12'
                ),
            ),
        )


class NatureEconomiqueForm(forms.ModelForm):
    class Meta:
        model = NatureEconomique
        fields = ['code', 'titre', 'parent']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1.1.1'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Exclure l'instance actuelle du queryset du parent pour éviter les références circulaires
        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = NatureEconomique.objects.exclude(pk=self.instance.pk)
        else:
            self.fields['parent'].queryset = NatureEconomique.objects.all()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('code', css_class='col-md-4'),
                Column('titre', css_class='col-md-8'),
                css_class='mb-3'
            ),
            Row(
                Column('parent', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column(
                    HTML('<div class="d-flex justify-content-end gap-2">'),
                    Submit('submit', 'Enregistrer', css_class='btn btn-primary'),
                    HTML('</div>'),
                    css_class='col-12'
                ),
            ),
        )


class ChequeBanqueForm(forms.Form):
    """Formulaire pour sélectionner la banque avant la génération du chèque"""
    banque = forms.ModelChoiceField(
        queryset=Banque.objects.filter(active=True).order_by('nom_banque'),
        label="Banque",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'required': True}),
        help_text="Sélectionnez la banque pour laquelle le chèque sera généré"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('banque', css_class='col-12'),
                css_class='mb-3'
            ),
        )
