#!/usr/bin/env python3
"""
Script de création des commandes Django pour gérer les utilisateurs
"""

import os
import subprocess
import sys

def run_django_command(command):
    """Exécute une commande Django et retourne le résultat"""
    try:
        # Utiliser python3 avec le chemin vers manage.py
        cmd = f"python3 {os.path.join(os.getcwd(), 'manage.py')} {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def creer_commande_gestion_utilisateurs():
    """Crée une commande Django de gestion des utilisateurs"""
    
    command_code = '''from django.core.management.base import BaseCommand
from accounts.models import User, Service

class Command(BaseCommand):
    help = 'Crée et configure les utilisateurs e-FinTrack selon les permissions spécifiées'

    def handle(self, *args, **options):
        self.stdout.write("=== Gestion des utilisateurs e-FinTrack ===")
        
        # 1. Créer les services par défaut
        self.creer_services_par_defaut()
        
        # 2. Supprimer les utilisateurs existants (sauf superadmin)
        self.supprimer_utilisateurs_existants()
        
        # 3. Créer les nouveaux utilisateurs
        self.creer_utilisateurs_specifies()
        
        # 4. Vérifier les permissions
        self.verifier_permissions()
        
        self.stdout.write(self.style.SUCCESS("=== Opération terminée avec succès ==="))
        self.stdout.write("\\nRésumé des comptes créés:")
        self.stdout.write("- DirDaf: DirDaf123! (Tableau de bord uniquement)")
        self.stdout.write("- DivDaf: DivDaf123! (Tableau de bord uniquement)")
        self.stdout.write("- AdminDaf: AdminDaf123! (Admin Django + Nature économique)")
        self.stdout.write("- OpsDaf: OpsDaf123! (Recettes + Dépenses + États)")

    def creer_services_par_defaut(self):
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
                self.stdout.write(f"✓ Service créé: {nom}")
            else:
                self.stdout.write(f"○ Service existant: {nom}")

    def supprimer_utilisateurs_existants(self):
        """Supprime tous les utilisateurs sauf le superadmin"""
        self.stdout.write("\\n=== Suppression des utilisateurs existants ===")
        
        # Conserver uniquement les superutilisateurs
        superadmins = User.objects.filter(is_superuser=True)
        self.stdout.write(f"Superadmins conservés: {[u.username for u in superadmins]}")
        
        # Supprimer tous les autres utilisateurs
        autres_utilisateurs = User.objects.filter(is_superuser=False)
        count = autres_utilisateurs.count()
        
        if count > 0:
            self.stdout.write(f"Suppression de {count} utilisateur(s)...")
            autres_utilisateurs.delete()
            self.stdout.write("✓ Utilisateurs supprimés")
        else:
            self.stdout.write("○ Aucun utilisateur à supprimer")

    def creer_utilisateurs_specifies(self):
        """Crée les utilisateurs avec les permissions spécifiées"""
        self.stdout.write("\\n=== Création des utilisateurs spécifiés ===")
        
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
                    self.stdout.write(f"○ Utilisateur {user_data['username']} existe déjà")
                    continue
                
                # Récupérer le service
                try:
                    service = Service.objects.get(nom_service=user_data['service'])
                except Service.DoesNotExist:
                    self.stdout.write(f"✗ Service {user_data['service']} non trouvé pour {user_data['username']}")
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
                
                self.stdout.write(f"✓ Utilisateur créé: {user.username} ({user.get_role_display()})")
                self.stdout.write(f"  - Mot de passe: {user_data['password']}")
                self.stdout.write(f"  - Service: {service.nom_service}")
                self.stdout.write(f"  - Accès Admin Django: {'Oui' if user.is_staff else 'Non'}")
                
            except Exception as e:
                self.stdout.write(f"✗ Erreur création utilisateur {user_data['username']}: {str(e)}")

    def verifier_permissions(self):
        """Vérifie les permissions des utilisateurs créés"""
        self.stdout.write("\\n=== Vérification des permissions ===")
        
        utilisateurs = User.objects.filter(is_superuser=False).order_by('username')
        
        for user in utilisateurs:
            self.stdout.write(f"\\n{user.username} ({user.get_role_display()}):")
            self.stdout.write(f"  - Tableau de bord: {'Oui' if user.peut_voir_tableau_bord() else 'Non'}")
            self.stdout.write(f"  - Admin Django: {'Oui' if user.peut_acceder_admin_django() else 'Non'}")
            self.stdout.write(f"  - Nature économique: {'Oui' if user.peut_creer_entites_base() else 'Non'}")
            self.stdout.write(f"  - Recettes: {'Oui' if user.peut_voir_menu_recettes() else 'Non'}")
            self.stdout.write(f"  - Dépenses: {'Oui' if user.peut_voir_menu_depenses() else 'Non'}")
            self.stdout.write(f"  - États: {'Oui' if user.peut_creer_etats() else 'Non'}")
'''

    # Créer le répertoire de commandes s'il n'existe pas
    command_dir = os.path.join(os.getcwd(), 'accounts', 'management', 'commands')
    os.makedirs(command_dir, exist_ok=True)
    
    # Créer les fichiers __init__.py s'ils n'existent pas
    init_files = [
        os.path.join(os.getcwd(), 'accounts', 'management', '__init__.py'),
        os.path.join(os.getcwd(), 'accounts', 'management', 'commands', '__init__.py')
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('')
    
    # Créer le fichier de commande
    command_file = os.path.join(command_dir, 'gestion_utilisateurs.py')
    with open(command_file, 'w') as f:
        f.write(command_code)
    
    print(f"✓ Commande Django créée: {command_file}")
    return command_file

def main():
    """Fonction principale"""
    print("=== Création de la commande de gestion des utilisateurs ===")
    
    try:
        # Créer la commande Django
        command_file = creer_commande_gestion_utilisateurs()
        
        print(f"\n✓ Commande créée avec succès")
        print(f"\nPour exécuter la commande, utilisez:")
        print(f"python3 manage.py gestion_utilisateurs")
        
        # Tenter d'exécuter la commande
        print(f"\nTentative d'exécution de la commande...")
        success, stdout, stderr = run_django_command("gestion_utilisateurs")
        
        if success:
            print("✓ Commande exécutée avec succès!")
            print(stdout)
        else:
            print("✗ Erreur lors de l'exécution:")
            print(stderr)
            print("\nNote: Vous devrez peut-être installer Django et les dépendances:")
            print("pip3 install -r requirements.txt")
            print("Puis exécuter: python3 manage.py gestion_utilisateurs")
        
    except Exception as e:
        print(f"✗ Erreur: {str(e)}")

if __name__ == '__main__':
    main()
