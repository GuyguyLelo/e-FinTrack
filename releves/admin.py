"""
Admin pour les modèles releves
"""
from django.contrib import admin
from .models import ReleveBancaire, MouvementBancaire


class MouvementBancaireInline(admin.TabularInline):
    model = MouvementBancaire
    extra = 1
    fields = ['type_mouvement', 'reference_operation', 'description', 'montant', 
             'date_operation', 'beneficiaire_ou_source']


@admin.register(ReleveBancaire)
class ReleveBancaireAdmin(admin.ModelAdmin):
    list_display = ['banque', 'compte_bancaire', 'periode_debut', 'periode_fin', 
                   'devise', 'total_recettes', 'total_depenses', 'solde_banque', 
                   'valide', 'saisi_par']
    list_filter = ['valide', 'devise', 'banque', 'periode_fin']
    search_fields = ['banque__nom_banque', 'compte_bancaire__numero_compte']
    readonly_fields = ['solde_banque', 'date_saisie', 'date_modification']
    date_hierarchy = 'periode_fin'
    inlines = [MouvementBancaireInline]


@admin.register(MouvementBancaire)
class MouvementBancaireAdmin(admin.ModelAdmin):
    list_display = ['releve', 'type_mouvement', 'montant', 'devise', 'date_operation', 
                   'beneficiaire_ou_source']
    list_filter = ['type_mouvement', 'devise', 'date_operation']
    search_fields = ['description', 'reference_operation', 'beneficiaire_ou_source']

