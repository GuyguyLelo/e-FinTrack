"""
Admin pour les modèles recettes
"""
from django.contrib import admin
from .models import Recette, SourceRecette


class ReadOnlyAdminMixin:
    """Mixin pour les permissions de l'admin simple"""
    
    def has_view_permission(self, request, obj=None):
        # L'admin simple peut voir tous les modèles
        return True
    
    def has_add_permission(self, request):
        # L'admin simple ne peut rien ajouter dans recettes
        if request.user.role == 'ADMIN':
            return False
        return super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        # L'admin simple ne peut rien modifier dans recettes
        if request.user.role == 'ADMIN':
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # L'admin simple ne peut rien supprimer
        if request.user.role == 'ADMIN':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(SourceRecette)
class SourceRecetteAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ["nom", "description"]


@admin.register(Recette)
class RecetteAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['reference', 'banque', 'compte_bancaire', 'montant_usd', 'montant_cdf', 
                   'source_recette', 'date_encaissement', 'valide', 'enregistre_par']
    list_filter = ['valide', 'source_recette', 'banque', 'date_encaissement']
    search_fields = ['reference', 'description', 'banque__nom_banque']
    readonly_fields = ['reference', 'date_creation', 'date_modification']
    date_hierarchy = 'date_encaissement'

