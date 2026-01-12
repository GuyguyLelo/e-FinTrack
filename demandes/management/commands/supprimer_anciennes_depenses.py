"""
Commande pour supprimer les anciennes dépenses qui ne respectent pas la nouvelle logique
(les dépenses qui n'ont pas été créées via la validation des relevés)
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from demandes.models import Depense


class Command(BaseCommand):
    help = 'Supprime les anciennes dépenses qui ne respectent pas la nouvelle logique (non créées via validation des relevés)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprimer sans confirmation',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui sera supprimé sans effectuer la suppression',
        )

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']
        
        # Identifier les anciennes dépenses (celles qui n'ont pas "Dépense validée depuis le relevé" dans l'observation)
        anciennes_depenses = Depense.objects.filter(
            ~Q(observation__startswith='Dépense validée depuis le relevé')
        )
        
        nb_anciennes = anciennes_depenses.count()
        nb_validees = Depense.objects.filter(
            observation__startswith='Dépense validée depuis le relevé'
        ).count()
        
        if nb_anciennes == 0:
            self.stdout.write(self.style.SUCCESS('✅ Aucune ancienne dépense à supprimer. Toutes les dépenses respectent la nouvelle logique !'))
            if nb_validees > 0:
                self.stdout.write(f'📊 Nombre de dépenses validées via les relevés : {nb_validees}')
            return
        
        self.stdout.write(self.style.WARNING('⚠️  ATTENTION : Cette opération est irréversible !'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'📊 Statistiques :')
        self.stdout.write(f'   - Anciennes dépenses à supprimer : {nb_anciennes}')
        self.stdout.write(f'   - Dépenses validées via les relevés (conservées) : {nb_validees}')
        self.stdout.write('=' * 70)
        
        # Afficher un échantillon des dépenses à supprimer
        self.stdout.write('\n📋 Échantillon des anciennes dépenses à supprimer (10 premières) :')
        echantillon = anciennes_depenses[:10]
        for depense in echantillon:
            observation_preview = depense.observation[:50] if depense.observation else '(vide)'
            self.stdout.write(
                f'   - {depense.code_depense} | '
                f'{depense.libelle_depenses[:40]}... | '
                f'Observation: {observation_preview}...'
            )
        
        if nb_anciennes > 10:
            self.stdout.write(f'   ... et {nb_anciennes - 10} autres dépenses')
        
        # Calculer les totaux
        total_fc = sum(d.montant_fc for d in anciennes_depenses)
        total_usd = sum(d.montant_usd for d in anciennes_depenses)
        self.stdout.write(f'\n💰 Montants totaux des anciennes dépenses :')
        self.stdout.write(f'   - Total CDF : {total_fc:,.2f} CDF')
        self.stdout.write(f'   - Total USD : {total_usd:,.2f} USD')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 Mode DRY-RUN : aucune suppression ne sera effectuée'))
            self.stdout.write(f'   {nb_anciennes} dépense(s) seraient supprimée(s)')
            return
        
        if not force:
            self.stdout.write(self.style.WARNING('\n⚠️  Vous êtes sur le point de supprimer définitivement ces données.'))
            confirmation = input('Êtes-vous sûr de vouloir continuer ? (tapez "SUPPRIMER" pour confirmer) : ')
            if confirmation != 'SUPPRIMER':
                self.stdout.write(self.style.ERROR('❌ Opération annulée.'))
                return
        
        # Supprimer dans une transaction
        try:
            with transaction.atomic():
                # Supprimer les anciennes dépenses
                anciennes_depenses.delete()
                
                self.stdout.write(self.style.SUCCESS(f'\n✅ Suppression réussie !'))
                self.stdout.write(f'   - {nb_anciennes} ancienne(s) dépense(s) supprimée(s)')
                self.stdout.write(f'   - {nb_validees} dépense(s) validée(s) conservée(s)')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erreur lors de la suppression : {e}'))
            raise


