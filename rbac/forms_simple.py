"""
Exemple d'interface utilisateur simplifiée pour la création de permissions
"""
from django import forms
from django.contrib import admin
from rbac.models_improved import CategoriePermission, Permission, Role


# FORMULAIRES SIMPLIFIÉS POUR UTILISATEURS NON-TECHNIQUES

class CategoriePermissionForm(forms.ModelForm):
    """Formulaire simple pour créer des catégories"""
    
    class Meta:
        model = CategoriePermission
        fields = ['nom', 'description', 'icone', 'ordre']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Banques, Demandes, Recettes...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Décrivez ce que cette catégorie contient...'
            }),
            'icone': forms.Select(attrs={
                'class': 'form-select',
                'choices': [
                    ('bi-bank', '🏦 Banques'),
                    ('bi-cash-stack', '💰 Recettes'),
                    ('bi-file-earmark-text', '📄 Demandes'),
                    ('bi-file-text', '📊 États'),
                    ('bi-people', '👥 Utilisateurs'),
                    ('bi-calendar-check', '📅 Clôtures'),
                    ('bi-speedometer2', '📈 Tableau de bord'),
                    ('bi-gear', '⚙️ Paramètres'),
                ]
            }),
            'ordre': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1, 2, 3...'
            })
        }


class PermissionSimpleForm(forms.ModelForm):
    """Formulaire simplifié pour créer des permissions (sans champs techniques)"""
    
    class Meta:
        model = Permission
        fields = ['nom', 'description', 'categorie', 'action']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Créer une banque, Voir les demandes...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Décrivez en détail ce que cette permission permet...'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Choisissez une catégorie...'
            }),
            'action': forms.Select(attrs={
                'class': 'form-select',
                'choices': [
                    ('voir', '👁️ Voir - Permet de voir/consulter'),
                    ('creer', '➕ Créer - Permet de créer/ajouter'),
                    ('modifier', '✏️ Modifier - Permet de modifier/éditer'),
                    ('supprimer', '🗑️ Supprimer - Permet de supprimer'),
                    ('valider', '✅ Valider - Permet de valider/approuver'),
                    ('effectuer', '⚡ Effectuer - Permet d\'effectuer une action'),
                    ('generer', '📊 Générer - Permet de générer des documents'),
                ]
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].queryset = CategoriePermission.objects.filter(est_active=True)


class RoleSimpleForm(forms.ModelForm):
    """Formulaire simplifié pour créer des rôles"""
    
    class Meta:
        model = Role
        fields = ['nom', 'description', 'categorie', 'couleur', 'icone', 'niveau_acces']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Gestionnaire Banques, Comptable, Directeur...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Décrivez le rôle et les responsabilités...'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Catégorie principale du rôle...'
            }),
            'couleur': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'placeholder': '#007bff'
            }),
            'icone': forms.Select(attrs={
                'class': 'form-select',
                'choices': [
                    ('bi-person', '👤 Utilisateur'),
                    ('bi-bank', '🏦 Banques'),
                    ('bi-calculator', '🧮 Comptable'),
                    ('bi-briefcase', '💼 Directeur'),
                    ('bi-pencil-square', '✍️ Opérateur'),
                    ('bi-shield-check', '🛡️ Administrateur'),
                ]
            }),
            'niveau_acces': forms.Select(attrs={
                'class': 'form-select',
                'choices': [
                    (1, '🟢 Niveau 1 - Accès de base'),
                    (2, '🟡 Niveau 2 - Accès intermédiaire'),
                    (3, '🟠 Niveau 3 - Accès avancé'),
                    (4, '🔴 Niveau 4 - Accès expert'),
                    (5, '🟣 Niveau 5 - Accès complet'),
                ]
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].queryset = CategoriePermission.objects.filter(est_active=True)


class RolePermissionsForm(forms.Form):
    """Formulaire pour assigner les permissions à un rôle"""
    
    def __init__(self, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        
        # Grouper les permissions par catégorie
        categories = {}
        for perm in Permission.objects.filter(est_active=True):
            if perm.categorie not in categories:
                categories[perm.categorie] = []
            categories[perm.categorie].append(perm)
        
        # Créer des checkboxes pour chaque permission
        for categorie, permissions in categories.items():
            for perm in permissions:
                field_name = f"perm_{perm.id}"
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    label=f"{perm.get_action_display()} - {perm.nom}",
                    initial=role.permissions.filter(id=perm.id).exists(),
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input'
                    })
                )
    
    def save(self):
        """Sauvegarder les permissions du rôle"""
        # D'abord, enlever toutes les permissions existantes
        self.role.permissions.clear()
        
        # Ensuite, ajouter les permissions cochées
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('perm_') and value:
                perm_id = field_name.split('_')[1]
                try:
                    perm = Permission.objects.get(id=perm_id)
                    self.role.permissions.add(perm)
                except Permission.DoesNotExist:
                    pass


# INTERFACE ADMIN SIMPLIFIÉE

@admin.register(CategoriePermission)
class CategoriePermissionAdmin(admin.ModelAdmin):
    """Admin simple pour les catégories"""
    list_display = ['nom', 'icone', 'ordre', 'est_active']
    list_filter = ['est_active']
    search_fields = ['nom', 'description']
    ordering = ['ordre', 'nom']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin simple pour les permissions"""
    list_display = ['nom', 'categorie', 'action', 'code', 'est_active']
    list_filter = ['categorie', 'action', 'est_active']
    search_fields = ['nom', 'description', 'code']
    ordering = ['categorie__ordre', 'nom']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categorie')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin simple pour les rôles"""
    list_display = ['nom', 'categorie', 'niveau_acces', 'permissions_count', 'est_actif']
    list_filter = ['categorie', 'niveau_acces', 'est_active']
    search_fields = ['nom', 'description', 'code']
    ordering = ['niveau_acces', 'nom']
    
    def permissions_count(self, obj):
        return obj.permissions.count()
    permissions_count.short_description = 'Permissions'
    
    filter_horizontal = ['permissions']
