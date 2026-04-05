"""
Vues pour l'interface RBAC basée sur les modèles Django
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from django.db import models

from rbac.models_modele import PermissionModele, RoleModele
from rbac.forms_modeles import PermissionModeleForm, RoleModeleForm, RolePermissionsForm


class PermissionModeleListView(LoginRequiredMixin, ListView):
    """Liste des permissions basées sur les modèles"""
    model = PermissionModele
    template_name = 'rbac/permission_modele_list.html'
    context_object_name = 'permissions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par recherche
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(modele_django__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filtrage par modèle
        modele = self.request.GET.get('modele')
        if modele:
            queryset = queryset.filter(modele_django__icontains=modele)
        
        # Filtrage par action
        action = self.request.GET.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques
        context['total_permissions'] = PermissionModele.objects.count()
        context['total_modeles'] = PermissionModele.objects.values('modele_django').distinct().count()
        
        # Filtres
        context['modeles'] = PermissionModele.objects.values('modele_django').order_by('modele_django').distinct()
        context['actions'] = PermissionModele.objects.values_list('action', flat=True).distinct()
        
        return context


class PermissionModeleCreateView(LoginRequiredMixin, CreateView):
    """Créer une permission basée sur un modèle"""
    model = PermissionModele
    form_class = PermissionModeleForm
    template_name = 'rbac/permission_modele_form.html'
    success_url = reverse_lazy('rbac:permission_modele_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Permission '{form.instance.nom}' créée avec succès.")
        return super().form_valid(form)


class PermissionModeleUpdateView(LoginRequiredMixin, UpdateView):
    """Modifier une permission basée sur un modèle"""
    model = PermissionModele
    form_class = PermissionModeleForm
    template_name = 'rbac/permission_modele_form.html'
    success_url = reverse_lazy('rbac:permission_modele_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Permission '{form.instance.nom}' modifiée avec succès.")
        return super().form_valid(form)


class RoleModeleListView(LoginRequiredMixin, ListView):
    """Liste des rôles basés sur les modèles"""
    model = RoleModele
    template_name = 'rbac/role_modele_list.html'
    context_object_name = 'roles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('permissions_modeles')
        
        # Filtrage par recherche
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(description__icontains=search) |
                Q(code__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_roles'] = RoleModele.objects.count()
        return context


class RoleModeleCreateView(LoginRequiredMixin, CreateView):
    """Créer un rôle basé sur les modèles"""
    model = RoleModele
    form_class = RoleModeleForm
    template_name = 'rbac/role_modele_form.html'
    success_url = reverse_lazy('rbac:role_modele_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Rôle '{form.instance.nom}' créé avec succès.")
        return super().form_valid(form)


class RoleModeleUpdateView(LoginRequiredMixin, UpdateView):
    """Modifier un rôle basé sur les modèles"""
    model = RoleModele
    form_class = RoleModeleForm
    template_name = 'rbac/role_modele_form.html'
    success_url = reverse_lazy('rbac:role_modele_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Rôle '{form.instance.nom}' modifié avec succès.")
        return super().form_valid(form)


class RoleModeleDetailView(LoginRequiredMixin, DetailView):
    """Détails d'un rôle avec ses permissions"""
    model = RoleModele
    template_name = 'rbac/role_modele_detail.html'
    context_object_name = 'role'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Grouper les permissions par modèle
        permissions_by_modele = self.object.get_permissions_by_modele()
        context['permissions_by_modele'] = permissions_by_modele
        
        # Statistiques
        context['total_permissions'] = self.object.permissions_modeles.count()
        context['total_modeles'] = len(permissions_by_modele)
        
        return context


class RoleModelePermissionsView(LoginRequiredMixin, DetailView):
    """Page pour gérer les permissions d'un rôle"""
    model = RoleModele
    template_name = 'rbac/role_modele_permissions.html'
    context_object_name = 'role'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Préparer le formulaire de permissions
        context['form'] = RolePermissionsForm(role=self.object)
        
        # Grouper les permissions par modèle pour l'affichage
        permissions_by_modele = {}
        for perm in PermissionModele.objects.filter(est_active=True):
            if perm.modele_django not in permissions_by_modele:
                permissions_by_modele[perm.modele_django] = []
            permissions_by_modele[perm.modele_django].append(perm)
        
        context['permissions_by_modele'] = permissions_by_modele
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = RolePermissionsForm(role=self.object, data=request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, f"Permissions du rôle '{self.object.nom}' mises à jour.")
            return redirect('rbac:role_modele_detail', pk=self.object.pk)
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


def dashboard_rbac_modeles(request):
    """Tableau de bord du système RBAC basé sur les modèles"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Statistiques
    stats = {
        'total_permissions': PermissionModele.objects.count(),
        'total_roles': RoleModele.objects.count(),
        'total_modeles': PermissionModele.objects.values('modele_django').distinct().count(),
        'active_permissions': PermissionModele.objects.filter(est_active=True).count(),
        'active_roles': RoleModele.objects.filter(est_actif=True).count(),
    }
    
    # Permissions par modèle
    permissions_by_modele = PermissionModele.objects.values('modele_django').annotate(
        count=models.Count('id')
    ).order_by('-count')[:10]
    
    # Calculer le pourcentage pour chaque modèle
    max_count = permissions_by_modele[0]['count'] if permissions_by_modele else 1
    for item in permissions_by_modele:
        item['percentage'] = int((item['count'] / max_count) * 100)
    
    # Rôles récents
    recent_roles = RoleModele.objects.order_by('-date_creation')[:5]
    
    return render(request, 'rbac/dashboard_rbac_modeles.html', {
        'stats': stats,
        'permissions_by_modele': permissions_by_modele,
        'recent_roles': recent_roles,
    })
