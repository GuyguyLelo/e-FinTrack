"""
Admin pour les modèles demandes
"""
from django.contrib import admin
from .models import DemandePaiement, ReleveDepense, NomenclatureDepense, Depense, NatureEconomique, Paiement


@admin.register(DemandePaiement)
class DemandePaiementAdmin(admin.ModelAdmin):
    list_display = ['reference', 'service_demandeur', 'nomenclature', 'nature_economique', 'montant', 
                   'montant_deja_paye', 'reste_a_payer', 'devise', 'statut', 'date_soumission', 'cree_par']
    list_filter = ['statut', 'devise', 'service_demandeur', 'date_soumission', 'nomenclature', 'nature_economique']
    search_fields = ['reference', 'description', 'service_demandeur__nom_service']
    readonly_fields = ['reference', 'date_soumission', 'date_modification', 'reste_a_payer']
    date_hierarchy = 'date_soumission'
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.pk:  # Si l'objet existe déjà
            readonly_fields.extend(['montant', 'montant_deja_paye'])
        return readonly_fields


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


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['reference', 'demande', 'releve_depense', 'montant_paye', 'devise', 
                   'date_paiement', 'paiement_par']
    list_filter = ['devise', 'date_paiement', 'releve_depense', 'paiement_par']
    search_fields = ['reference', 'demande__reference', 'demande__description', 
                   'releve_depense__periode', 'observations']
    readonly_fields = ['reference', 'date_paiement']
    date_hierarchy = 'date_paiement'
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.pk:  # Si l'objet existe déjà
            readonly_fields.extend(['demande', 'releve_depense', 'montant_paye', 'paiement_par'])
        return readonly_fields
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'demande', 'releve_depense', 'paiement_par'
        ).prefetch_related('demande__service_demandeur')

