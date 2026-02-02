#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User

def test_middleware():
    """Test les permissions du middleware"""
    
    print("=== Test des permissions du middleware ===\n")
    
    # Test des différents rôles
    roles_test = [
        ('SUPER_ADMIN', 'superadmin', '/'),
        ('ADMIN', 'admin', '/admin/'),
        ('DG', 'dg', '/'),  # DG peut voir le tableau de bord
        ('DF', 'df', '/'),  # DF peut voir le tableau de bord
        ('CD_FINANCE', 'cdfinance', '/'),  # CD Finance peut voir le tableau de bord
        ('OPERATEUR_SAISIE', 'operateur', '/demandes/'),  # Ne peut pas voir tableau de bord
        ('AGENT_PAYEUR', 'payeur', '/demandes/paiements/'),  # Ne peut pas voir tableau de bord
    ]
    
    for role, username, expected_path in roles_test:
        try:
            user = User.objects.get(username=username)
            
            # Vérifier la permission de voir le tableau de bord
            peut_voir_tb = user.peut_voir_tableau_bord()
            
            print(f"Rôle: {role}")
            print(f"  Peut voir tableau de bord: {'✅' if peut_voir_tb else '❌'}")
            print(f"  Redirection attendue: {expected_path}")
            
            if role == 'OPERATEUR_SAISIE':
                print(f"  ✅ Ne doit PAS voir le tableau de bord")
            elif role == 'AGENT_PAYEUR':
                print(f"  ✅ Ne doit PAS voir le tableau de bord")
            elif peut_voir_tb:
                print(f"  ✅ Peut voir le tableau de bord")
            else:
                print(f"  ❌ Ne peut pas voir le tableau de bord")
            
            print()
            
        except User.DoesNotExist:
            print(f"❌ Utilisateur {username} non trouvé")
            print()

if __name__ == '__main__':
    test_middleware()
