"""
Commande de gestion pour créer l'utilisateur initial
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Service

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée l\'utilisateur administrateur initial'

    def handle(self, *args, **options):
        # Créer le service Direction Générale s'il n'existe pas
        service_dg, created = Service.objects.get_or_create(
            nom_service='Direction Générale',
            defaults={'description': 'Direction Générale de la DGRAD', 'actif': True}
        )
        
        # Créer l'utilisateur admin s'il n'existe pas
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@dgrad.cd',
                password='admin',
                role='DG',
                service=service_dg,
                first_name='Administrateur',
                last_name='Système',
                telephone='+243900000000'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Utilisateur admin créé avec succès!\n'
                                  f'Username: admin\n'
                                  f'Password: admin\n'
                                  f'⚠️  Veuillez changer le mot de passe après la première connexion!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('L\'utilisateur admin existe déjà.')
            )

