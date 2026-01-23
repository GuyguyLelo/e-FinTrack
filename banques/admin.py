"""
Admin pour les modèles banques
"""
from django.contrib import admin
from .models import Banque, CompteBancaire


@admin.register(Banque)
class BanqueAdmin(admin.ModelAdmin):
    list_display = ['nom_banque', 'code_swift', 'email', 'telephone', 'active', 'date_creation']
    list_filter = ['active']
    search_fields = ['nom_banque', 'code_swift', 'email']


@admin.register(CompteBancaire)
class CompteBancaireAdmin(admin.ModelAdmin):
    list_display = ['banque', 'intitule_compte', 'numero_compte', 'devise', 'solde_courant', 'date_solde_courant', 'actif']
    list_filter = ['banque', 'devise', 'actif']
    search_fields = ['intitule_compte', 'numero_compte', 'banque__nom_banque']
    readonly_fields = ['solde_courant', 'date_solde_courant', 'date_creation', 'date_modification']

