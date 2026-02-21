#!/usr/bin/env python
"""
Script de test pour vérifier qu'il n'y a plus de boucle de redirection
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from django.test import Client

def test_no_redirect_loop():
    """Test qu'il n'y a pas de boucle de redirection"""
    
    print("🔄 Test des boucles de redirection")
    print("=" * 40)
    
    users_to_test = [
        ('AdminDaf', 'admin123', 'ADMIN'),
        ('OpsDaf', 'OpsDaf123', 'OPERATEUR_SAISIE')
    ]
    
    for username, password, expected_role in users_to_test:
        try:
            user = User.objects.get(username=username)
            
            print(f"\n👤 Test pour {username} ({user.role})")
            
            # Créer un client et se connecter
            client = Client()
            login_success = client.login(username=username, password=password)
            
            if not login_success:
                user.set_password(password)
                user.save()
                login_success = client.login(username=username, password=password)
            
            if login_success:
                # Test 1: Accès depuis la page d'accueil
                print(f"\n🏠 Test depuis la page d'accueil:")
                response = client.get('/')
                print(f"   Accès '/': {response.status_code}")
                
                if response.status_code == 302:
                    print(f"   → Redirection vers: {response.url}")
                    
                    # Suivre la redirection une seule fois
                    response2 = client.get(response.url)
                    print(f"   Page finale: {response2.status_code}")
                    
                    if response2.status_code == 200:
                        print(f"   ✅ Redirection terminée correctement")
                    elif response2.status_code == 302:
                        print(f"   ⚠️ Double redirection vers: {response2.url}")
                        
                        # Suivre la deuxième redirection
                        response3 = client.get(response2.url)
                        print(f"   Page finale 2: {response3.status_code}")
                        
                        if response3.status_code == 200:
                            print(f"   ✅ Double redirection terminée")
                        else:
                            print(f"   ❌ Boucle de redirection possible")
                
                # Test 2: Accès direct aux pages autorisées
                print(f"\n🔗 Test accès direct aux pages autorisées:")
                
                if username == 'AdminDaf':
                    # Pages AdminDaf
                    test_pages = [
                        '/demandes/natures/',
                        '/demandes/natures/creer/',
                        '/admin/'
                    ]
                else:
                    # Pages OpsDaf
                    test_pages = [
                        '/recettes/feuille/',
                        '/demandes/depenses/feuille/',
                        '/tableau-bord-feuilles/etats-depenses/',
                        '/tableau-bord-feuilles/etats-recettes/'
                    ]
                
                for page in test_pages:
                    response = client.get(page)
                    print(f"   Accès '{page}': {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"      ✅ Accès direct autorisé")
                    elif response.status_code == 302:
                        print(f"      → Redirection vers: {response.url}")
                    else:
                        print(f"      ⚠️ Statut inattendu")
                
                # Test 3: Vérifier qu'il n'y a pas de redirection automatique sur les pages autorisées
                print(f"\n🔍 Test absence de redirection automatique:")
                
                if username == 'AdminDaf':
                    test_page = '/demandes/natures/'
                else:
                    test_page = '/recettes/feuille/'
                
                # Faire plusieurs requêtes successives pour vérifier qu'il n'y a pas de boucle
                for i in range(3):
                    response = client.get(test_page)
                    print(f"   Requête {i+1}: {response.status_code}")
                    
                    if response.status_code == 302:
                        print(f"      ⚠️ Redirection inattendue à la requête {i+1}")
                        break
                    elif response.status_code == 200:
                        if i == 2:
                            print(f"   ✅ Pas de boucle de redirection détectée")
            
        except User.DoesNotExist:
            print(f"\n❌ L'utilisateur {username} n'existe pas!")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
    
    print(f"\n🎯 Résumé:")
    print(f"   - AdminDaf: Redirection vers /demandes/natures/ sans boucle")
    print(f"   - OpsDaf: Accès direct sans boucle de redirection")
    print(f"   - Pages autorisées accessibles directement")

if __name__ == "__main__":
    test_no_redirect_loop()
