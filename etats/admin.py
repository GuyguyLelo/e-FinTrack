from django.contrib import admin
from .models import EtatGenerique, ConfigurationEtat, HistoriqueGeneration


@admin.register(EtatGenerique)
class EtatGeneriqueAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_etat', 'date_debut', 'date_fin', 'total_general', 'statut', 'genere_par', 'date_generation']
    list_filter = ['type_etat', 'statut', 'periodicite', 'date_generation']
    search_fields = ['titre', 'description']
    readonly_fields = ['total_general', 'date_generation', 'date_modification']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'type_etat', 'description', 'statut')
        }),
        ('Période', {
            'fields': ('date_debut', 'date_fin', 'periodicite')
        }),
        ('Filtres', {
            'fields': ('services', 'natures_economiques', 'banques', 'comptes_bancaires')
        }),
        ('Montants', {
            'fields': ('total_usd', 'total_cdf', 'total_general'),
            'classes': ('collapse',)
        }),
        ('Fichiers', {
            'fields': ('fichier_pdf', 'fichier_excel')
        }),
        ('Paramètres', {
            'fields': ('filtres_supplementaires', 'parametres_affichage'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('genere_par', 'date_generation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ConfigurationEtat)
class ConfigurationEtatAdmin(admin.ModelAdmin):
    list_display = ['type_etat', 'titre_par_defaut', 'periodicite_defaut', 'actif']
    list_filter = ['type_etat', 'actif', 'periodicite_defaut']
    search_fields = ['titre_par_defaut', 'description_template']


@admin.register(HistoriqueGeneration)
class HistoriqueGenerationAdmin(admin.ModelAdmin):
    list_display = ['etat', 'action', 'utilisateur', 'date_action']
    list_filter = ['action', 'date_action']
    search_fields = ['etat__titre', 'utilisateur__username']
