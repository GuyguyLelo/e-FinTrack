"""
Vues pour l'authentification et la gestion des utilisateurs
"""
from django.contrib.auth.forms import UserCreationForm
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
from .forms import UserCreationForm, ServiceForm, UserUpdateForm


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
        
        print(f"DEBUG: User authenticated: {user is not None}")
        if user is not None and user.is_active:
            login(self.request, user)
            print(f"DEBUG: User logged in: {user.username}")
            print(f"DEBUG: User role: {user.role}")
            print(f"DEBUG: User has rbac_role: {hasattr(user, 'rbac_role')}")
            
            # Redirection intelligente selon les permissions RBAC
            if hasattr(user, 'rbac_role_modele') and user.rbac_role_modele:
                # Utilisateur avec rôle RBAC (nouveau système basé sur les modèles)
                # Vérifier si l'utilisateur a la permission de voir le tableau de bord
                if hasattr(user, 'has_permission_modele') and user.has_permission_modele('Dashboard', 'voir'):
                    return redirect('/tableau-bord-feuilles/')  # Ancien dashboard pour ceux qui ont la permission
                else:
                    return redirect('/dashboard/')  # Dashboard intelligent pour les autres
            elif hasattr(user, 'rbac_role') and user.rbac_role:
                # Utilisateur avec rôle RBAC (ancien système)
                if hasattr(user, 'has_rbac_permission') and user.has_rbac_permission('voir_tableau_bord'):
                    return redirect('/tableau-bord-feuilles/')
                else:
                    return redirect('/dashboard/')
            elif user.role == 'SUPER_ADMIN':
                return redirect('/tableau-bord-feuilles/')
            elif user.role == 'DG' or user.role == 'CD_FINANCE':
                return redirect('/tableau-bord-feuilles/')
            elif user.role == 'ADMIN':
                return redirect('/demandes/natures/')
            elif user.role in ['OPS_DAF', 'Ts']:
                return redirect('/')
            else:
                # Fallback pour tous les autres cas
                return redirect('/dashboard/')
        
        print("DEBUG: Authentication failed, calling parent")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mon profil'
        return context


class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/logout.html'
    
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:login')


# Mixins pour les permissions
class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est un admin (ADMIN, SUPER_ADMIN)"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'SUPER_ADMIN']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Accès réservé aux administrateurs")
            return redirect('accounts:login')
        return redirect('accounts:login')


class SuperAdminRequiredMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur est un super admin"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'SUPER_ADMIN'
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Accès réservé au super administrateur")
            return redirect('accounts:login')
        return redirect('accounts:login')


# Vues pour la gestion des services
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
    form_class = ServiceForm
    template_name = 'accounts/service_form.html'
    success_url = reverse_lazy('accounts:service_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un service'
        context['action'] = 'Ajouter'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Service créé avec succès')
        return super().form_valid(form)


class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    """Modification d'un service - Admin uniquement"""
    model = Service
    form_class = ServiceForm
    template_name = 'accounts/service_form.html'
    success_url = reverse_lazy('accounts:service_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier un service'
        context['action'] = 'Modifier'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Service modifié avec succès')
        return super().form_valid(form)


class ServiceDeleteView(AdminRequiredMixin, DetailView):
    """Suppression d'un service - Admin uniquement"""
    model = Service
    template_name = 'accounts/service_confirm_delete.html'
    
    def post(self, request, *args, **kwargs):
        service = self.get_object()
        service.delete()
        messages.success(request, 'Service supprimé avec succès')
        return redirect('accounts:service_list')


# Vues pour la gestion des utilisateurs
class UserManagementMixin(LoginRequiredMixin):
    """Mixin de base pour la gestion des utilisateurs"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(actif=True)
        return context


class UserModificationMixin(UserManagementMixin):
    """Mixin pour les vues de modification d'utilisateurs"""
    pass


class UserListView(SuperAdminRequiredMixin, ListView):
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
        context['title'] = 'Gestion des Utilisateurs'
        return context


class UserDetailView(SuperAdminRequiredMixin, DetailView):
    """Détails d'un utilisateur - SuperAdmin uniquement"""
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Détails de {self.object.username}'
        return context


class UserCreateView(SuperAdminRequiredMixin, CreateView):
    """Création d'un utilisateur - SuperAdmin uniquement"""
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un utilisateur'
        context['action'] = 'Ajouter'
        context['services'] = Service.objects.filter(actif=True)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Utilisateur {form.instance.username} créé avec succès')
        return super().form_valid(form)


class UserUpdateView(SuperAdminRequiredMixin, UpdateView):
    """Modification d'un utilisateur - SuperAdmin uniquement"""
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier un utilisateur'
        context['action'] = 'Modifier'
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pré-remplir le rôle RBAC actuel
        try:
            user = self.get_object()
            if user and user.rbac_role:
                kwargs['initial'] = {'rbac_role': user.rbac_role}
        except:
            pass  # Si l'objet n'existe pas encore
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f"Utilisateur '{form.instance.username}' modifié avec succès.")
        return super().form_valid(form)


class UserDeleteView(SuperAdminRequiredMixin, DetailView):
    """Suppression d'un utilisateur - SuperAdmin uniquement"""
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Empêcher la suppression de soi-même
        if user == request.user:
            messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
            return redirect('accounts:user_list')
        
        username = user.username
        user.delete()
        messages.success(request, f'Utilisateur "{username}" supprimé avec succès.')
        return redirect('accounts:user_list')
