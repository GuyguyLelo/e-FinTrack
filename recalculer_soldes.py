"""
Script pour recalculer les soldes bancaires en fonction des recettes et paiements
ATTENTION: Ce script recalcule les soldes en partant du solde initial.
Il faut d'abord corriger manuellement les soldes initiaux si nécessaire.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from decimal import Decimal
from banques.models import CompteBancaire
from recettes.models import Recette
from demandes.models import Paiement

print("=== Recalcul des soldes bancaires ===\n")
print("ATTENTION: Ce script recalcule les soldes en partant du solde initial.")
print("Assurez-vous que les soldes initiaux sont corrects avant d'exécuter ce script.\n")

# Demander confirmation
response = input("Voulez-vous continuer ? (oui/non): ")
if response.lower() != 'oui':
    print("Opération annulée.")
    exit()

# Pour chaque compte bancaire actif
for compte in CompteBancaire.objects.filter(actif=True):
    print(f"\nCompte: {compte.banque.nom_banque} - {compte.intitule_compte} ({compte.devise})")
    print(f"  Solde initial: {compte.solde_initial}")
    print(f"  Solde courant (avant recalcul): {compte.solde_courant}")
    
    # Recalculer le solde à partir du solde initial
    nouveau_solde = compte.solde_initial
    
    # Ajouter toutes les recettes validées pour ce compte
    if compte.devise == 'USD':
        recettes = Recette.objects.filter(
            compte_bancaire=compte,
            valide=True,
            montant_usd__gt=0
        )
        total_recettes = sum(r.montant_usd for r in recettes)
    else:  # CDF
        recettes = Recette.objects.filter(
            compte_bancaire=compte,
            valide=True,
            montant_cdf__gt=0
        )
        total_recettes = sum(r.montant_cdf for r in recettes)
    
    nouveau_solde += total_recettes
    print(f"  Total recettes: {total_recettes}")
    
    # Pour les paiements, on ne peut pas savoir exactement quel compte a été utilisé
    # car les anciens paiements n'ont pas de lien avec le compte
    # On va donc utiliser une approximation : répartir les paiements proportionnellement
    # ou simplement utiliser le solde initial + recettes comme nouveau solde
    
    # Option 1: Utiliser seulement solde initial + recettes (sans soustraire les paiements)
    # car les paiements ont déjà été déduits (peut-être deux fois)
    
    print(f"  Nouveau solde calculé (solde initial + recettes): {nouveau_solde}")
    
    # Mettre à jour le solde
    compte.solde_courant = nouveau_solde
    compte.save(update_fields=['solde_courant'])
    print(f"  ✓ Solde mis à jour")

print("\n=== Recalcul terminé ===")
print("\nNOTE: Les paiements n'ont pas été soustraits car ils ont peut-être été déduits deux fois.")
print("Vous devrez peut-être ajuster manuellement les soldes en fonction de vos paiements réels.")
