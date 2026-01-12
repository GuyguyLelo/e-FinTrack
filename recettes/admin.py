"""
Admin pour les modèles recettes
"""
from django.contrib import admin
from .models import Recette


@admin.register(Recette)
class RecetteAdmin(admin.ModelAdmin):
    list_display = ['reference', 'banque', 'compte_bancaire', 'montant_usd', 'montant_cdf', 
                   'source_recette', 'date_encaissement', 'valide', 'enregistre_par']
    list_filter = ['valide', 'source_recette', 'banque', 'date_encaissement']
    search_fields = ['reference', 'description', 'banque__nom_banque']
    readonly_fields = ['reference', 'date_creation', 'date_modification']
    date_hierarchy = 'date_encaissement'

