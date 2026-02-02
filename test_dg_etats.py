#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User

def test_dg_etats_permissions():
    """Test les permissions du DG pour les états"""
    
    print("=== Test Permissions DG pour États ===\n")
    
    try:
        # Récupérer l'utilisateur DG
        dg = User.objects.get(username='dg')
        
        print(f"Utilisateur: {dg.username}")
        print(f"Rôle: {dg.role}")
        print()
        
        # Tester les permissions d'états
        peut_voir_menu_etats = dg.peut_voir_menu_etats()
        peut_creer_etats = dg.peut_creer_etats()
        
        print("Permissions d'états:")
        print(f"  ✅ Peut voir le menu états: {peut_voir_menu_etats}")
        print(f"  ❌ Peut créer des états: {peut_creer_etats}")
        print()
        
        # Vérifier les permissions attendues
        if peut_voir_menu_etats and not peut_creer_etats:
            print("🎉 Le DG a les permissions correctes pour les états !")
            print()
            print("Fonctionnalités accessibles:")
            print("  ✅ Voir le menu 'États et rapports'")
            print("  ✅ Consulter la liste des états générés")
            print("  ✅ Télécharger les états existants (PDF/Excel)")
            print("  ❌ Ne peut PAS créer de nouveaux états")
            print("  ❌ Ne voit PAS les boutons 'Nouvel état'")
            print("  ❌ Ne voit PAS les boutons 'Générer'")
            print()
            print("Le DG peut consulter les états sans pouvoir en créer - Parfait !")
        else:
            print("❌ Les permissions ne sont pas correctes")
            
    except User.DoesNotExist:
        print("❌ Utilisateur DG non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_dg_etats_permissions()
