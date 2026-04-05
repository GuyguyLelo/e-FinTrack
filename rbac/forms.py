"""
Formulaires pour la gestion des permissions et rôles
"""
from django import forms
from .models import Role, Permission


class RoleForm(forms.ModelForm):
    """Formulaire pour créer/modifier un rôle"""
    class Meta:
        model = Role
        fields = ['nom', 'code', 'description', 'couleur', 'icone', 'est_actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'couleur': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'icone': forms.TextInput(attrs={'class': 'form-control'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].label = "Nom du rôle"
        self.fields['code'].label = "Code du rôle"
        self.fields['description'].label = "Description"
        self.fields['couleur'].label = "Couleur"
        self.fields['icone'].label = "Icône Bootstrap"
        self.fields['est_actif'].label = "Rôle actif"


class PermissionForm(forms.ModelForm):
    """Formulaire pour créer/modifier une permission"""
    class Meta:
        model = Permission
        fields = ['nom', 'code', 'description', 'module', 'url_pattern', 'est_active']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'module': forms.Select(attrs={'class': 'form-control'}),
            'url_pattern': forms.TextInput(attrs={'class': 'form-control'}),
            'est_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].label = "Nom de la permission"
        self.fields['code'].label = "Code de la permission"
        self.fields['description'].label = "Description"
        self.fields['module'].label = "Module"
        self.fields['url_pattern'].label = "Pattern URL"
        self.fields['est_active'].label = "Permission active"
        
        # Définir les choix pour le module
        MODULE_CHOICES = [
            ('', '----------'),
            ('tableau_bord', 'Tableau de bord'),
            ('demandes', 'Demandes'),
            ('paiements', 'Paiements'),
            ('recettes', 'Recettes'),
            ('releves', 'Relevés'),
            ('etats', 'États'),
            ('banques', 'Banques'),
            ('clotures', 'Clôtures'),
            ('utilisateurs', 'Utilisateurs'),
            ('permissions', 'Permissions'),
        ]
        self.fields['module'].widget = forms.Select(
            choices=MODULE_CHOICES,
            attrs={'class': 'form-control'}
        )
