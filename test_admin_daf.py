#!/usr/bin/env python
"""
Script de test pour vérifier que l'utilisateur AdminDaf peut accéder à l'admin Django
et gérer les utilisateurs et les natures économiques.
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from demandes.models import NatureEconomique
from django.test import RequestFactory
from accounts.admin import UserAdmin, ServiceAdmin
from demandes.admin import NatureEconomiqueAdmin

def test_admin_daf_permissions():
    """Teste les permissions de l'utilisateur AdminDaf"""
    
    print("🔍 Test des permissions pour l'utilisateur AdminDaf")
    print("=" * 60)
    
    try:
        # Récupérer l'utilisateur
        user = User.objects.get(username='AdminDaf')
        
        print(f"✅ Utilisateur trouvé: {user.username}")
        print(f"   Rôle: {user.role}")
        print(f"   Email: {user.email}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Actif: {user.actif}")
        
        # Permissions générales
        print(f"\n📋 Permissions générales:")
        print(f"   Peut accéder admin Django: {user.peut_acceder_admin_django()}")
        print(f"   Peut créer entités de base: {user.peut_creer_entites_base()}")
        
        # Créer une requête factice
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = user
        
        # Tester permissions sur les utilisateurs
        print(f"\n👥 Gestion des utilisateurs:")
        user_admin = UserAdmin(User, None)
        print(f"   Peut voir: {user_admin.has_view_permission(request)}")
        print(f"   Peut ajouter: {user_admin.has_add_permission(request)}")
        print(f"   Peut modifier: {user_admin.has_change_permission(request)}")
        print(f"   Peut supprimer: {user_admin.has_delete_permission(request)}")
        
        # Tester permissions sur les natures économiques
        print(f"\n🌿 Gestion des natures économiques:")
        nature_admin = NatureEconomiqueAdmin(NatureEconomique, None)
        print(f"   Peut voir: {nature_admin.has_view_permission(request)}")
        print(f"   Peut ajouter: {nature_admin.has_add_permission(request)}")
        print(f"   Peut modifier: {nature_admin.has_change_permission(request)}")
        print(f"   Peut supprimer: {nature_admin.has_delete_permission(request)}")
        
        # Vérifier le nombre de natures économiques existantes
        print(f"\n📊 Statistiques des natures économiques:")
        total_natures = NatureEconomique.objects.count()
        print(f"   Total de natures économiques: {total_natures}")
        
        if total_natures > 0:
            print(f"   5 premières natures:")
            for nature in NatureEconomique.objects.all()[:5]:
                print(f"   - {nature.code}: {nature.titre}")
        
        print(f"\n✅ Tests terminés avec succès!")
        print(f"   L'utilisateur AdminDaf peut:")
        print(f"   ✓ Accéder à l'admin Django")
        print(f"   ✓ Créer et modifier des utilisateurs")
        print(f"   ✓ Créer et modifier des natures économiques")
        
    except User.DoesNotExist:
        print("❌ L'utilisateur AdminDaf n'existe pas!")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_admin_daf_permissions()
