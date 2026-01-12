"""
Script pour importer les données de dépenses dans le modèle Depense
Usage:
    python import_depenses_data.py                    # Lit depuis stdin
    python import_depenses_data.py < fichier.txt      # Lit depuis un fichier
    python import_depenses_data.py --file fichier.txt # Lit depuis un fichier
"""
import os
import sys
import django
import re
from decimal import Decimal
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.utils import timezone
from demandes.models import Depense, NomenclatureDepense
from banques.models import Banque

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

def import_depenses(data=None):
    """Importe les dépenses depuis les données"""
    # Lire les données
    if data is None:
        # Lire depuis stdin
        if not sys.stdin.isatty():
            data = sys.stdin.read()
        else:
            print("❌ Aucune donnée fournie. Utilisez:")
            print("   python import_depenses_data.py < fichier.txt")
            print("   ou")
            print("   python import_depenses_data.py --file fichier.txt")
            return

    lines = data.strip().split('\n')
    # Ignorer l'en-tête
    if lines[0].startswith('CODE DEPENSE'):
        lines = lines[1:]

    total_imported = 0
    total_errors = 0

    print("="*60)
    print("📥 Importation des dépenses...")
    print("="*60)

    for line_num, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        try:
            # Parser la ligne (format tab-separated)
            parts = line.split('\t')
            if len(parts) < 10:
                # Essayer avec des espaces multiples comme séparateur
                parts = re.split(r'\s{2,}', line)
            
            if len(parts) < 10:
                print(f"⚠️  Ligne {line_num}: Format invalide (moins de 10 colonnes) - IGNORÉE")
                total_errors += 1
                continue

            code_depense = parts[0].strip()
            mois_str = parts[1].strip()
            annee_str = parts[2].strip()
            date_str = parts[3].strip()
            article_littera = parts[4].strip()
            libelle_depenses = parts[5].strip()
            banque_nom = parts[6].strip()
            montant_fc_str = parts[7].strip()
            montant_usd_str = parts[8].strip()
            observation = parts[9].strip() if len(parts) > 9 else ''

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

            montant_fc = parse_amount(montant_fc_str)
            montant_usd = parse_amount(montant_usd_str)

            # Si les deux montants sont à zéro, ignorer
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
                print(f"⚠️  Ligne {line_num}: Erreur lors de la création/récupération de la banque '{banque_nom}': {e}")
                # Continuer sans banque

            # Récupérer la nomenclature
            nomenclature = None
            try:
                if article_littera:
                    try:
                        nomenclature = NomenclatureDepense.objects.get(
                            article_littera=article_littera
                        )
                    except NomenclatureDepense.DoesNotExist:
                        nomenclature, _ = NomenclatureDepense.objects.get_or_create(
                            article_littera=article_littera,
                            defaults={
                                'libelle_article': libelle_depenses[:200] if libelle_depenses else article_littera,
                                'code_compte': '',
                                'libelle_compte_principal': '',
                                'actif': True
                            }
                        )
            except Exception as e:
                print(f"⚠️  Ligne {line_num}: Erreur lors de la création/récupération de la nomenclature '{article_littera}': {e}")
                # Continuer sans nomenclature

            # Créer la dépense
            try:
                depense = Depense.objects.create(
                    code_depense=code_depense,
                    mois=mois,
                    annee=annee,
                    date_depense=date_obj,
                    article_littera=article_littera,
                    nomenclature=nomenclature,
                    libelle_depenses=libelle_depenses,
                    banque=banque,
                    montant_fc=montant_fc,
                    montant_usd=montant_usd,
                    observation=observation
                )
                
                total_imported += 1
                print(f"✓ Créé: {depense.code_depense} - {libelle_depenses[:50]} - {montant_fc} CDF / {montant_usd} USD")
            except Exception as e:
                # Erreur lors de la création de la dépense
                raise Exception(f"Impossible de créer la dépense: {e}")

        except Exception as e:
            total_errors += 1
            print(f"❌ Erreur ligne {line_num}: {e} - LIGNE IGNORÉE, CONTINUATION...")
            # Continuer avec la ligne suivante
            continue

    print("="*60)
    print(f"✅ Import terminé!")
    print(f"   - Dépenses créées: {total_imported}")
    print(f"   - Erreurs: {total_errors}")
    print("="*60)

if __name__ == '__main__':
    # Vérifier les arguments de ligne de commande
    data = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--data' and len(sys.argv) > 2:
            data = sys.argv[2]
        elif sys.argv[1] == '--file' and len(sys.argv) > 2:
            with open(sys.argv[2], 'r', encoding='utf-8') as f:
                data = f.read()
        else:
            print("Usage:")
            print("  python import_depenses_data.py                    # Lit depuis stdin")
            print("  python import_depenses_data.py < fichier.txt     # Lit depuis un fichier")
            print("  python import_depenses_data.py --file fichier.txt # Lit depuis un fichier")
            sys.exit(1)
    
    import_depenses(data)
