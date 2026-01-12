"""
Commande pour initialiser les données de base
"""
from django.core.management.base import BaseCommand
from accounts.models import Service
from banques.models import Banque, CompteBancaire
from django.utils import timezone


class Command(BaseCommand):
    help = 'Initialise les données de base (services et banques)'

    def handle(self, *args, **options):
        # Créer les services
        services_data = [
            {'nom': 'Direction Générale', 'description': 'Direction Générale de la DGRAD'},
            {'nom': 'Service Financier', 'description': 'Service de gestion financière'},
            {'nom': 'Service Comptable', 'description': 'Service de comptabilité'},
            {'nom': 'Service Audit', 'description': 'Service d\'audit interne'},
        ]
        
        for srv_data in services_data:
            service, created = Service.objects.get_or_create(
                nom_service=srv_data['nom'],
                defaults={
                    'description': srv_data['description'],
                    'actif': True
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Service créé: {service.nom_service}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Service existe déjà: {service.nom_service}')
                )
        
        # Créer les banques
        banques_data = [
            {
                'nom': 'Bank of Kinshasa',
                'code_swift': 'BKNSCDXXX',
                'adresse': 'Avenue de la République, Kinshasa',
                'email': 'contact@bankofkinshasa.cd',
                'telephone': '+243900000001',
            },
            {
                'nom': 'Trust Bank DRC',
                'code_swift': 'TBDCDCDXXX',
                'adresse': 'Boulevard 30 Juin, Kinshasa',
                'email': 'info@trustbank.cd',
                'telephone': '+243900000002',
            },
        ]
        
        for bank_data in banques_data:
            banque, created = Banque.objects.get_or_create(
                nom_banque=bank_data['nom'],
                defaults={
                    'code_swift': bank_data['code_swift'],
                    'adresse': bank_data['adresse'],
                    'email': bank_data['email'],
                    'telephone': bank_data['telephone'],
                    'active': True
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Banque créée: {banque.nom_banque}')
                )
                
                # Créer les comptes pour cette banque
                comptes_data = [
                    {'intitule': 'Compte Principal USD', 'numero': f'USD-{banque.id:03d}-2024', 'devise': 'USD', 'solde': 100000.00},
                    {'intitule': 'Compte Principal CDF', 'numero': f'CDF-{banque.id:03d}-2024', 'devise': 'CDF', 'solde': 50000000.00},
                ]
                
                for compte_data in comptes_data:
                    compte, created = CompteBancaire.objects.get_or_create(
                        banque=banque,
                        numero_compte=compte_data['numero'],
                        defaults={
                            'intitule_compte': compte_data['intitule'],
                            'devise': compte_data['devise'],
                            'solde_initial': compte_data['solde'],
                            'solde_courant': compte_data['solde'],
                            'date_ouverture': timezone.now().date(),
                            'actif': True
                        }
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ Compte créé: {compte.intitule_compte}')
                        )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Banque existe déjà: {banque.nom_banque}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ Initialisation des données terminée!')
        )

