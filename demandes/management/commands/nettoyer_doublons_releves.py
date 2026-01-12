"""
Commande pour nettoyer les doublons : retirer les demandes qui sont dans plusieurs relevés
Garde la demande uniquement dans le relevé le plus récent
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from demandes.models import DemandePaiement, ReleveDepense
from django.db.models import Count


class Command(BaseCommand):
    help = 'Nettoie les doublons : retire les demandes qui sont dans plusieurs relevés, en gardant uniquement le relevé le plus récent'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui sera fait sans effectuer les modifications',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Mode DRY-RUN : aucune modification ne sera effectuée'))
        
        # Trouver les demandes dans plusieurs relevés
        doublons = DemandePaiement.objects.annotate(
            num_releves=Count('releves_depense')
        ).filter(num_releves__gt=1)
        
        total_doublons = doublons.count()
        
        if total_doublons == 0:
            self.stdout.write(self.style.SUCCESS('Aucun doublon trouvé. Tout est correct !'))
            return
        
        self.stdout.write(self.style.WARNING(f'⚠️  {total_doublons} demande(s) trouvée(s) dans plusieurs relevés'))
        
        corrections = 0
        
        with transaction.atomic():
            for demande in doublons:
                # Récupérer tous les relevés contenant cette demande, triés par date (plus récent en premier)
                releves = demande.releves_depense.all().order_by('-date_creation')
                
                if releves.count() > 1:
                    # Garder uniquement le relevé le plus récent
                    releve_a_garder = releves.first()
                    releves_a_retirer = releves[1:]
                    
                    self.stdout.write(
                        f'\n📋 Demande {demande.reference}:'
                    )
                    self.stdout.write(
                        f'   ✅ Garder dans: {releve_a_garder.numero} (créé le {releve_a_garder.date_creation.strftime("%d/%m/%Y %H:%M")})'
                    )
                    
                    for releve in releves_a_retirer:
                        self.stdout.write(
                            f'   ❌ Retirer de: {releve.numero} (créé le {releve.date_creation.strftime("%d/%m/%Y %H:%M")})'
                        )
                    
                    if not dry_run:
                        # Retirer la demande des autres relevés
                        for releve in releves_a_retirer:
                            releve.demandes.remove(demande)
                            # Recalculer les totaux du relevé
                            releve.calculer_total()
                        
                        corrections += 1
                        self.stdout.write(self.style.SUCCESS(f'   ✓ Correction effectuée'))
                    else:
                        corrections += 1
                        self.stdout.write(self.style.WARNING(f'   [DRY-RUN] Correction à effectuer'))
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n📊 Résumé DRY-RUN: {corrections} correction(s) seraient effectuée(s)'
                )
            )
            self.stdout.write(
                self.style.WARNING('Exécutez sans --dry-run pour appliquer les corrections')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ {corrections} correction(s) effectuée(s) avec succès !'
                )
            )
            self.stdout.write(
                self.style.SUCCESS('Les totaux des relevés ont été recalculés automatiquement.')
            )


