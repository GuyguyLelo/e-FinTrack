"""
Formulaires personnalisés pour l'application accounts
"""
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django import forms
from .models import User, Service


class UserCreationForm(BaseUserCreationForm):
    """Formulaire de création d'utilisateur personnalisé"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    service = forms.ModelChoiceField(queryset=Service.objects.filter(actif=True), required=False)
    
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'service', 'password1', 'password2')
    
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
        self.fields['service'].label = "Service"
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
        user.service = self.cleaned_data.get('service')
        
        if commit:
            user.save()
        return user
