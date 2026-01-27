"""
Commande Django pour initialiser les configurations par défaut des états
"""
from django.core.management.base import BaseCommand
from etats.models import ConfigurationEtat


class Command(BaseCommand):
    help = 'Initialise les configurations par défaut pour les types d\'états'

    def handle(self, *args, **options):
        configurations = [
            {
                'type_etat': 'DEMANDE_PAIEMENT',
                'titre_par_defaut': 'Rapport des demandes de paiement',
                'description_template': 'Rapport des demandes de paiement pour la période du {date_debut} au {date_fin}',
                'champs_affiches': ['reference', 'service', 'nature_economique', 'description', 'montant', 'devise', 'statut', 'date_soumission'],
                'filtres_disponibles': ['statut', 'devise', 'service', 'nature_economique', 'montant_min', 'montant_max'],
                'periodicite_defaut': 'MENSUEL',
            },
            {
                'type_etat': 'RECETTE',
                'titre_par_defaut': 'Rapport des recettes',
                'description_template': 'Rapport des recettes encaissées pour la période du {date_debut} au {date_fin}',
                'champs_affiches': ['reference', 'banque', 'source_recette', 'description', 'montant_usd', 'montant_cdf', 'date_encaissement'],
                'filtres_disponibles': ['source_recette', 'banque', 'compte_bancaire', 'montant_min', 'montant_max'],
                'periodicite_defaut': 'MENSUEL',
            },
            {
                'type_etat': 'DEPENSE',
                'titre_par_defaut': 'Rapport des dépenses',
                'description_template': 'Rapport des dépenses pour la période du {date_debut} au {date_fin}',
                'champs_affiches': ['code_depense', 'libelle_depenses', 'banque', 'montant_usd', 'montant_cdf', 'date_depense'],
                'filtres_disponibles': ['code_depense', 'banque', 'nomenclature', 'montant_min', 'montant_max'],
                'periodicite_defaut': 'MENSUEL',
            },
            {
                'type_etat': 'PAIEMENT',
                'titre_par_defaut': 'Rapport des paiements effectués',
                'description_template': 'Rapport des paiements effectués pour la période du {date_debut} au {date_fin}',
                'champs_affiches': ['reference', 'demande', 'montant_paye', 'devise', 'date_paiement', 'beneficiaire'],
                'filtres_disponibles': ['devise', 'montant_min', 'montant_max', 'inclure_paiements_partiels'],
                'periodicite_defaut': 'MENSUEL',
            },
            {
                'type_etat': 'RELEVE_DEPENSE',
                'titre_par_defaut': 'Rapport des relevés de dépenses',
                'description_template': 'Rapport des relevés de dépenses pour la période du {date_debut} au {date_fin}',
                'champs_affiches': ['numero', 'periode', 'net_a_payer_usd', 'net_a_payer_cdf', 'valide_par', 'date_creation'],
                'filtres_disponibles': ['valide_par', 'periode'],
                'periodicite_defaut': 'MENSUEL',
            },
            {
                'type_etat': 'SOLDE_BANCAIRE',
                'titre_par_defaut': 'État des soldes bancaires',
                'description_template': 'État des soldes bancaires au {date_fin}',
                'champs_affiches': ['banque', 'intitule_compte', 'devise', 'solde_courant', 'date_derniere_maj'],
                'filtres_disponibles': ['banque', 'compte_bancaire', 'devise'],
                'periodicite_defaut': 'JOURNALIER',
            },
            {
                'type_etat': 'Bilan',
                'titre_par_defaut': 'Bilan financier',
                'description_template': 'Bilan financier pour la période du {date_debut} au {date_fin}',
                'champs_affiches': ['type', 'categorie', 'montant_usd', 'montant_cdf', 'pourcentage'],
                'filtres_disponibles': ['type', 'categorie', 'banque'],
                'periodicite_defaut': 'MENSUEL',
            },
            {
                'type_etat': 'SITUATION_FINANCIERE',
                'titre_par_defaut': 'Situation financière',
                'description_template': 'Situation financière pour la période du {date_debut} au {date_fin}',
                'champs_affiches': ['indicateur', 'valeur_actuelle', 'valeur_precedente', 'variation'],
                'filtres_disponibles': ['indicateur', 'periode'],
                'periodicite_defaut': 'MENSUEL',
            },
        ]

        created_count = 0
        updated_count = 0

        for config_data in configurations:
            config, created = ConfigurationEtat.objects.update_or_create(
                type_etat=config_data['type_etat'],
                defaults=config_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Configuration créée: {config.get_type_etat_display()}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Configuration mise à jour: {config.get_type_etat_display()}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTerminé! {created_count} configurations créées, {updated_count} mises à jour.'
            )
        )
