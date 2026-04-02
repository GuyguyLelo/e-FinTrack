#!/usr/bin/env python
"""
Script pour lister les utilisateurs et créer des mots de passe
"""
import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
django.setup()

from accounts.models import User
from django.contrib.auth.hashers import make_password

def list_users():
    """Lister tous les utilisateurs"""
    print("=== UTILISATEURS EXISTANTS ===")
    users = User.objects.all()
    
    for user in users:
        print(f"👤 {user.username}")
        print(f"   📧 Email: {user.email or 'Non renseigné'}")
        print(f"   🏷️  Rôle: {user.role}")
        print(f"   ✅ Actif: {user.is_active}")
        print(f"   👨‍💼 Staff: {user.is_staff}")
        print(f"   🦸 Superuser: {user.is_superuser}")
        print(f"   📅 Créé: {user.date_joined.strftime('%d/%m/%Y %H:%M')}")
        print("-" * 50)
    
    print(f"\n📊 Total: {users.count()} utilisateurs")

def create_passwords():
    """Créer des mots de passe par défaut pour les utilisateurs"""
    print("\n=== CRÉATION DE MOTS DE PASSE ===")
    
    # Mots de passe par défaut simples pour développement
    default_passwords = {
        'admin': 'admin123',
        'superadmin': 'superadmin123',
        'mohamed': 'mohamed123',
        'dg': 'dg123',
        'df': 'df123',
        'cdfinance': 'cdfinance123',
        'operateur': 'operateur123',
        'agent': 'agent123',
    }
    
    users_updated = 0
    
    for user in User.objects.all():
        username = user.username.lower()
        
        # Trouver un mot de passe par défaut
        password = None
        for key, pwd in default_passwords.items():
            if key in username:
                password = pwd
                break
        
        if not password:
            password = f"{username}123"  # Mot de passe par défaut
        
        # Mettre à jour le mot de passe
        user.password = make_password(password)
        user.save()
        users_updated += 1
        
        print(f"🔑 {user.username}: {password}")
    
    print(f"\n✅ {users_updated} mots de passe mis à jour")

def reset_superadmin():
    """Créer ou réinitialiser le superadmin"""
    print("\n=== CRÉATION DU SUPERADMIN ===")
    
    try:
        superadmin = User.objects.get(username='superadmin')
        print("✅ Superadmin existe déjà")
    except User.DoesNotExist:
        superadmin = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@efintrack.com',
            password='superadmin123',
            role='SUPER_ADMIN'
        )
        print("🆕 Superadmin créé")
    
    print(f"👤 Username: {superadmin.username}")
    print("🔑 Password: superadmin123")
    print("🏷️  Role: SUPER_ADMIN")

if __name__ == "__main__":
    print("🔐 GESTION DES UTILISATEURS E-FINTRACK\n")
    
    # Lister les utilisateurs
    list_users()
    
    # Créer des mots de passe
    create_passwords()
    
    # Créer le superadmin
    reset_superadmin()
    
    print("\n🎉 Opération terminée!")
    print("\n📝 RÉCAPITULATIF DES MOTS DE PASSE:")
    print("┌─────────────────┬──────────────────┐")
    print("│ Username        │ Password         │")
    print("├─────────────────┼──────────────────┤")
    print("│ superadmin      │ superadmin123    │")
    print("│ admin           │ admin123         │")
    print("│ mohamed         │ mohamed123       │")
    print("│ dg              │ dg123            │")
    print("│ df              │ df123            │")
    print("│ cdfinance       │ cdfinance123     │")
    print("│ operateur       │ operateur123     │")
    print("│ agent           │ agent123         │")
    print("└─────────────────┴──────────────────┘")
