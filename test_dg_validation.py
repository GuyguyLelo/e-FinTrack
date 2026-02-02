#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User

def test_dg_permissions():
    """Test les permissions de validation du DG"""
    
    print("=== Test Permissions DG pour Validation ===\n")
    
    try:
        # Récupérer l'utilisateur DG
        dg = User.objects.get(username='dg')
        
        print(f"Utilisateur: {dg.username}")
        print(f"Rôle: {dg.role}")
        print()
        
        # Tester les permissions de validation
        peut_valider_demandes = dg.peut_valider_demandes()
        peut_valider_depense = dg.peut_valider_depense()
        peut_voir_tout = dg.peut_voir_tout_sans_modification()
        peut_voir_tb = dg.peut_voir_tableau_bord()
        
        print("Permissions de validation:")
        print(f"  ✅ Peut valider les demandes: {peut_valider_demandes}")
        print(f"  ✅ Peut valider les dépenses: {peut_valider_depense}")
        print(f"  ✅ Peut voir tout sans modification: {peut_voir_tout}")
        print(f"  ✅ Peut voir le tableau de bord: {peut_voir_tb}")
        print()
        
        # Vérifier que toutes les permissions sont True
        if all([peut_valider_demandes, peut_valider_depense, peut_voir_tout, peut_voir_tb]):
            print("🎉 Le DG a toutes les permissions nécessaires !")
            print()
            print("Fonctionnalités accessibles:")
            print("  ✅ Voir le tableau de bord")
            print("  ✅ Voir toutes les demandes")
            print("  ✅ Valider les demandes en attente")
            print("  ✅ Valider les dépenses dans les relevés")
            print("  ✅ Voir les paiements")
            print("  ✅ Accès en lecture seule à toutes les données")
        else:
            print("❌ Certaines permissions manquent")
            
    except User.DoesNotExist:
        print("❌ Utilisateur DG non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_dg_permissions()
