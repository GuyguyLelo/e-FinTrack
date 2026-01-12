"""
Admin pour les modèles rapprochements
"""
from django.contrib import admin
from .models import RapprochementBancaire


@admin.register(RapprochementBancaire)
class RapprochementBancaireAdmin(admin.ModelAdmin):
    list_display = ['banque', 'compte_bancaire', 'periode_mois', 'periode_annee', 
                   'devise', 'solde_banque', 'solde_interne', 'ecart', 'valide', 'observateur']
    list_filter = ['valide', 'devise', 'banque', 'periode_annee', 'periode_mois']
    search_fields = ['banque__nom_banque', 'compte_bancaire__numero_compte']
    readonly_fields = ['ecart', 'date_rapprochement', 'date_modification']
    date_hierarchy = 'date_rapprochement'

