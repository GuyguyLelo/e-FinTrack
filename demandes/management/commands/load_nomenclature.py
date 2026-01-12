"""
Commande pour charger la nomenclature des dépenses
"""
from django.core.management.base import BaseCommand
from demandes.models import NomenclatureDepense
from datetime import date


class Command(BaseCommand):
    help = 'Charge la nomenclature des dépenses (modèle simplifié)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--annee',
            type=int,
            help='Année de la nomenclature (par défaut: année actuelle)',
        )
        parser.add_argument(
            '--date-publication',
            type=str,
            help='Date de publication au format YYYY-MM-DD (par défaut: date actuelle)',
        )
        parser.add_argument(
            '--statut',
            type=str,
            choices=['EN_COURS', 'DEPASSE'],
            default='EN_COURS',
            help='Statut de la nomenclature (par défaut: EN_COURS)',
        )

    def handle(self, *args, **options):
        from datetime import datetime
        
        annee = options.get('annee') or datetime.now().year
        date_pub_str = options.get('date_publication')
        if date_pub_str:
            date_publication = datetime.strptime(date_pub_str, '%Y-%m-%d').date()
        else:
            date_publication = date.today()
        statut = options.get('statut', 'EN_COURS')
        
        nomencl, created = NomenclatureDepense.objects.get_or_create(
            annee=annee,
            date_publication=date_publication,
            defaults={
                'statut': statut
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Nomenclature créée: {annee} - {date_publication} - {nomencl.get_statut_display()}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'→ Nomenclature existante: {annee} - {date_publication} - {nomencl.get_statut_display()}'
                )
            )


