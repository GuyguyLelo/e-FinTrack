"""
Vues pour l'authentification
"""
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt


class LoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Vérifier si la session a expiré
        if self.request.GET.get('session_expired'):
            context['session_expired'] = True
        return context
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_active:
            login(self.request, user)
            
            # Redirection selon le rôle
            if user.role == 'DG' or user.role == 'CD_FINANCE':
                return redirect('/tableau-bord-feuilles/')
            else:
                return redirect('/')
        
        return super().form_valid(form)


class LoginTestView(TemplateView):
    """Vue de connexion de test sans CSRF pour les tests"""
    template_name = 'accounts/login_test.html'
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_active:
            login(request, user)
            return redirect('/')
        
        return render(request, self.template_name, {
            'error': 'Identifiants invalides'
        })


class LoginSimpleView(TemplateView):
    """Vue de connexion simple sans middleware"""
    template_name = 'accounts/login_simple.html'
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_active:
            login(request, user)
            return redirect('/')
        
        return render(request, self.template_name, {
            'error': 'Identifiants invalides'
        })


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
