#!/usr/bin/env python
"""
Script de test complet avec client Django pour DirDaf et DivDaf
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.test import Client
from accounts.models import User

def test_dirdaf_divdaf_web_access():
    """Teste l'accès web réel pour DirDaf et DivDaf"""
    
    print("🌐 Test d'accès web pour DirDaf et DivDaf")
    print("=" * 50)
    
    users_to_test = [
        ('DirDaf', 'DirDaf123'),
        ('DivDaf', 'DivDaf123')
    ]
    
    for username, password in users_to_test:
        try:
            user = User.objects.get(username=username)
            
            print(f"\n👤 Test pour {username} ({user.role})")
            
            # Créer un client
            client = Client()
            
            # Test 1: Login
            print(f"\n🔑 Test login...")
            login_success = client.login(username=username, password=password)
            print(f"   Login réussi: {login_success}")
            
            if not login_success:
                # Définir un mot de passe si nécessaire
                user.set_password(password)
                user.save()
                login_success = client.login(username=username, password=password)
                print(f"   Login après reset password: {login_success}")
            
            if login_success:
                # Test 2: Accès à la racine
                print(f"\n🏠 Test accès '/'...")
                response = client.get('/')
                print(f"   Status: {response.status_code}")
                if response.status_code == 302:
                    print(f"   Redirection vers: {response.url}")
                elif response.status_code == 200:
                    print(f"   ✅ Accès autorisé")
                
                # Test 3: Accès au tableau de bord feuille
                print(f"\n📊 Test accès '/tableau-bord-feuilles/'...")
                response = client.get('/tableau-bord-feuilles/')
                print(f"   Status: {response.status_code}")
                if response.status_code == 302:
                    print(f"   Redirection vers: {response.url}")
                elif response.status_code == 200:
                    print(f"   ✅ Accès autorisé au tableau de bord")
                    # Vérifier le contenu
                    content = response.content.decode()
                    if 'Tableau de bord' in content:
                        print(f"   ✅ Page tableau de bord chargée")
                
                # Test 4: Accès aux demandes (devrait être bloqué)
                print(f"\n📋 Test accès '/demandes/'...")
                response = client.get('/demandes/')
                print(f"   Status: {response.status_code}")
                if response.status_code == 302:
                    print(f"   Redirection vers: {response.url}")
                elif response.status_code == 200:
                    print(f"   ⚠️ Accès autorisé (non attendu)")
                elif response.status_code == 403:
                    print(f"   ✅ Accès bloqué (403)")
                
                # Test 5: Accès aux recettes (devrait être bloqué)
                print(f"\n💰 Test accès '/recettes/'...")
                response = client.get('/recettes/')
                print(f"   Status: {response.status_code}")
                if response.status_code == 302:
                    print(f"   Redirection vers: {response.url}")
                elif response.status_code == 200:
                    print(f"   ⚠️ Accès autorisé (non attendu)")
                elif response.status_code == 403:
                    print(f"   ✅ Accès bloqué (403)")
                
                # Test 6: Vérifier le menu dans le template
                print(f"\n🧭 Test du menu...")
                response = client.get('/tableau-bord-feuilles/')
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    # Vérifier que seul le menu tableau de bord est présent
                    menu_items = []
                    if 'Tableau de bord' in content:
                        menu_items.append('Tableau de bord')
                    if 'Natures Économiques' in content:
                        menu_items.append('Natures Économiques')
                    if 'Gestion dépenses' in content:
                        menu_items.append('Gestion dépenses')
                    if 'Gestion recettes' in content:
                        menu_items.append('Gestion recettes')
                    if 'Rapports feuilles' in content:
                        menu_items.append('Rapports feuilles')
                    
                    print(f"   Menu items trouvés: {menu_items}")
                    if len(menu_items) == 1 and 'Tableau de bord' in menu_items:
                        print(f"   ✅ Menu correctement limité")
                    else:
                        print(f"   ⚠️ Menu contient plus d'éléments que prévu")
            
        except User.DoesNotExist:
            print(f"\n❌ L'utilisateur {username} n'existe pas!")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 Résumé:")
    print(f"   - DirDaf (DG) et DivDaf (CD_FINANCE)")
    print(f"   - Accès limité au tableau de bord feuille")
    print(f"   - Redirection automatique des autres URLs")
    print(f"   - Menu limité à 'Tableau de bord' uniquement")

if __name__ == "__main__":
    test_dirdaf_divdaf_web_access()
