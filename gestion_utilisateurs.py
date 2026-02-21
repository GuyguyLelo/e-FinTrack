#!/usr/bin/env python3
"""
Script de gestion des utilisateurs e-FinTrack
Crée et configure les utilisateurs selon les permissions spécifiées
"""

import os
import sys
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialiser Django
django.setup()

from accounts.models import User, Service

def creer_services_par_defaut():
    """Crée les services par défaut si ils n'existent pas"""
    services = {
        'DAF': 'Direction Administrative et Financière',
        'DIR_DAF': 'Direction DAF',
        'DIV_DAF': 'Division DAF',
    }
    
    for nom, description in services.items():
        service, created = Service.objects.get_or_create(
            nom_service=nom,
            defaults={'description': description}
        )
        if created:
            print(f"✓ Service créé: {nom}")
        else:
            print(f"○ Service existant: {nom}")

def supprimer_utilisateurs_existants():
    """Supprime tous les utilisateurs sauf le superadmin"""
    print("\n=== Suppression des utilisateurs existants ===")
    
    # Conserver uniquement les superutilisateurs
    superadmins = User.objects.filter(is_superuser=True)
    print(f"Superadmins conservés: {[u.username for u in superadmins]}")
    
    # Supprimer tous les autres utilisateurs
    autres_utilisateurs = User.objects.filter(is_superuser=False)
    count = autres_utilisateurs.count()
    
    if count > 0:
        print(f"Suppression de {count} utilisateur(s)...")
        autres_utilisateurs.delete()
        print("✓ Utilisateurs supprimés")
    else:
        print("○ Aucun utilisateur à supprimer")

def creer_utilisateurs_specifies():
    """Crée les utilisateurs avec les permissions spécifiées"""
    print("\n=== Création des utilisateurs spécifiés ===")
    
    utilisateurs = [
        {
            'username': 'DirDaf',
            'password': 'DirDaf123!',
            'role': 'DG',  # Directeur Général pour accès tableau de bord
            'service': 'DIR_DAF',
            'description': 'Directeur DAF - Accès tableau de bord uniquement'
        },
        {
            'username': 'DivDaf', 
            'password': 'DivDaf123!',
            'role': 'DF',  # Directeur Financier pour accès tableau de bord
            'service': 'DIV_DAF',
            'description': 'Division DAF - Accès tableau de bord uniquement'
        },
        {
            'username': 'AdminDaf',
            'password': 'AdminDaf123!',
            'role': 'ADMIN',  # Admin pour accès Django et nature économique
            'service': 'DAF',
            'description': 'Admin DAF - Admin Django et nature économique'
        },
        {
            'username': 'OpsDaf',
            'password': 'OpsDaf123!',
            'role': 'OPERATEUR_SAISIE',  # Opérateur pour recettes/dépenses/états
            'service': 'DAF',
            'description': 'Opérateur DAF - Recettes, dépenses et états'
        }
    ]
    
    for user_data in utilisateurs:
        try:
            # Vérifier si l'utilisateur existe déjà
            if User.objects.filter(username=user_data['username']).exists():
                print(f"○ Utilisateur {user_data['username']} existe déjà")
                continue
            
            # Récupérer le service
            try:
                service = Service.objects.get(nom_service=user_data['service'])
            except Service.DoesNotExist:
                print(f"✗ Service {user_data['service']} non trouvé pour {user_data['username']}")
                continue
            
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                service=service,
                email=f"{user_data['username'].lower()}@efintrack.com",
                first_name=user_data['username'],
                last_name=user_data['service'],
                is_active=True,
                is_staff=user_data['role'] == 'ADMIN'  # Admin Django
            )
            
            print(f"✓ Utilisateur créé: {user.username} ({user.get_role_display()})")
            print(f"  - Mot de passe: {user_data['password']}")
            print(f"  - Service: {service.nom_service}")
            print(f"  - Accès Admin Django: {'Oui' if user.is_staff else 'Non'}")
            
        except Exception as e:
            print(f"✗ Erreur création utilisateur {user_data['username']}: {str(e)}")

def verifier_permissions():
    """Vérifie les permissions des utilisateurs créés"""
    print("\n=== Vérification des permissions ===")
    
    utilisateurs = User.objects.filter(is_superuser=False).order_by('username')
    
    for user in utilisateurs:
        print(f"\n{user.username} ({user.get_role_display()}):")
        print(f"  - Tableau de bord: {'Oui' if user.peut_voir_tableau_bord() else 'Non'}")
        print(f"  - Admin Django: {'Oui' if user.peut_acceder_admin_django() else 'Non'}")
        print(f"  - Nature économique: {'Oui' if user.peut_creer_entites_base() else 'Non'}")
        print(f"  - Recettes: {'Oui' if user.peut_voir_menu_recettes() else 'Non'}")
        print(f"  - Dépenses: {'Oui' if user.peut_voir_menu_depenses() else 'Non'}")
        print(f"  - États: {'Oui' if user.peut_creer_etats() else 'Non'}")

def main():
    """Fonction principale"""
    print("=== Gestion des utilisateurs e-FinTrack ===")
    
    try:
        # 1. Créer les services par défaut
        creer_services_par_defaut()
        
        # 2. Supprimer les utilisateurs existants (sauf superadmin)
        supprimer_utilisateurs_existants()
        
        # 3. Créer les nouveaux utilisateurs
        creer_utilisateurs_specifies()
        
        # 4. Vérifier les permissions
        verifier_permissions()
        
        print("\n=== Opération terminée avec succès ===")
        print("\nRésumé des comptes créés:")
        print("- DirDaf: DirDaf123! (Tableau de bord uniquement)")
        print("- DivDaf: DivDaf123! (Tableau de bord uniquement)")
        print("- AdminDaf: AdminDaf123! (Admin Django + Nature économique)")
        print("- OpsDaf: OpsDaf123! (Recettes + Dépenses + États)")
        
    except Exception as e:
        print(f"✗ Erreur lors de l'exécution: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
