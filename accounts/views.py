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
from .models import User


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
            if user.role == 'DG' or user.role == 'CD_FINANCE' or user.role == 'ADMIN':
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
    """Vue pour afficher les utilisateurs de la base de données (identifiants d'accès)"""
    template_name = 'accounts/identifiants.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les utilisateurs actifs depuis la base de données
        users = User.objects.filter(is_active=True).select_related('service').order_by('role', 'username')
        
        # Grouper par catégorie (Direction / Opérationnel)
        ROLES_DIRECTION = {'SUPER_ADMIN', 'ADMIN', 'DG', 'DF', 'CD_FINANCE'}
        identifiants = {'Direction': [], 'Opérationnel': []}
        
        for u in users:
            item = {
                'username': u.username,
                'role': u.get_role_display(),
                'service': u.service.nom_service if u.service else '—',
            }
            if u.role in ROLES_DIRECTION:
                identifiants['Direction'].append(item)
            else:
                identifiants['Opérationnel'].append(item)
        
        # Retirer les catégories vides
        context['identifiants'] = {k: v for k, v in identifiants.items() if v}
        return context
