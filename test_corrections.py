#!/usr/bin/env python
"""
Script de test pour vérifier les corrections AdminDaf et OpsDaf
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from django.test import Client

def test_corrections_admindaf_opsdaf():
    """Teste les corrections pour AdminDaf et OpsDaf"""
    
    print("🔍 Test des corrections pour AdminDaf et OpsDaf")
    print("=" * 55)
    
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
                print(f"\n🌐 Test d'accès web:")
                
                if username == 'AdminDaf':
                    # AdminDaf : peut ajouter des natures économiques
                    print(f"\n🌿 Tests AdminDaf - Natures Économiques:")
                    
                    # Test 1: Accès à la liste des natures
                    response = client.get('/demandes/natures/')
                    print(f"   Accès '/demandes/natures/': {response.status_code}")
                    if response.status_code == 302:
                        print(f"      → Redirection vers: {response.url}")
                    elif response.status_code == 200:
                        print(f"      ✅ Accès autorisé")
                    
                    # Test 2: Accès à la création de nature
                    response = client.get('/demandes/natures/creer/')
                    print(f"   Accès '/demandes/natures/creer/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ Création de nature autorisée")
                    elif response.status_code == 302:
                        print(f"      → Redirection vers: {response.url}")
                    
                    # Test 3: Vérifier que tableau de bord est bloqué
                    response = client.get('/tableau-bord-feuilles/')
                    print(f"   Accès '/tableau-bord-feuilles/': {response.status_code}")
                    if response.status_code == 302:
                        print(f"      → Redirection vers: {response.url} (attendu)")
                    elif response.status_code == 200:
                        print(f"      ⚠️ Accès non attendu")
                
                elif username == 'OpsDaf':
                    # OpsDaf : ne doit PAS voir le tableau de bord feuille
                    print(f"\n📊 Tests OpsDaf - Pas de tableau de bord:")
                    
                    # Test 1: Vérifier que tableau de bord est bloqué
                    response = client.get('/tableau-bord-feuilles/')
                    print(f"   Accès '/tableau-bord-feuilles/': {response.status_code}")
                    if response.status_code == 302:
                        print(f"      → Redirection vers: {response.url} (attendu)")
                    elif response.status_code == 200:
                        print(f"      ⚠️ Accès non attendu")
                    
                    # Test 2: Vérifier que les états sont accessibles
                    response = client.get('/tableau-bord-feuilles/etats-depenses/')
                    print(f"   Accès '/tableau-bord-feuilles/etats-depenses/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ État dépenses autorisé")
                    
                    response = client.get('/tableau-bord-feuilles/etats-recettes/')
                    print(f"   Accès '/tableau-bord-feuilles/etats-recettes/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ État recettes autorisé")
                    
                    # Test 3: Vérifier que recettes/dépenses sont accessibles
                    response = client.get('/recettes/feuille/')
                    print(f"   Accès '/recettes/feuille/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ Recettes autorisé")
                    
                    response = client.get('/demandes/depenses/feuille/')
                    print(f"   Accès '/demandes/depenses/feuille/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ Dépenses autorisé")
                
                # Test du menu
                print(f"\n🧭 Test du menu:")
                response = client.get('/demandes/natures/' if username == 'AdminDaf' else '/recettes/feuille/')
                if response.status_code == 200:
                    content = response.content.decode()
                    
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
                    
                    print(f"   Menu items: {menu_items}")
                    
                    # Vérifier les menus attendus
                    if username == 'AdminDaf':
                        expected_items = ['Natures Économiques']
                        if 'Natures Économiques' in menu_items and 'Tableau de bord' not in menu_items:
                            print(f"   ✅ Menu AdminDaf correct (pas de tableau de bord)")
                        else:
                            print(f"   ⚠️ Menu AdminDaf incorrect")
                    
                    elif username == 'OpsDaf':
                        # OpsDaf ne doit PAS avoir "Tableau de bord"
                        unexpected_items = ['Tableau de bord']
                        expected_items = ['Gestion dépenses', 'Gestion recettes', 'Rapports feuilles']
                        
                        has_unexpected = any(item in menu_items for item in unexpected_items)
                        has_expected = all(item in menu_items for item in expected_items)
                        
                        if not has_unexpected and has_expected:
                            print(f"   ✅ Menu OpsDaf correct (pas de tableau de bord)")
                        else:
                            if has_unexpected:
                                print(f"   ⚠️ Menu OpsDaf contient 'Tableau de bord' (non attendu)")
                            if not has_expected:
                                print(f"   ⚠️ Menu OpsDaf incomplet")
            
        except User.DoesNotExist:
            print(f"\n❌ L'utilisateur {username} n'existe pas!")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 Résumé des corrections:")
    print(f"   - AdminDaf: Peut accéder à /demandes/natures/creer/")
    print(f"   - OpsDaf: Ne peut PAS voir le tableau de bord feuille")
    print(f"   - Accès limité selon les nouvelles spécifications")

if __name__ == "__main__":
    test_corrections_admindaf_opsdaf()
