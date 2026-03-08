#!/usr/bin/env python3
"""
Script de création des utilisateurs e-FinTrack
Ce script crée les utilisateurs avec les mêmes rôles et permissions
que ceux configurés dans votre environnement de développement
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
from accounts.models import Service, User

User = get_user_model()

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

def create_services():
    """Crée les services par défaut"""
    print("🏢 Création des services...")
    
    services_data = [
        {'nom_service': 'Direction Générale', 'description': 'Direction générale de l\'entreprise'},
        {'nom_service': 'Direction Financière', 'description': 'Direction financière et comptable'},
        {'nom_service': 'Chef Division Finance', 'description': 'Chef de division finance'},
        {'nom_service': 'Opérations', 'description': 'Service des opérations'},
        {'nom_service': 'Administration', 'description': 'Service administratif'},
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            nom_service=service_data['nom_service'],
            defaults={
                'description': service_data['description'],
                'actif': True
            }
        )
        if created:
            print(f"  ✅ Service '{service_data['nom_service']}' créé")
        else:
            print(f"  ℹ️  Service '{service_data['nom_service']}' existe déjà")

def create_users():
    """Crée les utilisateurs avec leurs rôles et services"""
    print("👥 Création des utilisateurs...")
    
    users_data = [
        {
            'username': 'AdminDaf',
            'email': 'admindaf@e-fintrack.com',
            'first_name': 'Admin',
            'last_name': 'DAF',
            'role': 'ADMIN',
            'service_code': 'Administration',
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
            'service_code': 'Direction Générale',
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
            'service_code': 'Chef Division Finance',
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
            'service_code': 'Opérations',
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
            'service_code': 'Direction Générale',
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
            'service_code': 'Opérations',
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
        
        # Récupérer le service
        try:
            service = Service.objects.get(nom_service=user_data['service_code'])
        except Service.DoesNotExist:
            print(f"  ❌ Service '{user_data['service_code']}' non trouvé pour l'utilisateur '{user_data['username']}'")
            continue
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            service=service,
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
    
    users = User.objects.all()
    for user in users:
        service_name = user.service.nom if user.service else 'Non assigné'
        print(f"👤 {user.username:<15} | {user.first_name:<10} {user.last_name:<10} | {user.role:<15} | {service_name:<20} | {'Actif' if user.is_active else 'Inactif'}")
    
    print("=" * 80)
    print(f"Total: {users.count()} utilisateur(s)")

def main():
    """Fonction principale du script"""
    print("🚀 Démarrage du script de création des utilisateurs e-FinTrack")
    print("=" * 60)
    
    try:
        # Création des groupes et services
        create_groups_and_permissions()
        create_services()
        
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
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du script: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
