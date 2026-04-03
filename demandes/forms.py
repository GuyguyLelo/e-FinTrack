"""
Formulaires pour la gestion des demandes de paiement
"""
from django import forms
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import DemandePaiement, ReleveDepense, Depense, NatureEconomique, Cheque, Paiement, DepenseFeuille
from accounts.models import Service
from banques.models import Banque
from releves.models import ReleveBancaire
from datetime import datetime


class StyledSelectWidget(forms.Select):
    """Widget personnalisé qui permet le rendu HTML dans les options"""
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if label and label.startswith('<span'):
            # Permettre le rendu HTML pour les labels stylisés
            option['label'] = mark_safe(label)
        return option


class DemandePaiementForm(forms.ModelForm):
    service_demandeur = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        label="Service demandeur",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    nature_economique = forms.ModelChoiceField(
        queryset=NatureEconomique.objects.none(),
        label="Article Littera",
        widget=StyledSelectWidget(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = DemandePaiement
        fields = ['service_demandeur', 'nomenclature', 'nature_economique', 'date_demande', 'description', 'montant', 'devise', 'pieces_justificatives']
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
            if self.user.role == 'CHEF_SERVICE' and self.user.service:  # Ancien rôle à adapter
                # Le chef de service ne peut créer que pour son propre service
                self.fields['service_demandeur'].queryset = Service.objects.filter(pk=self.user.service.pk)
                self.fields['service_demandeur'].initial = self.user.service
                self.fields['service_demandeur'].widget.attrs['readonly'] = True
            else:
                # Les autres rôles peuvent voir tous les services
                self.fields['service_demandeur'].queryset = Service.objects.filter(actif=True)
        else:
            self.fields['service_demandeur'].queryset = Service.objects.filter(actif=True)
        
        # Filtrer les natures économiques pour n'afficher que les actives
        # comme dans le formulaire d'état
        natures_queryset = NatureEconomique.objects.filter(active=True).order_by('code')
        self.fields['nature_economique'].queryset = natures_queryset
        
        # Personnaliser les choices avec style pour différencier les niveaux
        choices = self._get_styled_choices()
        self.fields['nature_economique'].choices = choices
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('service_demandeur', css_class='col-md-6'),
                Column('nomenclature', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column('nature_economique', css_class='col-md-12'),
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
    
    def _get_styled_choices(self):
        """Génère les choices avec style CSS pour différencier les niveaux hiérarchiques"""
        choices = [('', '--- Sélectionner un article littera ---')]
        
        # Récupérer toutes les natures actives organisées par hiérarchie
        natures = NatureEconomique.objects.filter(active=True).order_by('code')
        
        # Organiser par niveau
        level_0 = [n for n in natures if n.parent is None]  # Niveau 1
        level_1 = [n for n in natures if n.parent and n.parent.parent is None]  # Niveau 2
        level_2 = [n for n in natures if n.parent and n.parent.parent and n.parent.parent.parent is None]  # Niveau 3
        
        # Afficher niveau 1 (style principal)
        for i, nature in enumerate(level_0):
            choices.append((nature.pk, f'<span style="color: #2c3e50; font-weight: bold; font-size: 14px;">📁 {nature.code} - {nature.titre}</span>'))
            
            # Afficher niveau 2 (style secondaire)
            children_level_1 = [n for n in level_1 if n.parent_id == nature.pk]
            for child in children_level_1:
                choices.append((child.pk, f'<span style="color: #34495e; font-weight: 600; font-size: 13px; margin-left: 20px;">📂 {child.code} - {child.titre}</span>'))
                
                # Afficher niveau 3 (style tertiaire)
                children_level_2 = [n for n in level_2 if n.parent_id == child.pk]
                for grandchild in children_level_2:
                    choices.append((grandchild.pk, f'<span style="color: #7f8c8d; font-weight: normal; font-size: 12px; margin-left: 40px;">📄 {grandchild.code} - {grandchild.titre}</span>'))
        
        return choices


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


class ReleveDepenseCreateForm(forms.ModelForm):
    """Formulaire pour créer un relevé de dépenses vide (sans demandes)"""
    class Meta:
        model = ReleveDepense
        fields = ['periode', 'observation']
        widgets = {
            'periode': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observation': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Observations sur ce relevé...'}),
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
                    Submit('submit', 'Créer le relevé', css_class='btn btn-primary'),
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
        fields = ['code', 'titre', 'description', 'code_parent', 'parent', 'active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1.1.1'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'code_parent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code du parent (ex: 1 pour 1-171)'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Exclure l'instance actuelle du queryset du parent pour éviter les références circulaires
        # Et filtrer pour n'afficher que les natures actives
        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = NatureEconomique.objects.exclude(pk=self.instance.pk).filter(active=True)
        else:
            self.fields['parent'].queryset = NatureEconomique.objects.filter(active=True)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('code', css_class='col-md-4'),
                Column('titre', css_class='col-md-8'),
                css_class='mb-3'
            ),
            Row(
                Column('code_parent', css_class='col-md-6'),
                Column('parent', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column('active', css_class='col-12'),
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


class PaiementForm(forms.ModelForm):
    """Formulaire pour le paiement des demandes"""
    
    class Meta:
        model = Paiement
        fields = ['releve_depense', 'demande', 'montant_paye', 'beneficiaire', 'observations']
        widgets = {
            'montant_paye': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'beneficiaire': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du bénéficiaire...'
            }),
            'observations': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Observations sur ce paiement...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        releve_queryset = kwargs.pop('releve_queryset', None)
        super().__init__(*args, **kwargs)
        
        # Ajouter le champ releve_depense
        self.fields['releve_depense'] = forms.ModelChoiceField(
            queryset=ReleveDepense.objects.all().order_by('-periode'),
            label="Relevé de dépenses",
            widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_releve_depense'})
        )
        
        # Initialiser le champ demande avec le queryset fourni
        if releve_queryset is not None:
            self.fields['demande'].queryset = releve_queryset
        else:
            self.fields['demande'].queryset = DemandePaiement.objects.none()
        
        # Si un relevé est déjà sélectionné, filtrer les demandes
        if 'releve_depense' in self.data:
            try:
                releve_id = int(self.data.get('releve_depense'))
                releve = ReleveDepense.objects.get(pk=releve_id)
                self.fields['demande'].queryset = releve.demandes.all()
            except (ValueError, TypeError, ReleveDepense.DoesNotExist):
                pass
        elif self.instance and self.instance.pk:
            # Mode édition
            if self.instance.releve_depense:
                self.fields['releve_depense'].initial = self.instance.releve_depense
                self.fields['demande'].queryset = self.instance.releve_depense.demandes.all()
                if self.instance.demande:
                    self.fields['demande'].initial = self.instance.demande
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('releve_depense', css_class='col-md-6'),
                Column('demande', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column('montant_paye', css_class='col-md-6'),
                Column('beneficiaire', css_class='col-md-6'),
                css_class='mb-3'
            ),
            Row(
                Column('observations', css_class='col-12'),
                css_class='mb-3'
            ),
            Row(
                Column(
                    HTML('<div class="d-flex justify-content-end gap-2">'),
                    Submit('submit', 'Effectuer le paiement', css_class='btn btn-primary'),
                    HTML('</div>'),
                    css_class='col-12'
                ),
            ),
        )
    
    def clean(self):
        cleaned_data = super().clean()
        releve_depense = cleaned_data.get('releve_depense')
        demande = cleaned_data.get('demande')
        montant_paye = cleaned_data.get('montant_paye')
        
        if releve_depense and demande:
            # Vérifier que la demande appartient bien au relevé sélectionné
            if demande not in releve_depense.demandes.all():
                raise forms.ValidationError(
                    "Cette demande n'appartient pas au relevé de dépenses sélectionné."
                )
        
        if demande and montant_paye:
            if montant_paye > demande.reste_a_payer:
                raise forms.ValidationError(
                    f"Le montant à payer ({montant_paye}) ne peut pas dépasser "
                    f"le reste à payer ({demande.reste_a_payer})"
                )
        
        return cleaned_data


class PaiementMultipleForm(forms.Form):
    """Formulaire pour payer plusieurs demandes en même temps pour un relevé de dépenses"""
    
    releve_depense = forms.ModelChoiceField(
        queryset=ReleveDepense.objects.none(),
        label="Relevé de dépenses",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les relevés de dépenses qui ont des demandes non entièrement payées
        # Simplification : utiliser tous les relevés pour éviter les erreurs de relation
        self.fields['releve_depense'].queryset = ReleveDepense.objects.all().order_by('-periode')
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'releve_depense',
            Submit('submit', 'Voir les demandes à payer', css_class='btn btn-primary')
        )


from decimal import Decimal

MOIS_FEUILLE = [
    (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'), (5, 'Mai'), (6, 'Juin'),
    (7, 'Juillet'), (8, 'Août'), (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre'),
]


class DepenseFeuilleForm(forms.ModelForm):
    """Formulaire correspondant à la feuille DEPENSES (MOIS, ANNEE, DATE, NATURE ECONOMIQUE, LIBELLE, BANQUE, MONTANT FC, MONTANT $us, OBSERVATION)."""
    class Meta:
        model = DepenseFeuille
        fields = [
            'mois', 'annee', 'date', 'service_beneficiaire', 'nature_economique', 
            'libelle_depenses', 'banque', 'montant_fc', 'montant_usd', 'observation',
            # Champs optionnels pour mode workflow
            'releve_depense', 'demande', 'paiement_par', 'beneficiaire', 'date_paiement'
        ]
        widgets = {
            'mois': forms.Select(choices=MOIS_FEUILLE, attrs={'class': 'form-select'}),
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'service_beneficiaire': forms.Select(attrs={'class': 'form-select'}),
            'nature_economique': forms.Select(attrs={'class': 'form-select'}),
            'libelle_depenses': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'banque': forms.Select(attrs={'class': 'form-select'}),
            'montant_fc': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'montant_usd': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'observation': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            # Champs workflow
            'releve_depense': forms.Select(attrs={'class': 'form-select'}),
            'demande': forms.Select(attrs={'class': 'form-select'}),
            'paiement_par': forms.Select(attrs={'class': 'form-select'}),
            'beneficiaire': forms.TextInput(attrs={'class': 'form-control'}),
            'date_paiement': forms.DateTimeInput(format='%Y-%m-%d %H:%M', attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mois'].choices = MOIS_FEUILLE
        self.fields['nature_economique'].queryset = NatureEconomique.objects.filter(active=True).order_by('code')
        self.fields['nature_economique'].empty_label = "Sélectionner un article littéra"
        self.fields['service_beneficiaire'].queryset = Service.objects.filter(actif=True).order_by('nom_service')
        self.fields['service_beneficiaire'].empty_label = "Sélectionner un service bénéficiaire"
        self.fields['banque'].queryset = Banque.objects.filter(active=True).order_by('nom_banque')
        self.fields['banque'].empty_label = "Sélectionner une banque"
        
        # Configuration des champs workflow (uniquement s'ils existent)
        workflow_fields = ['releve_depense', 'demande', 'paiement_par', 'beneficiaire', 'date_paiement']
        for field_name in workflow_fields:
            if field_name in self.fields:
                if field_name == 'releve_depense':
                    self.fields[field_name].queryset = ReleveDepense.objects.all()
                    self.fields[field_name].empty_label = "Sélectionner un relevé (optionnel)"
                elif field_name == 'demande':
                    self.fields[field_name].queryset = DemandePaiement.objects.all()
                    self.fields[field_name].empty_label = "Sélectionner une demande (optionnel)"
                
                self.fields[field_name].required = False
                self.fields[field_name].widget.attrs['class'] += ' workflow-field'
        
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
                raise forms.ValidationError('La date doit correspondre au mois et à l\'année saisis.')
        
        # Validation de la cohérence des champs workflow
        releve = cleaned_data.get('releve_depense')
        demande = cleaned_data.get('demande')
        paiement_par = cleaned_data.get('paiement_par')
        beneficiaire = cleaned_data.get('beneficiaire')
        
        # Si on utilise le mode workflow, il faut au moins une demande ou un relevé
        if releve or demande:
            if not paiement_par:
                raise forms.ValidationError('En mode workflow, veuillez spécifier qui a effectué le paiement.')
            if not beneficiaire:
                raise forms.ValidationError('En mode workflow, veuillez spécifier le bénéficiaire du paiement.')


class DepenseFeuilleWorkflowForm(DepenseFeuilleForm):
    """Formulaire spécialisé pour le mode workflow (Demande → Relevé → Paiement)"""
    
    class Meta(DepenseFeuilleForm.Meta):
        fields = [
            'demande', 'releve_depense', 'paiement_par', 'beneficiaire', 'date_paiement',
            'mois', 'annee', 'date', 'service_beneficiaire', 'nature_economique', 
            'libelle_depenses', 'banque', 'montant_fc', 'montant_usd', 'observation'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs workflow obligatoires pour ce formulaire
        workflow_fields = ['demande', 'paiement_par', 'beneficiaire']
        for field_name in workflow_fields:
            self.fields[field_name].required = True
            self.fields[field_name].widget.attrs['class'] += ' required'
        
        # Rendre les champs de base obligatoires aussi
        base_fields = ['libelle_depenses', 'banque', 'montant_fc', 'montant_usd']
        for field_name in base_fields:
            self.fields[field_name].required = True


class DepenseFeuilleDirectForm(DepenseFeuilleForm):
    """Formulaire spécialisé pour le mode direct (tableau_bord_feuille)"""
    
    class Meta(DepenseFeuilleForm.Meta):
        fields = [
            'mois', 'annee', 'date', 'service_beneficiaire', 'nature_economique', 
            'libelle_depenses', 'banque', 'montant_fc', 'montant_usd', 'observation'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cacher complètement les champs workflow pour le mode direct
        workflow_fields = ['releve_depense', 'demande', 'paiement_par', 'beneficiaire', 'date_paiement']
        for field_name in workflow_fields:
            if field_name in self.fields:
                del self.fields[field_name]

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
