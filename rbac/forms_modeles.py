"""
Formulaires pour l'interface RBAC basée sur les modèles Django
"""
from django import forms
from django.apps import apps
from .models_modele import PermissionModele, RoleModele


class PermissionModeleForm(forms.ModelForm):
    """Formulaire pour créer/modifier une permission basée sur un modèle"""
    
    modele_django = forms.ChoiceField(
        choices=[
            ('', 'Choisissez un modèle'),
            ('banque', 'Banque'),
            ('comptebancaire', 'Compte Bancaire'),
            ('depensefeuille', 'Dépense (feuille)'),
            ('demande', 'Demande'),
            ('paiement', 'Paiement'),
            ('cheque', 'Chèque'),
            ('recette', 'Recette'),
            ('sourcerecette', 'Source de recette'),
            ('recettefeuille', 'Recette (feuille)'),
            ('cloturemensuelle', 'Clôture mensuelle'),
            ('etatgenerique', 'État généré'),
            ('configurationetat', 'Configuration d\'état'),
            ('historiquegeneration', 'Historique de génération'),
            ('relevebancaire', 'Relevé Bancaire'),
            ('mouvementbancaire', 'Mouvement Bancaire'),
            ('service', 'Service'),
            ('user', 'Utilisateur'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    app_label = forms.ChoiceField(
        choices=[
            ('', 'Choisissez une application'),
            ('banques', 'Banques'),
            ('demandes', 'Demandes'),
            ('recettes', 'Recettes'),
            ('clotures', 'Clôtures'),
            ('etats', 'États'),
            ('releves', 'Relevés'),
            ('accounts', 'Utilisateurs'),
            ('rapports', 'Rapports'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    class Meta:
        model = PermissionModele
        fields = ['nom', 'description', 'modele_django', 'app_label', 'action']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Voir la liste des dépenses'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Décrivez en détail ce que cette permission permet...'
            }),
            'action': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Choisissez une action'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remplir dynamiquement la liste des modèles Django
        modeles_choices = self.get_modeles_choices()
        self.fields['modele_django'].choices = modeles_choices
        
        app_choices = self.get_app_labels_choices()
        self.fields['app_label'].choices = app_choices
        
        # Debug pour vérifier
        print(f"MODELES CHOICES: {modeles_choices}")
        print(f"APP CHOICES: {app_choices}")
    
    def get_modeles_choices(self):
        """Obtenir la liste des modèles Django disponibles"""
        modeles = [
            ('banque', 'Banque'),
            ('comptebancaire', 'Compte Bancaire'),
            ('depensefeuille', 'Dépense (feuille)'),
            ('demande', 'Demande'),
            ('paiement', 'Paiement'),
            ('cheque', 'Chèque'),
            ('recette', 'Recette'),
            ('sourcerecette', 'Source de recette'),
            ('recettefeuille', 'Recette (feuille)'),
            ('cloturemensuelle', 'Clôture mensuelle'),
            ('etatgenerique', 'État généré'),
            ('configurationetat', 'Configuration d\'état'),
            ('historiquegeneration', 'Historique de génération'),
            ('relevebancaire', 'Relevé Bancaire'),
            ('mouvementbancaire', 'Mouvement Bancaire'),
            ('service', 'Service'),
            ('user', 'Utilisateur'),
        ]
        return sorted(modeles, key=lambda x: x[1])
    
    def get_app_labels_choices(self):
        """Obtenir la liste des applications Django disponibles"""
        app_labels = [
            ('banques', 'Banques'),
            ('demandes', 'Demandes'),
            ('recettes', 'Recettes'),
            ('clotures', 'Clôtures'),
            ('etats', 'États'),
            ('releves', 'Relevés'),
            ('accounts', 'Utilisateurs'),
            ('rapports', 'Rapports'),
        ]
        return app_labels


class RoleModeleForm(forms.ModelForm):
    """Formulaire pour créer/modifier un rôle basé sur les modèles"""
    
    niveau_acces = forms.ChoiceField(
        choices=[
            (1, 'Niveau 1 - Accès de base'),
            (2, 'Niveau 2 - Accès intermédiaire'),
            (3, 'Niveau 3 - Accès avancé'),
            (4, 'Niveau 4 - Accès expert'),
            (5, 'Niveau 5 - Accès administrateur'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    icone = forms.ChoiceField(
        choices=[
            ('bi-person', 'Personne'),
            ('bi-people', 'Personnes'),
            ('bi-shield-check', 'Bouclier'),
            ('bi-key', 'Clé'),
            ('bi-journal-text', 'Journal'),
            ('bi-bank', 'Banque'),
            ('bi-graph-up', 'Graphique'),
            ('bi-gear', 'Paramètres'),
            ('bi-star', 'Étoile'),
            ('bi-briefcase', 'Mallette'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    class Meta:
        model = RoleModele
        fields = ['nom', 'description', 'couleur', 'icone', 'niveau_acces']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Gestionnaire Dépenses'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez le rôle et ses responsabilités...'
            }),
            'couleur': forms.TextInput(attrs={
                'class': 'form-control form-control-color',
                'type': 'color',
                'placeholder': '#007bff'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les choix
        self.fields['icone'].choices = [
            ('bi-person', '👤 Utilisateur'),
            ('bi-bank', '🏦 Banques'),
            ('bi-calculator', '🧮 Comptable'),
            ('bi-briefcase', '💼 Directeur'),
            ('bi-pencil-square', '✍️ Opérateur'),
            ('bi-shield-check', '🛡️ Administrateur'),
            ('bi-journal-text', '📋 Dépenses'),
            ('bi-cash-stack', '💰 Recettes'),
            ('bi-file-text', '📄 États'),
            ('bi-people', '👥 Utilisateurs'),
            ('bi-gear', '⚙️ Paramètres'),
        ]
        
        self.fields['niveau_acces'].choices = [
            (1, '🟢 Niveau 1 - Accès de base'),
            (2, '🟡 Niveau 2 - Accès intermédiaire'),
            (3, '🟠 Niveau 3 - Accès avancé'),
            (4, '🔴 Niveau 4 - Accès expert'),
            (5, '🟣 Niveau 5 - Accès complet'),
        ]


class RolePermissionsForm(forms.Form):
    """Formulaire pour gérer les permissions d'un rôle"""
    
    def __init__(self, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        
        # Grouper les permissions par modèle
        permissions_by_modele = {}
        for perm in PermissionModele.objects.filter(est_active=True):
            if perm.modele_django not in permissions_by_modele:
                permissions_by_modele[perm.modele_django] = []
            permissions_by_modele[perm.modele_django].append(perm)
        
        # Créer des checkboxes pour chaque permission
        for modele, permissions in permissions_by_modele.items():
            for perm in permissions:
                field_name = f"perm_{perm.id}"
                self.fields[field_name] = forms.BooleanField(
                    required=False,
                    label=f"{perm.get_action_display()} - {perm.nom}",
                    initial=role.permissions_modeles.filter(id=perm.id).exists(),
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input'
                    })
                )
    
    def save(self):
        """Sauvegarder les permissions du rôle"""
        # D'abord, enlever toutes les permissions existantes
        self.role.permissions_modeles.clear()
        
        # Ensuite, ajouter les permissions cochées
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('perm_') and value:
                perm_id = field_name.split('_')[1]
                try:
                    perm = PermissionModele.objects.get(id=perm_id)
                    self.role.permissions_modeles.add(perm)
                except PermissionModele.DoesNotExist:
                    pass


class QuickRoleForm(forms.Form):
    """Formulaire rapide pour créer un rôle avec permissions prédéfinies"""
    
    nom = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom du rôle'
        })
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Description du rôle'
        })
    )
    
    modele_principal = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    permissions_type = forms.ChoiceField(
        choices=[
            ('lecture', '👁️ Lecture seule (voir)'),
            ('saisie', '✍️ Saisie (voir, créer, modifier)'),
            ('gestion', '⚙️ Gestion complète (voir, créer, modifier, supprimer)'),
            ('validation', '✅ Validation (voir, valider)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remplir la liste des modèles
        modeles = []
        apps_to_analyze = ['banques', 'demandes', 'recettes', 'clotures', 'etats']
        
        for app_name in apps_to_analyze:
            try:
                app_config = apps.get_app_config(app_name)
                for model_name, model_class in app_config.models.items():
                    if hasattr(model_class, '_meta'):
                        verbose_name = model_class._meta.verbose_name
                        modeles.append((model_name, verbose_name))
            except LookupError:
                continue
        
        self.fields['modele_principal'].choices = sorted(modeles, key=lambda x: x[1])
