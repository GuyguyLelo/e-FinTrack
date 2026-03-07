"""
<<<<<<< HEAD
Vues pour l'authentification et la gestion des utilisateurs
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import JsonResponse
from .models import User, Service
=======
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
>>>>>>> 5a1f2ed825b571d0531b0147150a27218e958d7a


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
<<<<<<< HEAD
            if user.role == 'SUPER_ADMIN':
                return redirect('/tableau-bord-feuilles/')
            elif user.role == 'DG' or user.role == 'CD_FINANCE':
                return redirect('/tableau-bord-feuilles/')
            elif user.role == 'ADMIN':
                # Admin -> toujours redirigé vers les natures économiques
                return redirect('/demandes/natures/')
=======
            if user.role == 'DG' or user.role == 'CD_FINANCE' or user.role == 'ADMIN':
                return redirect('/tableau-bord-feuilles/')
>>>>>>> 5a1f2ed825b571d0531b0147150a27218e958d7a
            else:
                return redirect('/')
        
        return super().form_valid(form)


<<<<<<< HEAD
=======
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

>>>>>>> 5a1f2ed825b571d0531b0147150a27218e958d7a

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    login_url = reverse_lazy('accounts:login')


<<<<<<< HEAD
class LogoutView(TemplateView):
    """Vue de déconnexion personnalisée qui accepte GET et POST"""
    
    def dispatch(self, request, *args, **kwargs):
        # Accepter les deux méthodes GET et POST
        if request.method == 'GET' or request.method == 'POST':
            logout(request)
            messages.info(request, 'Vous avez été déconnecté avec succès')
            return redirect('accounts:login')
        else:
            # Si c'est une autre méthode, renvoyer une erreur
            from django.http import HttpResponseNotAllowed
            return HttpResponseNotAllowed(['GET', 'POST'])


# Mixin pour vérifier si l'utilisateur est SuperAdmin
class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'SUPER_ADMIN'
    
    def handle_no_permission(self):
        messages.error(self.request, "Accès réservé au Super Administrateur")
        return redirect('accounts:login')


# Mixin pour vérifier les permissions de gestion des utilisateurs
class UserManagementMixin(UserPassesTestMixin):
    def test_func(self):
        return (self.request.user.is_authenticated and 
                self.request.user.peut_gerer_utilisateurs())
    
    def handle_no_permission(self):
        messages.error(self.request, "Accès réservé aux administrateurs")
        return redirect('accounts:login')


# Mixin pour vérifier les permissions de modification d'utilisateurs
class UserModificationMixin(UserManagementMixin):
    """Mixin pour les vues de modification d'utilisateurs"""
    pass


class UserListView(UserManagementMixin, ListView):
    """Liste des utilisateurs - SuperAdmin uniquement"""
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('role', 'username')
        
        # Filtrage par rôle
        role_filter = self.request.GET.get('role')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
            
        # Filtrage par service
        service_filter = self.request.GET.get('service')
        if service_filter:
            queryset = queryset.filter(service_id=service_filter)
            
        # Recherche
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = User.ROLE_CHOICES
        context['services'] = Service.objects.filter(actif=True)
        context['current_role'] = self.request.GET.get('role', '')
        context['current_service'] = self.request.GET.get('service', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class UserDetailView(UserManagementMixin, DetailView):
    """Détail d'un utilisateur - Admin uniquement"""
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_obj = self.get_object()
        
        # Informations sur les permissions
        context['permissions_info'] = {
            'peut_voir_tableau_bord': user_obj.peut_voir_tableau_bord(),
            'peut_voir_demandes': user_obj.peut_voir_demandes(),
            'peut_creer_demandes': user_obj.peut_creer_demandes(),
            'peut_valider_demandes': user_obj.peut_valider_demandes(),
            'peut_voir_banques': user_obj.peut_voir_banques(),
            'peut_gerer_banques': user_obj.peut_gerer_banques(),
            'peut_voir_recettes': user_obj.peut_voir_recettes(),
            'peut_voir_releves': user_obj.peut_voir_releves(),
            'peut_voir_etats': user_obj.peut_voir_etats(),
            'peut_gérer_clotures': user_obj.peut_gérer_clotures(),
        }
        
        return context


class UserCreateView(UserManagementMixin, CreateView):
    """Création d'un utilisateur - Admin uniquement"""
    model = User
    template_name = 'accounts/user_form.html'
    fields = ['username', 'password', 'first_name', 'last_name', 'email', 'role', 'service']
    success_url = reverse_lazy('accounts:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un utilisateur'
        context['roles'] = User.ROLE_CHOICES
        context['services'] = Service.objects.filter(actif=True)
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            # Hasher le mot de passe
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.permissions_custom = {}  # Pas de permissions personnalisées au début
            user.save()
            
            messages.success(self.request, f"Utilisateur '{user.username}' créé avec succès (basé sur le rôle '{user.get_role_display()}')")
            return super().form_valid(form)


class UserEditView(UserModificationMixin, UpdateView):
    """Modification d'un utilisateur - Admin uniquement"""
    model = User
    template_name = 'accounts/user_form.html'
    fields = ['username', 'first_name', 'last_name', 'email', 'role', 'service', 'is_active']
    success_url = reverse_lazy('accounts:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Modifier l'utilisateur {self.get_object().username}"
        context['roles'] = User.ROLE_CHOICES
        context['services'] = Service.objects.filter(actif=True)
        context['is_edit'] = True
        context['user_obj'] = self.get_object()
        return context
    
    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            
            # Réinitialiser les permissions personnalisées si le rôle change
            old_user = User.objects.get(pk=user.pk)
            if old_user.role != user.role:
                user.permissions_custom = {}
                messages.info(self.request, f"Le rôle de '{user.username}' a été changé. Les permissions sont maintenant basées sur le nouveau rôle '{user.get_role_display()}'.")
            
            user.save()
            
            # Empêcher la désactivation de son propre compte
            if user.id == self.request.user.id and not user.is_active:
                user.is_active = True
                messages.warning(self.request, "Vous ne pouvez pas désactiver votre propre compte")
                user.save()
            else:
                messages.success(self.request, f"Utilisateur '{user.username}' modifié avec succès")
            
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la modification: {str(e)}")
            return self.form_invalid(form)


class PermissionManagementView(UserManagementMixin, TemplateView):
    """Vue de gestion des permissions - Admin uniquement"""
    template_name = 'accounts/permission_management.html'
=======
class IdentifiantsView(TemplateView):
    """Vue pour afficher les utilisateurs de la base de données (identifiants d'accès)"""
    template_name = 'accounts/identifiants.html'
>>>>>>> 5a1f2ed825b571d0531b0147150a27218e958d7a
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
<<<<<<< HEAD
        # Statistiques des utilisateurs par rôle
        users_by_role = {}
        for role_code, role_name in User.ROLE_CHOICES:
            users_by_role[role_code] = {
                'name': role_name,
                'count': User.objects.filter(role=role_code, is_active=True).count(),
                'users': User.objects.filter(role=role_code, is_active=True)
            }
        
        context['users_by_role'] = users_by_role
        
        # Services actifs
        context['services'] = Service.objects.filter(actif=True)
        
        # Statistiques générales
        context['total_users'] = User.objects.filter(is_active=True).count()
        context['inactive_users'] = User.objects.filter(is_active=False).count()
        
        return context


# ===== GESTION DES SERVICES =====

class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est un admin (ADMIN, SUPER_ADMIN)"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'SUPER_ADMIN']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Accès réservé aux administrateurs")
            return redirect('accounts:login')
        return redirect('accounts:login')


class ServiceListView(AdminRequiredMixin, ListView):
    """Liste des services - Admin uniquement"""
    model = Service
    template_name = 'accounts/service_list.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        return Service.objects.all().order_by('nom_service')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gestion des Services'
        context['total_services'] = Service.objects.count()
        context['active_services'] = Service.objects.filter(actif=True).count()
        context['inactive_services'] = Service.objects.filter(actif=False).count()
        return context


class ServiceCreateView(AdminRequiredMixin, CreateView):
    """Création d'un service - Admin uniquement"""
    model = Service
    template_name = 'accounts/service_form.html'
    fields = ['nom_service', 'actif']
    success_url = reverse_lazy('accounts:service_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un Service'
        context['is_edit'] = False
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f"Service '{form.cleaned_data['nom_service']}' créé avec succès")
        return super().form_valid(form)


class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    """Modification d'un service - Admin uniquement"""
    model = Service
    template_name = 'accounts/service_form.html'
    fields = ['nom_service', 'actif']
    success_url = reverse_lazy('accounts:service_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Modifier le Service {self.get_object().nom_service}"
        context['is_edit'] = True
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f"Service '{form.cleaned_data['nom_service']}' modifié avec succès")
        return super().form_valid(form)


class ServiceToggleView(AdminRequiredMixin, UpdateView):
    """Activation/Désactivation d'un service - Admin uniquement"""
    model = Service
    fields = ['actif']
    
    def form_valid(self, form):
        service = form.save()
        status = "activé" if service.actif else "désactivé"
        messages.success(self.request, f"Service '{service.nom_service}' {status} avec succès")
        return redirect('accounts:service_list')
    
    def get(self, request, *args, **kwargs):
        service = self.get_object()
        service.actif = not service.actif
        service.save()
        status = "activé" if service.actif else "désactivé"
        messages.success(request, f"Service '{service.nom_service}' {status} avec succès")
        return redirect('accounts:service_list')


=======
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
>>>>>>> 5a1f2ed825b571d0531b0147150a27218e958d7a
