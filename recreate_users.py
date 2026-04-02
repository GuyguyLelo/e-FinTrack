#!/usr/bin/env python3
"""
Script de suppression et recréation des utilisateurs e-FinTrack
Ce script supprime tous les utilisateurs existants et crée les nouveaux
en suivant exactement le modèle User défini dans accounts/models.py
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
from django.contrib.auth.models import Group
from accounts.models import Service, User

User = get_user_model()

def delete_all_users():
    """Supprime tous les utilisateurs existants sauf le superuser si nécessaire"""
    print("🗑️  Suppression des utilisateurs existants...")
    
    # Compter les utilisateurs avant suppression
    total_users = User.objects.count()
    print(f"   📊 {total_users} utilisateur(s) trouvé(s)")
    
    # Supprimer tous les utilisateurs
    deleted_count = User.objects.all().delete()[0]
    print(f"   ✅ {deleted_count} utilisateur(s) supprimé(s)")

def create_services():
    """Crée les services par défaut nécessaires pour les utilisateurs"""
    print("🏢 Création des services...")
    
    services_data = [
        {'nom_service': 'Direction Générale', 'description': 'Direction générale de la DGRAD'},
        {'nom_service': 'Direction Financière', 'description': 'Direction financière et comptable'},
        {'nom_service': 'Division Finance', 'description': 'Division finance et comptabilité'},
        {'nom_service': 'Opérations', 'description': 'Service des opérations'},
        {'nom_service': 'Administration', 'description': 'Service administratif'},
        {'nom_service': 'Paie', 'description': 'Service des paiements'},
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

def create_new_users():
    """Crée les nouveaux utilisateurs en suivant le modèle User"""
    print("👥 Création des nouveaux utilisateurs...")
    
    users_data = [
        {
            'username': 'superadmin',
            'email': 'superadmin@efintrack.cd',
            'first_name': 'Super',
            'last_name': 'Admin',
            'role': 'SUPER_ADMIN',
            'password': 'superadmin123',
            'is_superuser': True,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'admin',
            'email': 'admin@efintrack.cd',
            'first_name': 'Admin',
            'last_name': 'System',
            'role': 'ADMIN',
            'password': 'admin123',
            'is_superuser': False,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'dg',
            'email': 'dg@efintrack.cd',
            'first_name': 'Directeur',
            'last_name': 'Général',
            'role': 'DG',
            'password': 'dg123',
            'is_superuser': False,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'df',
            'email': 'df@efintrack.cd',
            'first_name': 'Directeur',
            'last_name': 'Financier',
            'role': 'DF',
            'password': 'df123',
            'is_superuser': False,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'cdfinance',
            'email': 'cdfinance@efintrack.cd',
            'first_name': 'Chef',
            'last_name': 'Division Finance',
            'role': 'CD_FINANCE',
            'password': 'cdfinance123',
            'is_superuser': False,
            'is_staff': True,
            'is_active': True
        },
        {
            'username': 'operateur',
            'email': 'operateur@efintrack.cd',
            'first_name': 'Opérateur',
            'last_name': 'Saisie',
            'role': 'OPERATEUR_SAISIE',
            'password': 'operateur123',
            'is_superuser': False,
            'is_staff': False,
            'is_active': True
        },
        {
            'username': 'payeur',
            'email': 'payeur@efintrack.cd',
            'first_name': 'Agent',
            'last_name': 'Payeur',
            'role': 'AGENT_PAYEUR',
            'password': 'payeur123',
            'is_superuser': False,
            'is_staff': False,
            'is_active': True
        }
    ]
    
    for user_data in users_data:
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
        
        print(f"  ✅ Utilisateur '{user_data['username']}' créé avec le rôle '{user_data['role']}'")

def display_users():
    """Affiche tous les utilisateurs créés avec leurs informations"""
    print("\n📋 Liste des utilisateurs créés:")
    print("=" * 80)
    print(f"{'Username':<15} | {'Nom':<25} | {'Rôle':<15} | {'Statut'}")
    print("-" * 80)
    
    users = User.objects.all().order_by('role', 'username')
    for user in users:
        full_name = f"{user.first_name} {user.last_name}"
        status = 'Actif' if user.is_active else 'Inactif'
        
        print(f"{user.username:<15} | {full_name:<25} | {user.role:<15} | {status}")
    
    print("=" * 80)
    print(f"Total: {users.count()} utilisateur(s)")

def display_permissions_summary():
    """Affiche un résumé des permissions par rôle"""
    print("\n🔐 Résumé des permissions par rôle:")
    print("=" * 80)
    
    roles = User.ROLE_CHOICES
    for role_code, role_name in roles:
        users_in_role = User.objects.filter(role=role_code)
        if users_in_role.exists():
            user = users_in_role.first()
            print(f"\n📋 {role_name} ({role_code}):")
            
            permissions = [
                ("Tableau de bord", user.peut_voir_tableau_bord()),
                ("Créer entités base", user.peut_creer_entites_base()),
                ("Voir tout sans modification", user.peut_voir_tout_sans_modification()),
                ("Valider demandes", user.peut_valider_demandes()),
                ("Effectuer paiements", user.peut_effectuer_paiements()),
                ("Créer relevés", user.peut_creer_releves()),
                ("Saisir demandes/recettes", user.peut_saisir_demandes_recettes()),
                ("Accès admin Django", user.peut_acceder_admin_django()),
            ]
            
            for perm_name, has_perm in permissions:
                status = "✅" if has_perm else "❌"
                print(f"   {status} {perm_name}")

def main():
    """Fonction principale du script"""
    print("🚀 Démarrage du script de recréation des utilisateurs e-FinTrack")
    print("=" * 60)
    
    try:
        # Étape 1: Suppression des utilisateurs existants
        delete_all_users()
        
        # Étape 2: Création des nouveaux utilisateurs
        create_new_users()
        
        # Étape 3: Affichage des résultats
        display_users()
        display_permissions_summary()
        
        print("\n✅ Script terminé avec succès!")
        print("🔐 Vous pouvez maintenant vous connecter avec les comptes créés")
        print("\n📝 Identifiants de connexion:")
        print("   superadmin    : superadmin123  (Super Admin)")
        print("   admin         : admin123       (Admin)")
        print("   dg            : dg123          (Directeur Général)")
        print("   df            : df123          (Directeur Financier)")
        print("   cdfinance     : cdfinance123   (Chef Division Finance)")
        print("   operateur     : operateur123   (Opérateur de Saisie)")
        print("   payeur        : payeur123      (Agent Payeur)")
        
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
