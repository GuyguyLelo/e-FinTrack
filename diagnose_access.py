#!/usr/bin/env python
"""
Script pour diagnostiquer les problèmes de connexion et d'accès
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from django.test import RequestFactory
from accounts.middleware import AdminAccessMiddleware

def diagnose_user_access():
    """Diagnostiquer les problèmes d'accès des utilisateurs"""
    print("🔍 DIAGNOSTIC DES PROBLÈMES D'ACCÈS")
    print("=" * 60)
    
    # Créer une factory de requêtes
    factory = RequestFactory()
    middleware = AdminAccessMiddleware(lambda r: None)
    
    # Test de chaque utilisateur
    users_to_test = ['SuperAdmin', 'AdminDaf', 'DirDaf', 'DivDaf', 'OpsDaf', 'Operateur']
    
    for username in users_to_test:
        print(f"\n👤 Test de l'utilisateur: {username}")
        print("-" * 40)
        
        try:
            user = User.objects.get(username=username)
            print(f"   ✅ Utilisateur trouvé: {user.username}")
            print(f"   📧 Actif: {user.is_active}")
            print(f"   👑 SuperAdmin: {user.is_superuser}")
            print(f"   🏷️  Rôle: {getattr(user, 'role', 'Non défini')}")
            
            # Tester les permissions
            print(f"   🔐 Peut voir tableau bord: {user.peut_voir_tableau_bord()}")
            print(f"   ➕ Peut ajouter nature: {user.peut_ajouter_nature_economique()}")
            print(f"   🏢 Peut accéder admin Django: {user.peut_acceder_admin_django()}")
            
            # Tester l'accès à différentes URLs
            test_urls = [
                '/',
                '/accounts/login/',
                '/demandes/depenses/feuille/creer/',
                '/tableau-bord-feuilles/',
                '/admin/',
            ]
            
            for url in test_urls:
                request = factory.get(url)
                request.user = user
                
                # Simuler le middleware
                response = middleware(request)
                
                if response and hasattr(response, 'url'):
                    if response.status_code == 302:
                        print(f"   🌐 {url:30} -> REDIRIGÉ vers {response.url}")
                    elif response.status_code == 403:
                        print(f"   🌐 {url:30} -> INTERDIT (403)")
                    else:
                        print(f"   🌐 {url:30} -> STATUT {response.status_code}")
                else:
                    print(f"   🌐 {url:30} -> AUTORISÉ")
            
        except User.DoesNotExist:
            print(f"   ❌ Utilisateur {username} non trouvé")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def check_middleware_logic():
    """Vérifier la logique du middleware"""
    print("\n🔧 ANALYSE DU MIDDLEWARE")
    print("=" * 40)
    
    print("📋 Règles du middleware AdminAccessMiddleware:")
    print("   1. ADMIN -> redirection vers /demandes/natures/")
    print("   2. DG, CD_FINANCE -> accès limité à tableau-bord-feuilles/")
    print("   3. OPERATEUR_SAISIE -> accès limité à recettes/ et demandes/depenses/feuille/")
    print("   4. AGENT_PAYEUR -> accès limité à demandes/paiements/")
    print("   5. Autres -> redirection vers /admin/ ou /accounts/login/")
    
    print("\n⚠️  PROBLÈMES IDENTIFIÉS:")
    print("   - DirDaf, DivDaf, OpsDaf ne sont ni DG ni CD_FINANCE")
    print("   - Ils sont donc redirigés vers /accounts/login/ au lieu d'accéder aux pages")
    print("   - Le middleware est trop restrictif")

def suggest_fixes():
    """Suggérer des corrections"""
    print("\n💡 SOLUTIONS PROPOSÉES:")
    print("=" * 40)
    
    print("1. 🔧 MODIFIER LE MIDDLEWARE:")
    print("   - Ajouter DIR_DAF, DIV_DAF, OPS_DAF dans les accès autorisés")
    print("   - Ou modifier la logique pour permettre l'accès base")
    
    print("\n2. 🎯 MODIFICATIONS SUGGÉRÉES:")
    print("   - Ligne 35: ajouter 'DIR_DAF', 'DIV_DAF', 'OPS_DAF'")
    print("   - Ligne 69: ajouter ces rôles dans les permissions")
    
    print("\n3. 🚀 SOLUTION RAPIDE:")
    print("   - Temporairement désactiver le middleware pour tester")
    print("   - Ou modifier les rôles des utilisateurs concernés")

if __name__ == "__main__":
    diagnose_user_access()
    check_middleware_logic()
    suggest_fixes()
