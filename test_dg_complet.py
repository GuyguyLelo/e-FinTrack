#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User

def test_dg_acces_complet():
    """Test les accès complets du DG après les ajouts"""
    
    print("=== Test Accès Complet DG ===\n")
    
    try:
        # Récupérer l'utilisateur DG
        dg = User.objects.get(username='dg')
        
        print(f"Utilisateur: {dg.username}")
        print(f"Rôle: {dg.role}")
        print()
        
        # Tester toutes les permissions du DG
        permissions = {
            "Tableau de bord": dg.peut_voir_tableau_bord(),
            "Voir tout sans modification": dg.peut_voir_tout_sans_modification(),
            "Valider les demandes": dg.peut_valider_demandes(),
            "Valider les dépenses": dg.peut_valider_depense(),
            "Voir les paiements": dg.peut_voir_paiements(),
            "Voir menu demandes": dg.peut_voir_menu_demandes(),
            "Voir menu paiements": dg.peut_voir_menu_paiements(),
            "Voir menu recettes": dg.peut_voir_menu_recettes(),  # NOUVEAU
            "Voir menu états": dg.peut_voir_menu_etats(),  # NOUVEAU
            "Voir menu banques": dg.peut_voir_menu_banques(),
        }
        
        print("Permissions du DG:")
        for permission, valeur in permissions.items():
            status = "✅" if valeur else "❌"
            print(f"  {status} {permission}: {valeur}")
        
        print()
        
        # Vérifier que le DG a une vue complète
        acces_complet = all([
            permissions["Tableau de bord"],
            permissions["Voir tout sans modification"],
            permissions["Valider les demandes"],
            permissions["Valider les dépenses"],
            permissions["Voir les paiements"],
            permissions["Voir menu demandes"],
            permissions["Voir menu paiements"],
            permissions["Voir menu recettes"],  # NOUVEAU
            permissions["Voir menu états"],  # NOUVEAU
        ])
        
        if acces_complet:
            print("🎉 Le DG a un accès complet à toutes les fonctionnalités !")
            print()
            print("Fonctionnalités accessibles:")
            print("  ✅ Tableau de bord complet")
            print("  ✅ Demandes (validation)")
            print("  ✅ Paiements (consultation)")
            print("  ✅ Recettes (consultation)")  # NOUVEAU
            print("  ✅ États et rapports")  # NOUVEAU
            print("  ✅ Validation des dépenses")
            print("  ✅ Accès en lecture seule à tout")
            print()
            print("Le DG a maintenant une vue d'ensemble complète de l'organisation !")
        else:
            print("❌ Certains accès manquent pour une vue complète")
            
    except User.DoesNotExist:
        print("❌ Utilisateur DG non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_dg_acces_complet()
