#!/usr/bin/env python3
"""
Script de création des utilisateurs e-FinTrack
Ce script crée les utilisateurs avec les mêmes rôles et permissions
que ceux configurés dans votre environnement de développement
Version simplifiée sans modèle Service
"""

import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialisation Django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from demandes.models import NatureEconomique
from accounts.models import User

User = get_user_model()

def delete_all_users():
    """Supprime tous les utilisateurs existants"""
    print("🗑️  Suppression des utilisateurs existants...")
    
    # Compter les utilisateurs avant suppression
    total_users = User.objects.count()
    print(f"   📊 {total_users} utilisateur(s) trouvé(s)")
    
    # Supprimer tous les utilisateurs
    deleted_count = User.objects.all().delete()[0]
    print(f"   ✅ {deleted_count} utilisateur(s) supprimé(s)")

def create_groups_and_permissions():
    """Crée les groupes et permissions nécessaires"""
    print("🔧 Création des groupes et permissions...")
    
    # Création des groupes s'ils n'existent pas
    groups_data = {
        'DG': 'Direction Générale',
        'DF': 'Direction Financière', 
        'CD_FINANCE': 'Chef de Division Finance',
        'OPERATEUR_SAISIE': 'Opérateur de Saisie',
        'SUPER_ADMIN': 'Super Administrateur',
        'ADMIN': 'Administrateur DAF',
        'DIR_DAF': 'Directeur DAF',
        'DIV_DAF': 'Divisionnaire DAF',
        'OPS_DAF': 'Opérationnel DAF'
    }
    
    for group_code, group_name in groups_data.items():
        group, created = Group.objects.get_or_create(name=group_code)
        if created:
            print(f"  ✅ Groupe '{group_name}' ({group_code}) créé")
        else:
            print(f"  ℹ️  Groupe '{group_name}' ({group_code}) existe déjà")

def create_users():
    """Crée les utilisateurs avec leurs rôles (sans services)"""
    print("👥 Création des utilisateurs...")
    
    users_data = [
        {
            'username': 'AdminDaf',
            'email': 'admindaf@e-fintrack.com',
            'first_name': 'Admin',
            'last_name': 'DAF',
            'role': 'ADMIN',
            'password': 'Admin123!',
            'is_superuser': False,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'DirDaf',
            'email': 'dirdaf@e-fintrack.com',
            'first_name': 'Directeur',
            'last_name': 'DAF',
            'role': 'DIR_DAF',
            'password': 'Dir123!',
            'is_superuser': False,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'DivDaf',
            'email': 'divdaf@e-fintrack.com',
            'first_name': 'Divisionnaire',
            'last_name': 'DAF',
            'role': 'DIV_DAF',
            'password': 'Div123!',
            'is_superuser': False,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'OpsDaf',
            'email': 'opsdaf@e-fintrack.com',
            'first_name': 'Opérationnel',
            'last_name': 'DAF',
            'role': 'OPS_DAF',
            'password': 'Ops123!',
            'is_superuser': False,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'SuperAdmin',
            'email': 'superadmin@e-fintrack.com',
            'first_name': 'Super',
            'last_name': 'Admin',
            'role': 'SUPER_ADMIN',
            'password': 'Super123!',
            'is_superuser': True,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'Operateur',
            'email': 'operateur@e-fintrack.com',
            'first_name': 'Opérateur',
            'last_name': 'Saisie',
            'role': 'OPERATEUR_SAISIE',
            'password': 'Oper123!',
            'is_superuser': False,
            'is_staff': False,
            'is_active': True
        }
    ]
    
    for user_data in users_data:
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=user_data['username']).exists():
            print(f"  ⚠️  L'utilisateur '{user_data['username']}' existe déjà")
            continue
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            password=user_data['password'],
            is_superuser=user_data['is_superuser'],
            is_staff=user_data['is_staff'],
            is_active=user_data['is_active']
        )
        
        # Ajouter les permissions personnalisées si nécessaire
        if hasattr(user, 'permissions_custom'):
            user.permissions_custom = {}
            user.save()
        
        print(f"  ✅ Utilisateur '{user_data['username']}' créé avec le rôle '{user_data['role']}'")

def display_users():
    """Affiche tous les utilisateurs créés"""
    print("\n📋 Liste des utilisateurs créés:")
    print("=" * 80)
    print(f"{'Username':<15} | {'Nom':<25} | {'Rôle':<15} | {'Statut'}")
    print("-" * 80)
    
    users = User.objects.all()
    for user in users:
        full_name = f"{user.first_name} {user.last_name}"
        print(f"{user.username:<15} | {full_name:<25} | {user.role:<15} | {'Actif' if user.is_active else 'Inactif'}")
    
    print("=" * 80)
    print(f"Total: {users.count()} utilisateur(s)")

def main():
    """Fonction principale du script"""
    print("🚀 Démarrage du script de création des utilisateurs e-FinTrack")
    print("=" * 60)
    
    try:
        # Suppression des utilisateurs existants
        delete_all_users()
        
        # Création des groupes et permissions
        create_groups_and_permissions()
        
        # Création des utilisateurs
        create_users()
        
        # Affichage du résultat
        display_users()
        
        print("\n✅ Script terminé avec succès!")
        print("🔐 Vous pouvez maintenant vous connecter avec les comptes créés")
        print("\n📝 Identifiants de connexion:")
        print("   AdminDaf      : Admin123!")
        print("   DirDaf        : Dir123!")
        print("   DivDaf        : Div123!")
        print("   OpsDaf        : Ops123!")
        print("   SuperAdmin    : Super123!")
        print("   Operateur     : Oper123!")
        
        print("\n🌐 URLs d'accès:")
        print("   Application: http://127.0.0.1:8001/")
        print("   Admin Django: http://127.0.0.1:8001/admin/")
        
        print("\n⚠️  Changez ces mots de passe après première connexion!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du script: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
