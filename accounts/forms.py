"""
Formulaires personnalisés pour l'application accounts
"""
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django import forms
from .models import User, Service
from rbac.models import Role
from rbac.models_modele import RoleModele


class UserCreationForm(BaseUserCreationForm):
    """Formulaire de création d'utilisateur personnalisé"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        label="Rôle"
    )
    
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['role'].required = True
        
        # Personnaliser les labels
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['email'].label = "Adresse email"
        self.fields['first_name'].label = "Prénom"
        self.fields['last_name'].label = "Nom"
        self.fields['role'].label = "Rôle"
        self.fields['password1'].label = "Mot de passe"
        self.fields['password2'].label = "Confirmer le mot de passe"
        
        # Ajouter les classes Bootstrap
        for field_name, field in self.fields.items():
            if field_name not in ['is_active', 'is_superuser']:
                field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Formulaire de modification d'utilisateur avec rôles directs"""
    
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        label="Rôle"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'actif')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les labels
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['email'].label = "Adresse email"
        self.fields['first_name'].label = "Prénom"
        self.fields['last_name'].label = "Nom"
        self.fields['role'].label = "Rôle"
        self.fields['actif'].label = "Utilisateur actif"
        
        # Ajouter les classes Bootstrap
        for field_name, field in self.fields.items():
            if field_name != 'actif':
                field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Assigner le rôle directement depuis le formulaire
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
        return user


class ServiceForm(forms.ModelForm):
    """Formulaire pour la gestion des services avec structure hiérarchique"""
    
    class Meta:
        model = Service
        fields = ['nom_service', 'description', 'parent_service', 'actif']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'parent_service': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les labels
        self.fields['nom_service'].label = "Nom du service"
        self.fields['description'].label = "Description"
        self.fields['parent_service'].label = "Service parent"
        self.fields['actif'].label = "Service actif"
        
        # Ajouter les classes Bootstrap
        for field_name, field in self.fields.items():
            if field_name != 'actif':
                field.widget.attrs.update({'class': 'form-control'})
        
        # Filtrer les services parents pour éviter les références circulaires
        if self.instance and self.instance.pk:
            # Exclure le service lui-même et ses enfants des parents possibles
            excluded_services = [self.instance.pk] + [child.pk for child in self.instance.get_all_children()]
            self.fields['parent_service'].queryset = Service.objects.filter(
                actif=True
            ).exclude(pk__in=excluded_services)
        else:
            self.fields['parent_service'].queryset = Service.objects.filter(actif=True)
        
        # Ajouter une option vide pour le niveau racine
        self.fields['parent_service'].empty_label = "-- Aucun (service racine) --"
