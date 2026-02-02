"""
Admin personnalisé pour les banques avec permissions spécifiques
"""
from django.contrib import admin
from .models import Banque, CompteBancaire


class ReadOnlyAdminMixin:
    """Mixin pour rendre les admin en lecture seule pour l'admin simple"""
    
    def has_add_permission(self, request):
        # L'admin simple peut ajouter
        if request.user.role == 'ADMIN':
            return True
        return super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        # L'admin simple peut modifier
        if request.user.role == 'ADMIN':
            return True
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # L'admin simple ne peut pas supprimer
        if request.user.role == 'ADMIN':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Banque)
class BanqueAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['nom_banque', 'code_banque', 'actif', 'date_creation']
    list_filter = ['actif']
    search_fields = ['nom_banque', 'code_banque']


@admin.register(CompteBancaire)
class CompteBancaireAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['intitule_compte', 'banque', 'devise', 'solde_courant', 'actif']
    list_filter = ['banque', 'devise', 'actif']
    search_fields = ['intitule_compte', 'banque__nom_banque']
