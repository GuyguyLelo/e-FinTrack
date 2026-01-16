#!/usr/bin/env python
"""
Script pour créer des données de test pour la fonctionnalité de paiement
"""
import os
import sys
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from accounts.models import Service
from banques.models import Banque, CompteBancaire
from releves.models import ReleveBancaire
from demandes.models import DemandePaiement

User = get_user_model()

def create_test_data():
    """Créer des données de test pour les paiements"""
    print("🚀 Création des données de test pour les paiements...")
    
    # 1. Créer un utilisateur comptable si n'existe pas
    comptable, created = User.objects.get_or_create(
        username='comptable_test',
        defaults={
            'email': 'comptable@test.com',
            'first_name': 'Test',
            'last_name': 'Comptable',
            'role': 'COMPTABLE',
            'is_active': True,
        }
    )
    if created:
        comptable.set_password('password123')
        comptable.save()
        print("✅ Utilisateur comptable créé")
    
    # 2. Créer une banque de test
    banque, created = Banque.objects.get_or_create(
        nom_banque='BANQUE TEST',
        defaults={
            'code_swift': 'TESTCD',
            'adresse': 'Adresse Test',
            'telephone': '+243123456789',
            'email': 'test@banque.com',
        }
    )
    if created:
        print("✅ Banque créée")
    
    # 3. Créer des comptes bancaires
    compte_usd, created = CompteBancaire.objects.get_or_create(
        banque=banque,
        numero_compte='TEST-USD-001',
        defaults={
            'intitule_compte': 'Compte Test USD',
            'devise': 'USD',
            'solde_initial': Decimal('50000.00'),
            'solde_courant': Decimal('50000.00'),
            'date_ouverture': date.today() - timedelta(days=365),
            'actif': True,
        }
    )
    if created:
        print("✅ Compte USD créé")
    
    compte_cdf, created = CompteBancaire.objects.get_or_create(
        banque=banque,
        numero_compte='TEST-CDF-001',
        defaults={
            'intitule_compte': 'Compte Test CDF',
            'devise': 'CDF',
            'solde_initial': Decimal('150000000.00'),
            'solde_courant': Decimal('150000000.00'),
            'date_ouverture': date.today() - timedelta(days=365),
            'actif': True,
        }
    )
    if created:
        print("✅ Compte CDF créé")
    
    # 4. Créer un service de test
    service, created = Service.objects.get_or_create(
        nom_service='SERVICE TEST',
        defaults={
            'description': 'Service pour tester les paiements',
            'actif': True,
        }
    )
    if created:
        print("✅ Service créé")
    
    # 5. Créer des demandes de paiement validées
    demandes_data = [
        {
            'reference': 'DEM-TEST-001',
            'description': 'Achat de matériel informatique',
            'montant': Decimal('2500.00'),
            'devise': 'USD',
            'statut': 'VALIDEE_DF',
        },
        {
            'reference': 'DEM-TEST-002',
            'description': 'Frais de formation',
            'montant': Decimal('1500.00'),
            'devise': 'USD',
            'statut': 'VALIDEE_DG',
        },
        {
            'reference': 'DEM-TEST-003',
            'description': 'Maintenance véhicules',
            'montant': Decimal('800.00'),
            'devise': 'USD',
            'statut': 'VALIDEE_DF',
        },
        {
            'reference': 'DEM-TEST-004',
            'description': 'Achat fournitures de bureau',
            'montant': Decimal('50000000.00'),
            'devise': 'CDF',
            'statut': 'VALIDEE_DG',
        },
    ]
    
    for demande_data in demandes_data:
        demande, created = DemandePaiement.objects.get_or_create(
            reference=demande_data['reference'],
            defaults={
                **demande_data,
                'service_demandeur': service,
                'cree_par': comptable,
                'date_demande': date.today() - timedelta(days=10),
                'montant_deja_paye': Decimal('0.00'),
            }
        )
        if created:
            print(f"✅ Demande {demande.reference} créée")
        else:
            # S'assurer que les champs de paiement sont corrects
            demande.montant_deja_paye = Decimal('0.00')
            demande.reste_a_payer = demande.montant
            demande.save()
    
    # 6. Créer des relevés bancaires
    releve_usd, created = ReleveBancaire.objects.get_or_create(
        banque=banque,
        compte_bancaire=compte_usd,
        periode_debut=date.today() - timedelta(days=30),
        periode_fin=date.today(),
        defaults={
            'devise': 'USD',
            'total_recettes': Decimal('100000.00'),
            'total_depenses': Decimal('30000.00'),
            'solde_banque': Decimal('70000.00'),
            'saisi_par': comptable,
            'valide': True,
            'valide_par': comptable,
            'date_validation': timezone.now(),
            'archive': False,
        }
    )
    if created:
        print("✅ Relevé USD créé")
    
    releve_cdf, created = ReleveBancaire.objects.get_or_create(
        banque=banque,
        compte_bancaire=compte_cdf,
        periode_debut=date.today() - timedelta(days=30),
        periode_fin=date.today(),
        defaults={
            'devise': 'CDF',
            'total_recettes': Decimal('300000000.00'),
            'total_depenses': Decimal('100000000.00'),
            'solde_banque': Decimal('200000000.00'),
            'saisi_par': comptable,
            'valide': True,
            'valide_par': comptable,
            'date_validation': timezone.now(),
            'archive': False,
        }
    )
    if created:
        print("✅ Relevé CDF créé")
    
    print("\n🎉 Données de test créées avec succès !")
    print("\n📋 Instructions pour tester :")
    print("1. Connectez-vous avec :")
    print("   - Nom d'utilisateur : comptable_test")
    print("   - Mot de passe : password123")
    print("\n2. Dans le menu de gauche, cliquez sur 'Paiements'")
    print("3. Testez les deux méthodes de paiement :")
    print("   - Payer par relevé (recommandé)")
    print("   - Nouveau paiement (paiement individuel)")
    print("\n💡 Les demandes créées sont déjà validées et prêtes à être payées !")

if __name__ == '__main__':
    create_test_data()
