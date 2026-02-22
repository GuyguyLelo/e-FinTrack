from django.contrib import admin
from .models import ClotureMensuelle


@admin.register(ClotureMensuelle)
class ClotureMensuelleAdmin(admin.ModelAdmin):
    list_display = [
        'mois', 'annee', 'statut', 'solde_net_fc', 'solde_net_usd', 
        'date_cloture', 'cloture_par'
    ]
    list_filter = ['statut', 'annee', 'mois']
    search_fields = ['observations']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('mois', 'annee', 'statut')
        }),
        ('Soldes d\'ouverture', {
            'fields': ('solde_ouverture_fc', 'solde_ouverture_usd')
        }),
        ('Soldes de la période', {
            'fields': (
                'total_recettes_fc', 'total_recettes_usd',
                'total_depenses_fc', 'total_depenses_usd'
            )
        }),
        ('Solde net', {
            'fields': ('solde_net_fc', 'solde_net_usd')
        }),
        ('Informations de clôture', {
            'fields': ('date_cloture', 'cloture_par', 'observations'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.statut == 'CLOTURE':
            return ['mois', 'annee', 'statut', 'solde_ouverture_fc', 'solde_ouverture_usd',
                   'total_recettes_fc', 'total_recettes_usd', 'total_depenses_fc', 
                   'total_depenses_usd', 'solde_net_fc', 'solde_net_usd', 
                   'date_cloture', 'cloture_par']
        return self.readonly_fields
