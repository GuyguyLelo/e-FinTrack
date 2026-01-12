"""
Vues pour l'authentification
"""
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_active:
            login(self.request, user)
            # Redirection vers le dashboard (racine)
            return redirect('/')
        
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    login_url = reverse_lazy('accounts:login')


class IdentifiantsView(TemplateView):
    """Vue pour afficher les identifiants de connexion (développement/test uniquement)"""
    template_name = 'accounts/identifiants.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Liste des identifiants par défaut
        context['identifiants'] = {
            'Direction': [
                {'username': 'admin', 'password': 'admin', 'role': 'Administrateur', 'service': 'Direction Générale'},
                {'username': 'dg', 'password': 'dg123456', 'role': 'Directeur Général', 'service': 'Direction Générale'},
                {'username': 'daf', 'password': 'daf123456', 'role': 'Directeur Administratif et Financier', 'service': 'Direction Générale'},
                {'username': 'df', 'password': 'df123456', 'role': 'Directeur Financier', 'service': 'Service Financier'},
            ],
            'Opérationnel': [
                {'username': 'comptable1', 'password': 'comptable123', 'role': 'Comptable', 'service': 'Service Comptable'},
                {'username': 'comptable2', 'password': 'comptable123', 'role': 'Comptable', 'service': 'Service Comptable'},
                {'username': 'chef_service', 'password': 'chef123456', 'role': 'Chef de Service', 'service': 'Service Financier'},
                {'username': 'auditeur', 'password': 'audit123456', 'role': 'Auditeur', 'service': 'Service Audit'},
                {'username': 'operateur1', 'password': 'operateur123', 'role': 'Opérateur de Saisie', 'service': 'Service Comptable'},
                {'username': 'operateur2', 'password': 'operateur123', 'role': 'Opérateur de Saisie', 'service': 'Service Comptable'},
            ]
        }
        
        return context

