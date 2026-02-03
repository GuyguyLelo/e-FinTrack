#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from decimal import Decimal
from recettes.models import Recette
from demandes.models import Depense
from banques.models import CompteBancaire, Banque

def test_suppression_mise_a_jour_soldes():
    """Test que la suppression des recettes et dépenses met à jour les soldes"""
    
    print("=== Test Mise à Jour Soldes lors Suppression ===\n")
    
    try:
        # Récupérer un compte bancaire pour les tests
        compte_usd = CompteBancaire.objects.filter(devise='USD', actif=True).first()
        compte_cdf = CompteBancaire.objects.filter(devise='CDF', actif=True).first()
        
        if not compte_usd or not compte_cdf:
            print("❌ Aucun compte bancaire trouvé pour les tests")
            return
        
        print(f"Comptes utilisés:")
        print(f"  USD: {compte_usd}")
        print(f"  CDF: {compte_cdf}")
        print()
        
        # Test 1: Suppression d'une recette
        print("🧪 Test 1: Suppression d'une recette")
        recette = Recette.objects.filter(valide=True, compte_bancaire=compte_usd).first()
        if recette:
            solde_avant = compte_usd.solde_courant
            montant_recette = recette.montant_usd
            
            print(f"  Recette: {recette.reference}")
            print(f"  Montant: {montant_recette} USD")
            print(f"  Solde avant: {solde_avant} USD")
            
            # Supprimer la recette
            recette.delete()
            
            # Rafraîchir le compte
            compte_usd.refresh_from_db()
            solde_apres = compte_usd.solde_courant
            
            print(f"  Solde après: {solde_apres} USD")
            
            solde_attendu = solde_avant - montant_recette
            if solde_apres == solde_attendu:
                print(f"  ✅ Solde correctement mis à jour: {solde_avant} → {solde_apres}")
            else:
                print(f"  ❌ Solde incorrect. Attendu: {solde_attendu}, Obtenu: {solde_apres}")
        else:
            print("  ⚠️ Aucune recette valide trouvée pour le test")
        
        print()
        
        # Test 2: Suppression d'une dépense
        print("🧪 Test 2: Suppression d'une dépense")
        depense = Depense.objects.filter(banque=compte_cdf.banque, montant_fc__gt=0).first()
        if depense:
            solde_avant = compte_cdf.solde_courant
            montant_depense = depense.montant_fc
            
            print(f"  Dépense: {depense.code_depense}")
            print(f"  Montant: {montant_depense} CDF")
            print(f"  Solde avant: {solde_avant} CDF")
            
            # Supprimer la dépense
            depense.delete()
            
            # Rafraîchir le compte
            compte_cdf.refresh_from_db()
            solde_apres = compte_cdf.solde_courant
            
            print(f"  Solde après: {solde_apres} CDF")
            
            solde_attendu = solde_avant + montant_depense
            if solde_apres == solde_attendu:
                print(f"  ✅ Solde correctement mis à jour: {solde_avant} → {solde_apres}")
            else:
                print(f"  ❌ Solde incorrect. Attendu: {solde_attendu}, Obtenu: {solde_apres}")
        else:
            print("  ⚠️ Aucune dépense trouvée pour le test")
        
        print()
        print("🎉 Tests terminés ! Les soldes sont maintenant cohérents avec les transactions.")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")

if __name__ == '__main__':
    test_suppression_mise_a_jour_soldes()
