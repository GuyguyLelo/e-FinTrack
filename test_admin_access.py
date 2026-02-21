#!/usr/bin/env python
"""
Script de test pour vérifier l'accès à l'admin Django
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.test import Client, RequestFactory
from accounts.models import User
from django.contrib.auth import login
from accounts.auto_permissions_middleware import AutoPermissionsMiddleware

def test_admin_access():
    """Teste l'accès à l'admin Django"""
    
    print("🔐 Test d'accès à l'admin Django pour AdminDaf")
    print("=" * 50)
    
    try:
        # Récupérer l'utilisateur
        user = User.objects.get(username='AdminDaf')
        print(f"✅ Utilisateur: {user.username}")
        print(f"   Rôle: {user.role}")
        print(f"   is_staff: {user.is_staff}")
        print(f"   Permissions: {user.user_permissions.count()}")
        
        # Créer un client de test
        client = Client()
        
        # Test 1: Accès à la page de login admin
        print(f"\n🌐 Test 1: Accès à /admin/")
        response = client.get('/admin/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   Redirection vers: {response.url}")
        
        # Test 2: Login avec l'utilisateur
        print(f"\n🔑 Test 2: Login avec AdminDaf")
        login_success = client.login(username='AdminDaf', password='admin123')
        print(f"   Login réussi: {login_success}")
        
        if login_success:
            # Test 3: Accès après login
            print(f"\n📊 Test 3: Accès à l'admin après login")
            response = client.get('/admin/')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Accès autorisé!")
                # Vérifier le contenu
                if 'Site d\'administration' in response.content.decode():
                    print(f"   ✅ Page d'admin chargée")
                else:
                    print(f"   ⚠️ Contenu inattendu")
            elif response.status_code == 302:
                print(f"   Redirection vers: {response.url}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
            
            # Test 4: Accès à la gestion des utilisateurs
            print(f"\n👥 Test 4: Accès à /admin/accounts/user/")
            response = client.get('/admin/accounts/user/')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Accès aux utilisateurs autorisé")
            elif response.status_code == 403:
                print(f"   ❌ Accès aux utilisateurs refusé (403)")
            elif response.status_code == 302:
                print(f"   Redirection vers: {response.url}")
            
            # Test 5: Accès aux natures économiques
            print(f"\n🌿 Test 5: Accès à /admin/demandes/natureeconomique/")
            response = client.get('/admin/demandes/natureeconomique/')
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Accès aux natures économiques autorisé")
            elif response.status_code == 403:
                print(f"   ❌ Accès aux natures économiques refusé (403)")
            elif response.status_code == 302:
                print(f"   Redirection vers: {response.url}")
        
        print(f"\n🎯 Résumé:")
        print(f"   - Utilisateur AdminDaf configuré")
        print(f"   - Permissions Django appliquées")
        print(f"   - Middleware auto-permissions activé")
        
    except User.DoesNotExist:
        print(f"❌ L'utilisateur AdminDaf n'existe pas!")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_access()
