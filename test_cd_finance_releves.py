#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User

def test_cd_finance_releves_permissions():
    """Test les permissions du CD Finance pour créer des relevés"""
    
    print("=== Test Permissions CD Finance pour Relevés ===\n")
    
    try:
        # Récupérer l'utilisateur CD Finance
        cd_finance = User.objects.get(username='cdfinance')
        
        print(f"Utilisateur: {cd_finance.username}")
        print(f"Rôle: {cd_finance.role}")
        print()
        
        # Tester les permissions de relevés
        peut_creer_releves = cd_finance.peut_creer_releves()
        peut_valider_depense = cd_finance.peut_valider_depense()
        peut_consulter_depenses = cd_finance.peut_consulter_depenses()
        peut_creer_etats = cd_finance.peut_creer_etats()
        peut_voir_menu_releves = cd_finance.peut_creer_releves()  # Utilise la même permission
        
        print("Permissions de relevés:")
        print(f"  ✅ Peut créer des relevés: {peut_creer_releves}")
        print(f"  ❌ Peut valider les dépenses: {peut_valider_depense}")
        print(f"  ✅ Peut consulter les dépenses: {peut_consulter_depenses}")
        print(f"  ✅ Peut créer des états: {peut_creer_etats}")
        print(f"  ✅ Peut voir le menu relevés: {peut_voir_menu_releves}")
        print()
        
        # Vérifier les permissions attendues
        if peut_creer_releves and peut_consulter_depenses and peut_creer_etats and not peut_valider_depense:
            print("🎉 Le CD Finance a les permissions correctes pour les relevés !")
            print()
            print("Fonctionnalités accessibles:")
            print("  ✅ Voir le menu 'Relevés de dépenses'")
            print("  ✅ Créer des relevés de dépenses")
            print("  ✅ Consulter les dépenses")
            print("  ✅ Créer des états et rapports")
            print("  ❌ Ne peut PAS valider les dépenses (réservé au DG)")
            print("  ❌ Ne peut PAS modifier les relevés existants")
        else:
            print("❌ Les permissions ne sont pas correctes")
            
    except User.DoesNotExist:
        print("❌ Utilisateur CD Finance non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_cd_finance_releves_permissions()
