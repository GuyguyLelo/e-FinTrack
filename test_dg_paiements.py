#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User

def test_dg_paiements_permissions():
    """Test les permissions du DG pour les paiements"""
    
    print("=== Test Permissions DG pour Paiements ===\n")
    
    try:
        # Récupérer l'utilisateur DG
        dg = User.objects.get(username='dg')
        
        print(f"Utilisateur: {dg.username}")
        print(f"Rôle: {dg.role}")
        print()
        
        # Tester les permissions de paiements
        peut_voir_paiements = dg.peut_voir_paiements()
        peut_effectuer_paiements = dg.peut_effectuer_paiements()
        peut_voir_menu_paiements = dg.peut_voir_menu_paiements()
        
        print("Permissions de paiements:")
        print(f"  ✅ Peut voir le menu paiements: {peut_voir_menu_paiements}")
        print(f"  ✅ Peut voir les paiements: {peut_voir_paiements}")
        print(f"  ❌ Peut effectuer les paiements: {peut_effectuer_paiements}")
        print()
        
        # Vérifier les permissions attendues
        if peut_voir_paiements and peut_voir_menu_paiements and not peut_effectuer_paiements:
            print("🎉 Le DG a les permissions correctes pour les paiements !")
            print()
            print("Fonctionnalités accessibles:")
            print("  ✅ Voir le menu 'Paiements'")
            print("  ✅ Consulter la liste des paiements")
            print("  ✅ Voir les détails des paiements")
            print("  ❌ Ne peut PAS créer de paiements")
            print("  ❌ Ne voit PAS les boutons 'Nouveau paiement'")
            print("  ❌ Ne voit PAS les boutons 'Payer par relevé'")
        else:
            print("❌ Les permissions ne sont pas correctes")
            
    except User.DoesNotExist:
        print("❌ Utilisateur DG non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_dg_paiements_permissions()
