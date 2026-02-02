#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User

def test_dg_sans_etats():
    """Test que le DG n'a plus accès aux états"""
    
    print("=== Test DG Sans Accès États ===\n")
    
    try:
        # Récupérer l'utilisateur DG
        dg = User.objects.get(username='dg')
        
        print(f"Utilisateur: {dg.username}")
        print(f"Rôle: {dg.role}")
        print()
        
        # Tester les permissions du DG
        permissions = {
            "Tableau de bord": dg.peut_voir_tableau_bord(),
            "Voir tout sans modification": dg.peut_voir_tout_sans_modification(),
            "Valider les demandes": dg.peut_valider_demandes(),
            "Valider les dépenses": dg.peut_valider_depense(),
            "Voir les paiements": dg.peut_voir_paiements(),
            "Voir menu demandes": dg.peut_voir_menu_demandes(),
            "Voir menu paiements": dg.peut_voir_menu_paiements(),
            "Voir menu recettes": dg.peut_voir_menu_recettes(),
            "Voir menu états": dg.peut_voir_menu_etats(),  # MODIFIÉ
            "Peut créer états": dg.peut_creer_etats(),
        }
        
        print("Permissions du DG:")
        for permission, valeur in permissions.items():
            status = "✅" if valeur else "❌"
            print(f"  {status} {permission}: {valeur}")
        
        print()
        
        # Vérifier que le DG a accès à tout sauf les états
        acces_sauf_etats = all([
            permissions["Tableau de bord"],
            permissions["Voir tout sans modification"],
            permissions["Valider les demandes"],
            permissions["Valider les dépenses"],
            permissions["Voir les paiements"],
            permissions["Voir menu demandes"],
            permissions["Voir menu paiements"],
            permissions["Voir menu recettes"],
            not permissions["Voir menu états"],  # Doit être False
            not permissions["Peut créer états"],  # Doit être False
        ])
        
        if acces_sauf_etats:
            print("🎉 Le DG a un accès complet sauf les états !")
            print()
            print("Fonctionnalités accessibles:")
            print("  ✅ Tableau de bord complet")
            print("  ✅ Demandes (validation)")
            print("  ✅ Paiements (consultation)")
            print("  ✅ Recettes (consultation)")
            print("  ✅ Validation des dépenses")
            print("  ✅ Accès en lecture seule à tout")
            print()
            print("Fonctionnalités non accessibles:")
            print("  ❌ États et rapports (menu masqué)")
            print("  ❌ Création d'états (déjà bloqué)")
            print()
            print("Le DG a une vue complète de l'organisation sans les états !")
        else:
            print("❌ Les permissions ne sont pas correctes")
            
    except User.DoesNotExist:
        print("❌ Utilisateur DG non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_dg_sans_etats()
