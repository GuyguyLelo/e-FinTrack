#!/usr/bin/env python
"""
Script pour réinitialiser les mots de passe et résoudre les problèmes de connexion
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User

def reset_passwords():
    """Réinitialiser les mots de passe de tous les utilisateurs"""
    print("🔐 Réinitialisation des mots de passe")
    print("=" * 50)
    
    # Définition des utilisateurs et leurs mots de passe
    users_passwords = {
        'SuperAdmin': 'Super123!',
        'AdminDaf': 'Admin123!',
        'DirDaf': 'Dir123!',
        'DivDaf': 'Div123!',
        'OpsDaf': 'Ops123!',
        'Operateur': 'Oper123!',
    }
    
    print("📋 Mise à jour des mots de passe:")
    print("-" * 40)
    
    for username, password in users_passwords.items():
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_active = True  # S'assurer que l'utilisateur est actif
            user.save()
            print(f"   ✅ {username:12} -> {password}")
        except User.DoesNotExist:
            print(f"   ❌ {username:12} -> Utilisateur non trouvé")
            # Créer l'utilisateur s'il n'existe pas
            user = User.objects.create_user(
                username=username,
                password=password,
                is_active=True,
                is_superuser=(username == 'SuperAdmin')
            )
            print(f"   🔧 {username:12} -> Créé avec {password}")
    
    print()
    
    # Vérification finale
    users = User.objects.all()
    print("📊 État final des utilisateurs:")
    print("-" * 60)
    print(f"{'Username':15} | {'Actif':6} | {'SuperAdmin':9} | {'Mot de passe':15}")
    print("-" * 60)
    
    for user in users:
        if user.username in users_passwords:
            print(f"{user.username:15} | {str(user.is_active):6} | {str(user.is_superuser):9} | {users_passwords[user.username]:15}")
    
    print()
    print("🎯 Instructions de connexion:")
    print("   Utilisez ces identifiants pour vous connecter:")
    print()
    for username, password in users_passwords.items():
        print(f"   🔑 {username:12} : {password}")
    
    print()
    print("🌐 URL de connexion:")
    print("   http://127.0.0.1:8001/accounts/login/")
    print()
    print("⚠️  IMPORTANT:")
    print("   1. Redémarrez le serveur Django après cette opération")
    print("   2. Videz le cache de votre navigateur")
    print("   3. Essayez de vous connecter avec les identifiants ci-dessus")
    print("   4. Changez les mots de passe après première connexion")

def check_permissions():
    """Vérifier les permissions des utilisateurs"""
    print("\n🔍 Vérification des permissions")
    print("=" * 40)
    
    users = User.objects.all()
    for user in users:
        print(f"👤 {user.username}:")
        print(f"   - Actif: {user.is_active}")
        print(f"   - SuperAdmin: {user.is_superuser}")
        print(f"   - Rôle: {getattr(user, 'role', 'Non défini')}")
        print(f"   - Email: {user.email or 'Non défini'}")
        print()

if __name__ == "__main__":
    reset_passwords()
    check_permissions()
    
    print("✅ Opération terminée avec succès!")
    print("🚀 Redémarrez le serveur et essayez de vous connecter.")
