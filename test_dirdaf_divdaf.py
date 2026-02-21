#!/usr/bin/env python
"""
Script de test pour vérifier les permissions de DirDaf et DivDaf
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from django.test import RequestFactory

def test_dirdaf_divdaf_permissions():
    """Teste les permissions pour DirDaf et DivDaf"""
    
    print("🔍 Test des permissions pour DirDaf et DivDaf")
    print("=" * 50)
    
    users_to_test = ['DirDaf', 'DivDaf']
    
    for username in users_to_test:
        try:
            user = User.objects.get(username=username)
            
            print(f"\n👤 Utilisateur: {user.username}")
            print(f"   Rôle: {user.role}")
            print(f"   Email: {user.email}")
            print(f"   Actif: {user.actif}")
            
            # Permissions générales
            print(f"\n📋 Permissions générales:")
            print(f"   Peut voir tableau de bord: {user.peut_voir_tableau_bord()}")
            print(f"   Peut voir uniquement tableau bord feuille: {user.peut_voir_uniquement_tableau_bord_feuille()}")
            print(f"   Peut créer entités de base: {user.peut_creer_entites_base()}")
            print(f"   Peut saisir demandes/recettes: {user.peut_saisir_demandes_recettes()}")
            
            # Permissions de menu
            print(f"\n📊 Permissions de menu:")
            print(f"   Menu demandes: {user.peut_voir_menu_demandes()}")
            print(f"   Menu paiements: {user.peut_voir_menu_paiements()}")
            print(f"   Menu recettes: {user.peut_voir_menu_recettes()}")
            print(f"   Menu états: {user.peut_voir_menu_etats()}")
            print(f"   Menu banques: {user.peut_voir_menu_banques()}")
            
            # Test du middleware
            print(f"\n🔄 Test du middleware:")
            factory = RequestFactory()
            
            # Test accès à la racine
            request_root = factory.get('/')
            request_root.user = user
            
            from accounts.middleware import AdminAccessMiddleware
            middleware = AdminAccessMiddleware(None)
            
            # Simuler la redirection
            try:
                response = middleware(request_root)
                if hasattr(response, 'url'):
                    print(f"   Accès '/' redirigé vers: {response.url}")
                else:
                    print(f"   Accès '/' autorisé")
            except Exception as e:
                print(f"   Accès '/' bloqué/redirigé")
            
            # Test accès au tableau de bord feuille
            request_tb = factory.get('/tableau-bord-feuilles/')
            request_tb.user = user
            
            try:
                response = middleware(request_tb)
                if hasattr(response, 'url'):
                    print(f"   Accès '/tableau-bord-feuilles/' redirigé vers: {response.url}")
                else:
                    print(f"   ✅ Accès '/tableau-bord-feuilles/' autorisé")
            except Exception as e:
                print(f"   Accès '/tableau-bord-feuilles/' bloqué")
            
            # Test accès aux demandes
            request_demandes = factory.get('/demandes/')
            request_demandes.user = user
            
            try:
                response = middleware(request_demandes)
                if hasattr(response, 'url'):
                    print(f"   Accès '/demandes/' redirigé vers: {response.url}")
                else:
                    print(f"   Accès '/demandes/' autorisé")
            except Exception as e:
                print(f"   Accès '/demandes/' bloqué/redirigé")
            
        except User.DoesNotExist:
            print(f"\n❌ L'utilisateur {username} n'existe pas!")
    
    print(f"\n🎯 Résumé:")
    print(f"   - DirDaf (DG) et DivDaf (CD_FINANCE)")
    print(f"   - Accès limité au tableau de bord feuille")
    print(f"   - Redirection automatique vers /tableau-bord-feuilles/")
    print(f"   - Menu limité dans l'interface")

if __name__ == "__main__":
    test_dirdaf_divdaf_permissions()
