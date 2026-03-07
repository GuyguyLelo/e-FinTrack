"""
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
            if user.role == 'SUPER_ADMIN':
                return redirect('/tableau-bord-feuilles/')
            elif user.role == 'DG' or user.role == 'CD_FINANCE':
                return redirect('/tableau-bord-feuilles/')
            elif user.role == 'ADMIN':
                # Admin -> toujours redirigé vers les natures économiques
                return redirect('/demandes/natures/')
            else:
                return redirect('/')
        
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
    template_name = 'accounts/service_form.html'
    fields = ['nom_service', 'description', 'actif']
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
    template_name = 'accounts/service_form.html'
    fields = ['nom_service', 'description', 'actif']
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
        context['title'] = 'Gestion des Utilisateurs'
        context['services'] = Service.objects.filter(actif=True)
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
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ajouter un utilisateur'
        context['action'] = 'Ajouter'
        context['services'] = Service.objects.filter(actif=True)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Utilisateur créé avec succès')
        return super().form_valid(form)


class UserUpdateView(SuperAdminRequiredMixin, UpdateView):
    """Modification d'un utilisateur - SuperAdmin uniquement"""
    model = User
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    fields = ['username', 'email', 'first_name', 'last_name', 'role', 'service', 'is_active', 'is_superuser']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier un utilisateur'
        context['action'] = 'Modifier'
        context['services'] = Service.objects.filter(actif=True)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Utilisateur modifié avec succès')
        return super().form_valid(form)
