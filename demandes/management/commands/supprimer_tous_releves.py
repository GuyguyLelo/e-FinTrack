"""
Commande pour supprimer tous les relevés de dépense et les chèques associés
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from demandes.models import ReleveDepense, Cheque


class Command(BaseCommand):
    help = 'Supprime tous les relevés de dépense et les chèques associés'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Supprimer sans confirmation',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # Compter les relevés et chèques
        nb_releves = ReleveDepense.objects.count()
        nb_cheques = Cheque.objects.count()
        
        if nb_releves == 0 and nb_cheques == 0:
            self.stdout.write(self.style.SUCCESS('Aucun relevé ou chèque à supprimer.'))
            return
        
        self.stdout.write(self.style.WARNING('⚠️  ATTENTION : Cette opération est irréversible !'))
        self.stdout.write(f'📊 Nombre de relevés à supprimer : {nb_releves}')
        self.stdout.write(f'📊 Nombre de chèques à supprimer : {nb_cheques}')
        
        if not force:
            confirmation = input('\nÊtes-vous sûr de vouloir supprimer toutes ces données ? (oui/non) : ')
            if confirmation.lower() not in ['oui', 'o', 'yes', 'y']:
                self.stdout.write(self.style.ERROR('Opération annulée.'))
                return
        
        # Supprimer dans une transaction
        with transaction.atomic():
            # Supprimer les chèques d'abord (car ils ont une relation OneToOne avec ReleveDepense)
            if nb_cheques > 0:
                Cheque.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✓ {nb_cheques} chèque(s) supprimé(s)'))
            
            # Supprimer les relevés (cela supprimera aussi les relations ManyToMany avec les demandes)
            if nb_releves > 0:
                ReleveDepense.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✓ {nb_releves} relevé(s) supprimé(s)'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Suppression terminée avec succès !\n'
                f'   - {nb_cheques} chèque(s) supprimé(s)\n'
                f'   - {nb_releves} relevé(s) supprimé(s)'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  Note : Les demandes de paiement associées n\'ont pas été supprimées.\n'
                '   Elles sont maintenant disponibles pour être incluses dans de nouveaux relevés.'
            )
        )




