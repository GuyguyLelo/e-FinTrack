"""
Vues pour la gestion des permissions et rôles
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Role, Permission
from .forms import RoleForm, PermissionForm
from django.db import transaction


class RoleListView(LoginRequiredMixin, ListView):
    """Liste des rôles"""
    model = Role
    template_name = 'rbac/role_liste.html'
    context_object_name = 'roles'
    paginate_by = 20
    
    def get_queryset(self):
        return Role.objects.select_related().prefetch_related('permissions')


class RoleCreateView(LoginRequiredMixin, CreateView):
    """Création d'un rôle"""
    model = Role
    form_class = RoleForm
    template_name = 'rbac/role_form.html'
    success_url = reverse_lazy('rbac:role_liste')
    
    def form_valid(self, form):
        messages.success(self.request, f"Rôle '{form.instance.nom}' créé avec succès.")
        return super().form_valid(form)


class RoleUpdateView(LoginRequiredMixin, UpdateView):
    """Modification d'un rôle"""
    model = Role
    form_class = RoleForm
    template_name = 'rbac/role_form.html'
    success_url = reverse_lazy('rbac:role_liste')
    
    def form_valid(self, form):
        messages.success(self.request, f"Rôle '{form.instance.nom}' modifié avec succès.")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = f"Modifier le rôle: {self.object.nom}"
        return context


class RoleDeleteView(LoginRequiredMixin, DeleteView):
    """Suppression d'un rôle"""
    model = Role
    template_name = 'rbac/role_confirm_delete.html'
    success_url = reverse_lazy('rbac:role_liste')
    
    def delete(self, request, *args, **kwargs):
        role = self.get_object()
        if role.est_systeme:
            messages.error(request, "Impossible de supprimer un rôle système.")
            return redirect('rbac:role_liste')
        
        messages.success(request, f"Rôle '{role.nom}' supprimé avec succès.")
        return super().delete(request, *args, **kwargs)


class RoleDetailView(LoginRequiredMixin, DetailView):
    """Détails d'un rôle"""
    model = Role
    template_name = 'rbac/role_detail.html'
    context_object_name = 'role'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions_disponibles'] = Permission.objects.exclude(
            id__in=self.object.permissions.values_list('id')
        )
        return context


class PermissionListView(LoginRequiredMixin, ListView):
    """Liste des permissions"""
    model = Permission
    template_name = 'rbac/permission_liste.html'
    context_object_name = 'permissions'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = Permission.objects.all()
        module = self.request.GET.get('module')
        if module:
            queryset = queryset.filter(module=module)
        return queryset


class PermissionCreateView(LoginRequiredMixin, CreateView):
    """Création d'une permission"""
    model = Permission
    form_class = PermissionForm
    template_name = 'rbac/permission_form.html'
    success_url = reverse_lazy('rbac:permission_liste')
    
    def form_valid(self, form):
        messages.success(self.request, f"Permission '{form.instance.nom}' créée avec succès.")
        return super().form_valid(form)


class PermissionUpdateView(LoginRequiredMixin, UpdateView):
    """Modification d'une permission"""
    model = Permission
    form_class = PermissionForm
    template_name = 'rbac/permission_form.html'
    success_url = reverse_lazy('rbac:permission_liste')
    
    def form_valid(self, form):
        messages.success(self.request, f"Permission '{form.instance.nom}' modifiée avec succès.")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = f"Modifier la permission: {self.object.nom}"
        return context


class PermissionDetailView(LoginRequiredMixin, DetailView):
    """Détails d'une permission"""
    model = Permission
    template_name = 'rbac/permission_detail.html'
    context_object_name = 'permission'


class PermissionDeleteView(LoginRequiredMixin, DeleteView):
    """Suppression d'une permission"""
    model = Permission
    template_name = 'rbac/permission_confirm_delete.html'
    success_url = reverse_lazy('rbac:permission_liste')
    
    def delete(self, request, *args, **kwargs):
        permission = self.get_object()
        messages.success(request, f"Permission '{permission.nom}' supprimée avec succès.")
        return super().delete(request, *args, **kwargs)


class RolePermissionView(LoginRequiredMixin, DetailView):
    """Gestion des permissions d'un rôle"""
    model = Role
    template_name = 'rbac/role_permissions.html'
    context_object_name = 'role'
    pk_url_kwarg = 'role_id'  # Spécifier que l'URL utilise role_id au lieu de pk
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permissions_disponibles'] = Permission.objects.filter(est_active=True).exclude(
            id__in=self.object.permissions.values_list('id')
        )
        return context


class AddRolePermissionView(LoginRequiredMixin, View):
    """Ajouter une permission à un rôle"""
    
    def post(self, request, role_id, permission_id):
        role = get_object_or_404(Role, id=role_id)
        permission = get_object_or_404(Permission, id=permission_id)
        
        with transaction.atomic():
            RolePermission.objects.get_or_create(
                role=role,
                permission=permission
            )
        
        messages.success(request, f"Permission '{permission.nom}' ajoutée au rôle '{role.nom}'.")
        return redirect('rbac:role_permissions', role_id=role_id)


class AddRolePermissionView(LoginRequiredMixin, View):
    """Ajouter des permissions à un rôle"""
    
    def post(self, request, role_id):
        role = get_object_or_404(Role, id=role_id)
        permission_ids = request.POST.getlist('permissions')
        
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            # Utiliser le M2M directement
            role.permissions.add(*permissions)
            
            messages.success(request, f"{len(permissions)} permission(s) ajoutée(s) au rôle '{role.nom}'.")
        else:
            messages.warning(request, "Aucune permission sélectionnée.")
        
        return redirect('rbac:role_permissions', role_id=role_id)


class RemoveRolePermissionView(LoginRequiredMixin, View):
    """Retirer une permission d'un rôle"""
    
    def post(self, request, role_id, permission_id):
        role = get_object_or_404(Role, id=role_id)
        permission = get_object_or_404(Permission, id=permission_id)
        
        # Utiliser le M2M directement
        removed = role.permissions.remove(permission)
        
        if removed:
            messages.success(request, f"Permission '{permission.nom}' retirée du rôle '{role.nom}'.")
        else:
            messages.warning(request, f"La permission '{permission.nom}' n'était pas attribuée à ce rôle.")
        
        return redirect('rbac:role_permissions', role_id=role_id)


class CheckPermissionView(LoginRequiredMixin, View):
    """API pour vérifier les permissions"""
    
    def get(self, request):
        permission_code = request.GET.get('permission')
        user = request.user
        
        # Vérifier si l'utilisateur a un profil avec rôle
        try:
            profile = user.userprofile
            has_permission = profile.a_permission(permission_code)
        except:
            has_permission = False
        
        return JsonResponse({
            'has_permission': has_permission,
            'user': user.username,
            'permission': permission_code
        })
