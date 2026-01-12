"""
Commande pour importer les dépenses depuis des données tabulaires
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from datetime import datetime
import re

from demandes.models import Depense, NomenclatureDepense
from banques.models import Banque


class Command(BaseCommand):
    help = 'Importe les dépenses depuis des données tabulaires (format: CODE DEPENSE\tMOIS\tANNEE\tDATE\tLIBELLE DEPENSES\tBANQUE\tMONTANT EN Fc\tMONTANT EN $us\tOBSERVATION)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            type=str,
            help='Données tabulaires à importer (format tab-separated)',
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Chemin vers un fichier contenant les données',
        )

    def handle(self, *args, **options):

        # Lire les données
        data = options.get('data')
        if not data and options.get('file'):
            try:
                with open(options['file'], 'r', encoding='utf-8') as f:
                    data = f.read()
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erreur lors de la lecture du fichier: {e}')
                )
                return

        if not data:
            self.stdout.write(
                self.style.ERROR('Aucune donnée fournie. Utilisez --data ou --file')
            )
            return

        # Parser les données
        lines = data.strip().split('\n')
        if not lines:
            self.stdout.write(self.style.ERROR('Aucune ligne de données trouvée'))
            return

        # Ignorer la première ligne si c'est un en-tête
        if lines[0].startswith('CODE DEPENSE'):
            lines = lines[1:]

        total_imported = 0
        total_errors = 0
        errors = []

        for line_num, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            try:
                # Parser la ligne (format tab-separated)
                parts = line.split('\t')
                if len(parts) < 9:
                    # Essayer avec des espaces multiples comme séparateur
                    parts = re.split(r'\s{2,}', line)
                
                if len(parts) < 9:
                    errors.append(f'Ligne {line_num}: Format invalide (moins de 9 colonnes) - IGNORÉE')
                    total_errors += 1
                    self.stdout.write(
                        self.style.WARNING(f'Ligne {line_num}: Format invalide (moins de 9 colonnes) - IGNORÉE')
                    )
                    continue

                code_depense = parts[0].strip()
                mois_str = parts[1].strip()
                annee_str = parts[2].strip()
                date_str = parts[3].strip()
                libelle_depenses = parts[4].strip()
                banque_nom = parts[5].strip()
                montant_fc_str = parts[6].strip()
                montant_usd_str = parts[7].strip()
                observation = parts[8].strip() if len(parts) > 8 else ''

                # Parser le mois et l'année
                mois = None
                annee = None
                try:
                    if mois_str:
                        mois = int(mois_str)
                except (ValueError, TypeError):
                    pass
                
                try:
                    if annee_str:
                        annee = int(annee_str)
                except (ValueError, TypeError):
                    pass

                # Parser la date
                date_obj = None
                try:
                    if date_str:
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
                    elif annee and mois:
                        date_obj = datetime(int(annee), int(mois), 1).date()
                except (ValueError, TypeError):
                    pass

                # Parser les montants
                def parse_amount(amount_str):
                    """Parse un montant en supprimant les espaces et en convertissant en Decimal"""
                    if not amount_str or amount_str.strip() == '':
                        return Decimal('0.00')
                    # Supprimer les espaces et remplacer la virgule par un point
                    cleaned = amount_str.replace(' ', '').replace(',', '.')
                    try:
                        return Decimal(cleaned)
                    except:
                        return Decimal('0.00')

                montant_fc = parse_amount(montant_fc_str)
                montant_usd = parse_amount(montant_usd_str)

                # Si les deux montants sont à zéro, ignorer cette ligne
                if montant_fc == Decimal('0.00') and montant_usd == Decimal('0.00'):
                    continue

                # Récupérer ou créer la banque
                banque = None
                try:
                    if banque_nom:
                        banque, _ = Banque.objects.get_or_create(
                            nom_banque=banque_nom,
                            defaults={'active': True}
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Ligne {line_num}: Erreur banque "{banque_nom}": {e}')
                    )
                    # Continuer sans banque

                # Récupérer la nomenclature si l'année existe
                nomenclature = None
                try:
                    if annee:
                        # Chercher une nomenclature pour cette année
                        nomenclature = NomenclatureDepense.objects.filter(
                            annee=int(annee),
                            statut='EN_COURS'
                        ).order_by('-date_publication').first()
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Ligne {line_num}: Erreur nomenclature: {e}')
                    )
                    # Continuer sans nomenclature

                # Créer la dépense
                try:
                    depense = Depense.objects.create(
                        code_depense=code_depense,
                        mois=int(mois) if mois else None,
                        annee=int(annee) if annee else None,
                        date_depense=date_obj,
                        nomenclature=nomenclature,
                        libelle_depenses=libelle_depenses,
                        banque=banque,
                        montant_fc=montant_fc,
                        montant_usd=montant_usd,
                        observation=observation
                    )
                    total_imported += 1
                except Exception as e:
                    # Erreur lors de la création de la dépense
                    raise Exception(f"Impossible de créer la dépense: {e}")

            except Exception as e:
                errors.append(f'Ligne {line_num}: {str(e)}')
                total_errors += 1
                self.stdout.write(
                    self.style.ERROR(f'Erreur ligne {line_num}: {e} - LIGNE IGNORÉE, CONTINUATION...')
                )
                # Continuer avec la ligne suivante
                continue

        # Afficher le résumé
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Import terminé!\n'
                f'   - Dépenses créées: {total_imported}\n'
                f'   - Erreurs: {total_errors}'
            )
        )

        if errors:
            self.stdout.write(self.style.WARNING('\n⚠️  Erreurs rencontrées:'))
            for error in errors[:20]:  # Afficher les 20 premières erreurs
                self.stdout.write(f'   {error}')
            if len(errors) > 20:
                self.stdout.write(f'   ... et {len(errors) - 20} autres erreurs')

