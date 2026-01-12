"""
Commande pour supprimer tous les chèques
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from demandes.models import Cheque


class Command(BaseCommand):
    help = 'Supprime tous les chèques'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprimer sans confirmation',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Compter les chèques
        nb_cheques = Cheque.objects.count()
        
        if nb_cheques == 0:
            self.stdout.write(self.style.SUCCESS('Aucun chèque à supprimer.'))
            return
        
        self.stdout.write(self.style.WARNING('⚠️  ATTENTION : Cette opération est irréversible !'))
        self.stdout.write(f'📊 Nombre de chèques à supprimer : {nb_cheques}')
        
        # Afficher les détails des chèques
        cheques = Cheque.objects.select_related('releve_depense', 'banque', 'cree_par').all()
        self.stdout.write('\n📋 Détails des chèques à supprimer :')
        for cheque in cheques:
            self.stdout.write(
                f'   - {cheque.numero_cheque} | '
                f'Relevé: {cheque.releve_depense.numero if cheque.releve_depense else "N/A"} | '
                f'Banque: {cheque.banque.nom_banque} | '
                f'Montant CDF: {cheque.montant_cdf} | '
                f'Montant USD: {cheque.montant_usd}'
            )
        
        if not force:
            confirmation = input('\nÊtes-vous sûr de vouloir supprimer tous ces chèques ? (oui/non) : ')
            if confirmation.lower() not in ['oui', 'o', 'yes', 'y']:
                self.stdout.write(self.style.ERROR('Opération annulée.'))
                return
        
        # Supprimer dans une transaction
        with transaction.atomic():
            Cheque.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✓ {nb_cheques} chèque(s) supprimé(s)'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Suppression terminée avec succès !\n'
                f'   - {nb_cheques} chèque(s) supprimé(s)'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  Note : Les relevés de dépense associés n\'ont pas été supprimés.\n'
                '   Vous pouvez créer de nouveaux chèques pour ces relevés si nécessaire.'
            )
        )




