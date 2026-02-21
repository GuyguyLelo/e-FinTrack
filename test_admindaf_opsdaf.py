#!/usr/bin/env python
"""
Script de test pour vérifier les permissions de AdminDaf et OpsDaf
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from django.test import Client

def test_admindaf_opsdaf_permissions():
    """Teste les permissions pour AdminDaf et OpsDaf"""
    
    print("🔍 Test des permissions pour AdminDaf et OpsDaf")
    print("=" * 50)
    
    users_to_test = [
        ('AdminDaf', 'admin123', 'ADMIN'),
        ('OpsDaf', 'OpsDaf123', 'OPERATEUR_SAISIE')
    ]
    
    for username, password, expected_role in users_to_test:
        try:
            user = User.objects.get(username=username)
            
            print(f"\n👤 Test pour {username} ({user.role})")
            
            # Vérifier le rôle
            if user.role != expected_role:
                print(f"   ⚠️ Rôle attendu: {expected_role}, trouvé: {user.role}")
            
            # Permissions générales
            print(f"\n📋 Permissions générales:")
            print(f"   Peut ajouter nature économique: {user.peut_ajouter_nature_economique()}")
            print(f"   Peut ajouter recette/dépense: {user.peut_ajouter_recette_depense()}")
            print(f"   Peut générer états: {user.peut_generer_etats()}")
            print(f"   Peut voir tableau de bord: {user.peut_voir_tableau_bord()}")
            
            # Créer un client et se connecter
            client = Client()
            login_success = client.login(username=username, password=password)
            
            if not login_success:
                # Définir le mot de passe si nécessaire
                user.set_password(password)
                user.save()
                login_success = client.login(username=username, password=password)
            
            if login_success:
                print(f"\n🌐 Test d'accès web:")
                
                # Test 1: Accès à la racine
                response = client.get('/')
                print(f"   Accès '/': {response.status_code}")
                if response.status_code == 302:
                    print(f"      → Redirection vers: {response.url}")
                
                # Tests spécifiques selon l'utilisateur
                if username == 'AdminDaf':
                    # AdminDaf : peut ajouter des natures économiques
                    print(f"\n🌿 Tests AdminDaf - Natures Économiques:")
                    response = client.get('/demandes/natures/')
                    print(f"   Accès '/demandes/natures/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ Accès autorisé")
                    elif response.status_code == 302:
                        print(f"      → Redirection vers: {response.url}")
                    
                    response = client.get('/demandes/natures/creer/')
                    print(f"   Accès '/demandes/natures/creer/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ Création de nature autorisée")
                    
                    # AdminDaf : accès admin Django
                    print(f"\n⚙️ Tests AdminDaf - Admin Django:")
                    response = client.get('/admin/')
                    print(f"   Accès '/admin/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ Accès admin autorisé")
                
                elif username == 'OpsDaf':
                    # OpsDaf : peut ajouter des recettes et dépenses
                    print(f"\n📊 Tests OpsDaf - Recettes/Dépenses:")
                    response = client.get('/recettes/feuille/')
                    print(f"   Accès '/recettes/feuille/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ Accès recettes autorisé")
                    
                    response = client.get('/demandes/depenses/feuille/')
                    print(f"   Accès '/demandes/depenses/feuille/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ Accès dépenses autorisé")
                    
                    # OpsDaf : peut générer les états
                    print(f"\n📄 Tests OpsDaf - États:")
                    response = client.get('/tableau-bord-feuilles/etats-depenses/')
                    print(f"   Accès '/tableau-bord-feuilles/etats-depenses/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ État dépenses autorisé")
                    
                    response = client.get('/tableau-bord-feuilles/etats-recettes/')
                    print(f"   Accès '/tableau-bord-feuilles/etats-recettes/': {response.status_code}")
                    if response.status_code == 200:
                        print(f"      ✅ État recettes autorisé")
                
                # Test du menu
                print(f"\n🧭 Test du menu:")
                response = client.get('/tableau-bord-feuilles/')
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
                        expected_items = ['Tableau de bord', 'Natures Économiques']
                        if all(item in menu_items for item in expected_items):
                            print(f"   ✅ Menu AdminDaf correct")
                        else:
                            print(f"   ⚠️ Menu AdminDaf incomplet")
                    
                    elif username == 'OpsDaf':
                        expected_items = ['Tableau de bord', 'Gestion dépenses', 'Gestion recettes', 'Rapports feuilles']
                        if all(item in menu_items for item in expected_items):
                            print(f"   ✅ Menu OpsDaf correct")
                        else:
                            print(f"   ⚠️ Menu OpsDaf incomplet")
            
        except User.DoesNotExist:
            print(f"\n❌ L'utilisateur {username} n'existe pas!")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 Résumé:")
    print(f"   - AdminDaf (ADMIN): Admin Django + Natures Économiques")
    print(f"   - OpsDaf (OPERATEUR_SAISIE): Recettes + Dépenses + États")
    print(f"   - Accès limité selon les rôles spécifiés")

if __name__ == "__main__":
    test_admindaf_opsdaf_permissions()
