from django.core.management.base import BaseCommand
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
        self.stdout.write("\nRésumé des comptes créés:")
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
        self.stdout.write("\n=== Suppression des utilisateurs existants ===")
        
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
        self.stdout.write("\n=== Création des utilisateurs spécifiés ===")
        
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
        self.stdout.write("\n=== Vérification des permissions ===")
        
        utilisateurs = User.objects.filter(is_superuser=False).order_by('username')
        
        for user in utilisateurs:
            self.stdout.write(f"\n{user.username} ({user.get_role_display()}):")
            self.stdout.write(f"  - Tableau de bord: {'Oui' if user.peut_voir_tableau_bord() else 'Non'}")
            self.stdout.write(f"  - Admin Django: {'Oui' if user.peut_acceder_admin_django() else 'Non'}")
            self.stdout.write(f"  - Nature économique: {'Oui' if user.peut_creer_entites_base() else 'Non'}")
            self.stdout.write(f"  - Recettes: {'Oui' if user.peut_voir_menu_recettes() else 'Non'}")
            self.stdout.write(f"  - Dépenses: {'Oui' if user.peut_voir_menu_depenses() else 'Non'}")
            self.stdout.write(f"  - États: {'Oui' if user.peut_creer_etats() else 'Non'}")
