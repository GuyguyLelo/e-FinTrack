"""
Admin pour les modèles accounts
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Permission
from .models import User, Service


class ReadOnlyAdminMixin:
    """Mixin pour rendre les admin en lecture seule"""
    
    def has_view_permission(self, request, obj=None):
        # L'admin simple peut voir tous les modèles
        return True
    
    def has_add_permission(self, request):
        # L'admin simple peut ajouter seulement les modèles spécifiés
        if request.user.role == 'ADMIN':
            return self.model.__name__ in ['Service', 'Banque', 'CompteBancaire', 'NatureEconomique']
        return super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        # L'admin simple peut modifier seulement les modèles spécifiés
        if request.user.role == 'ADMIN':
            return self.model.__name__ in ['Service', 'Banque', 'CompteBancaire', 'NatureEconomique']
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # L'admin simple ne peut rien supprimer
        if request.user.role == 'ADMIN':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Service)
class ServiceAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['nom_service', 'description', 'actif', 'date_creation']
    list_filter = ['actif']
    search_fields = ['nom_service', 'description']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'service', 'actif', 'date_creation']
    list_filter = ['role', 'service', 'actif', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def has_view_permission(self, request, obj=None):
        # L'admin simple peut voir les utilisateurs (sauf super admin)
        return True
    
    def has_add_permission(self, request):
        # L'admin simple peut créer des utilisateurs
        return request.user.role in ['SUPER_ADMIN', 'ADMIN']
    
    def has_change_permission(self, request, obj=None):
        # L'admin simple peut modifier les utilisateurs
        if request.user.role == 'ADMIN' and obj and obj.role == 'SUPER_ADMIN':
            return False  # Ne peut pas modifier le super admin
        return request.user.role in ['SUPER_ADMIN', 'ADMIN']
    
    def has_delete_permission(self, request, obj=None):
        # L'admin simple ne peut pas supprimer d'utilisateurs
        return request.user.role == 'SUPER_ADMIN'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # L'admin simple ne peut pas voir le super admin
        if request.user.role == 'ADMIN':
            return qs.exclude(role='SUPER_ADMIN')
        return qs
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations DGRAD', {
            'fields': ('role', 'service', 'telephone', 'actif')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations DGRAD', {
            'fields': ('role', 'service', 'telephone', 'actif')
        }),
    )

