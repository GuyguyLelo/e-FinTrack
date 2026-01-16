from django.core.management.base import BaseCommand
from django.db import transaction
from demandes.models import DemandePaiement


class Command(BaseCommand):
    help = 'Corrige les montants incohérents des demandes de paiement'

    def handle(self, *args, **options):
        self.stdout.write('Correction des montants incohérents...')
        
        with transaction.atomic():
            demandes = DemandePaiement.objects.all()
            corrections = 0
            
            for demande in demandes:
                montant_initial = demande.montant
                deja_paye_initial = demande.montant_deja_paye
                reste_initial = demande.reste_a_payer
                
                # Correction si montant déjà payé > montant
                if deja_paye_initial > montant_initial:
                    demande.montant_deja_paye = montant_initial
                    corrections += 1
                    self.stdout.write(
                        f'Correction DEM-{demande.pk}: '
                        f'{deja_paye_initial} -> {montant_initial}'
                    )
                
                # Recalcul du reste à payer
                nouveau_reste = demande.montant - demande.montant_deja_paye
                if abs(nouveau_reste - reste_initial) > 0.01:  # Différence significative
                    demande.reste_a_payer = nouveau_reste
                    corrections += 1
                    self.stdout.write(
                        f'Reste DEM-{demande.pk}: '
                        f'{reste_initial} -> {nouveau_reste}'
                    )
                
                # Mise à jour du statut si nécessaire
                if demande.reste_a_payer <= 0 and demande.statut != 'PAYEE':
                    demande.statut = 'PAYEE'
                    demande.reste_a_payer = 0
                    corrections += 1
                    self.stdout.write(
                        f'Statut DEM-{demande.pk}: '
                        f'{demande.get_statut_display()} -> PAYEE'
                    )
                
                if corrections > 0:
                    demande.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Correction terminée! {corrections} modifications effectuées.'
            )
        )
