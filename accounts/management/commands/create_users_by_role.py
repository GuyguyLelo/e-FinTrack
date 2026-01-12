"""
Commande pour créer des utilisateurs par rôle
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Service

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée des utilisateurs de test pour chaque rôle'

    def handle(self, *args, **options):
        # Récupérer ou créer les services nécessaires
        service_dg, _ = Service.objects.get_or_create(
            nom_service='Direction Générale',
            defaults={'description': 'Direction Générale de la DGRAD', 'actif': True}
        )
        
        service_financier, _ = Service.objects.get_or_create(
            nom_service='Service Financier',
            defaults={'description': 'Service de gestion financière', 'actif': True}
        )
        
        service_comptable, _ = Service.objects.get_or_create(
            nom_service='Service Comptable',
            defaults={'description': 'Service de comptabilité', 'actif': True}
        )
        
        service_audit, _ = Service.objects.get_or_create(
            nom_service='Service Audit',
            defaults={'description': 'Service d\'audit interne', 'actif': True}
        )
        
        # Liste des utilisateurs à créer par rôle
        users_data = [
            {
                'username': 'dg',
                'email': 'dg@dgrad.cd',
                'first_name': 'Directeur',
                'last_name': 'Général',
                'role': 'DG',
                'service': service_dg,
                'password': 'dg123456',
                'is_staff': True,
            },
            {
                'username': 'daf',
                'email': 'daf@dgrad.cd',
                'first_name': 'Directeur',
                'last_name': 'Administratif et Financier',
                'role': 'DAF',
                'service': service_dg,
                'password': 'daf123456',
                'is_staff': True,
            },
            {
                'username': 'df',
                'email': 'df@dgrad.cd',
                'first_name': 'Directeur',
                'last_name': 'Financier',
                'role': 'DF',
                'service': service_financier,
                'password': 'df123456',
                'is_staff': True,
            },
            {
                'username': 'comptable1',
                'email': 'comptable1@dgrad.cd',
                'first_name': 'Comptable',
                'last_name': 'Principal',
                'role': 'COMPTABLE',
                'service': service_comptable,
                'password': 'comptable123',
                'is_staff': False,
            },
            {
                'username': 'comptable2',
                'email': 'comptable2@dgrad.cd',
                'first_name': 'Comptable',
                'last_name': 'Assistant',
                'role': 'COMPTABLE',
                'service': service_comptable,
                'password': 'comptable123',
                'is_staff': False,
            },
            {
                'username': 'chef_service',
                'email': 'chef.service@dgrad.cd',
                'first_name': 'Chef',
                'last_name': 'de Service',
                'role': 'CHEF_SERVICE',
                'service': service_financier,
                'password': 'chef123456',
                'is_staff': False,
            },
            {
                'username': 'auditeur',
                'email': 'auditeur@dgrad.cd',
                'first_name': 'Auditeur',
                'last_name': 'Interne',
                'role': 'AUDITEUR',
                'service': service_audit,
                'password': 'audit123456',
                'is_staff': False,
            },
            {
                'username': 'operateur1',
                'email': 'operateur1@dgrad.cd',
                'first_name': 'Opérateur',
                'last_name': 'de Saisie 1',
                'role': 'OPERATEUR_SAISIE',
                'service': service_comptable,
                'password': 'operateur123',
                'is_staff': False,
            },
            {
                'username': 'operateur2',
                'email': 'operateur2@dgrad.cd',
                'first_name': 'Opérateur',
                'last_name': 'de Saisie 2',
                'role': 'OPERATEUR_SAISIE',
                'service': service_comptable,
                'password': 'operateur123',
                'is_staff': False,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for user_data in users_data:
            username = user_data.pop('username')
            password = user_data.pop('password')
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                user.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Utilisateur créé: {username} ({user.get_role_display()}) - Password: {password}'
                    )
                )
            else:
                # Mettre à jour le mot de passe si l'utilisateur existe déjà
                user.set_password(password)
                user.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'→ Utilisateur mis à jour: {username} ({user.get_role_display()}) - Password: {password}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ {created_count} utilisateur(s) créé(s), {updated_count} mis à jour(s)'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  IMPORTANT: Changez les mots de passe après la première connexion!'
            )
        )


