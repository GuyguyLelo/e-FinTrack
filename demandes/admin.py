"""
Admin pour les modèles demandes
"""
from django.contrib import admin
from .models import DemandePaiement, ReleveDepense, NomenclatureDepense, Depense, NatureEconomique


@admin.register(DemandePaiement)
class DemandePaiementAdmin(admin.ModelAdmin):
    list_display = ['reference', 'service_demandeur', 'nomenclature', 'nature_economique', 'montant', 'devise', 
                   'statut', 'date_soumission', 'cree_par']
    list_filter = ['statut', 'devise', 'service_demandeur', 'date_soumission', 'nomenclature', 'nature_economique']
    search_fields = ['reference', 'description', 'service_demandeur__nom_service']
    readonly_fields = ['reference', 'date_soumission', 'date_modification']
    date_hierarchy = 'date_soumission'


@admin.register(ReleveDepense)
class ReleveDepenseAdmin(admin.ModelAdmin):
    list_display = ['periode', 'devise', 'total', 'valide_par', 'date_validation']
    list_filter = ['devise', 'periode']
    filter_horizontal = ['demandes']


@admin.register(NomenclatureDepense)
class NomenclatureDepenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'annee', 'date_publication', 'statut']
    list_filter = ['statut', 'annee', 'date_publication']
    search_fields = ['annee']
    ordering = ['-annee', '-date_publication']
    list_editable = ['statut']
    date_hierarchy = 'date_publication'


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ['code_depense', 'date_depense', 'annee', 'mois', 'nomenclature', 'banque', 
                   'montant_fc', 'montant_usd', 'libelle_depenses']
    list_filter = ['annee', 'mois', 'banque', 'nomenclature', 'date_depense']
    search_fields = ['code_depense', 'libelle_depenses', 'observation', 'banque__nom_banque']
    readonly_fields = ['date_creation', 'date_modification']
    date_hierarchy = 'date_depense'
    ordering = ['-date_depense', '-annee', '-mois']
    list_per_page = 50


@admin.register(NatureEconomique)
class NatureEconomiqueAdmin(admin.ModelAdmin):
    list_display = ['code', 'titre', 'parent', 'description']
    list_filter = ['parent']
    search_fields = ['code', 'titre', 'description']
    ordering = ['code']
    list_select_related = ['parent']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')

