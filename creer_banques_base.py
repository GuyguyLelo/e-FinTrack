#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from decimal import Decimal
from banques.models import Banque, CompteBancaire

def creer_banques_base():
    """Crée des banques et comptes bancaires de base pour repartir sur de bonnes bases"""
    
    print("=== Création des Banques et Comptes Bancaires de Base ===\n")
    
    # Banques à créer
    banques_data = [
        {
            'nom_banque': 'BCDC',
            'code_swift': 'BCDCCDKI',
            'adresse': 'Kinshasa, République Démocratique du Congo',
            'email': 'contact@bcdc.cd',
            'telephone': '+243 12 345 678',
            'comptes': [
                {'intitule': 'Compte Principal DGRAD', 'numero': 'BCDC-001-USD', 'devise': 'USD', 'solde': Decimal('0.00')},
                {'intitule': 'Compte Principal DGRAD', 'numero': 'BCDC-001-CDF', 'devise': 'CDF', 'solde': Decimal('0.00')},
            ]
        },
        {
            'nom_banque': 'RAWBANK',
            'code_swift': 'RAWBCDKI',
            'adresse': 'Kinshasa, République Démocratique du Congo',
            'email': 'info@rawbank.cd',
            'telephone': '+243 12 987 654',
            'comptes': [
                {'intitule': 'Compte Opérations DGRAD', 'numero': 'RAW-001-CDF', 'devise': 'CDF', 'solde': Decimal('0.00')},
            ]
        },
        {
            'nom_banque': 'TMB',
            'code_swift': 'TMBCCDKI',
            'adresse': 'Kinshasa, République Démocratique du Congo',
            'email': 'service@tmb.cd',
            'telephone': '+243 12 456 789',
            'comptes': [
                {'intitule': 'Compte USD DGRAD', 'numero': 'TMB-001-USD', 'devise': 'USD', 'solde': Decimal('0.00')},
            ]
        },
    ]
    
    try:
        for banque_data in banques_data:
            # Créer ou récupérer la banque
            banque, created = Banque.objects.get_or_create(
                nom_banque=banque_data['nom_banque'],
                defaults={
                    'code_swift': banque_data['code_swift'],
                    'adresse': banque_data['adresse'],
                    'email': banque_data['email'],
                    'telephone': banque_data['telephone'],
                    'active': True
                }
            )
            
            if created:
                print(f"✅ Banque créée: {banque.nom_banque}")
            else:
                print(f"ℹ️  Banque existante: {banque.nom_banque}")
            
            # Créer les comptes bancaires
            for compte_data in banque_data['comptes']:
                compte, created = CompteBancaire.objects.get_or_create(
                    numero_compte=compte_data['numero'],
                    defaults={
                        'banque': banque,
                        'intitule_compte': compte_data['intitule'],
                        'devise': compte_data['devise'],
                        'solde_initial': compte_data['solde'],
                        'solde_courant': compte_data['solde'],
                        'date_ouverture': '2024-01-01',
                        'actif': True
                    }
                )
                
                if created:
                    print(f"  ✅ Compte créé: {compte.intitule_compte} ({compte.devise})")
                else:
                    print(f"  ℹ️  Compte existant: {compte.intitule_compte} ({compte.devise})")
            
            print()
        
        # Résumé
        total_banques = Banque.objects.count()
        total_comptes = CompteBancaire.objects.count()
        
        print("📊 Résumé:")
        print(f"  Total banques: {total_banques}")
        print(f"  Total comptes: {total_comptes}")
        print()
        print("🎉 Configuration bancaire de base créée avec succès !")
        print()
        print("💡 Les soldes sont à 0.00 et seront mis à jour automatiquement")
        print("   lors de la création des recettes et dépenses.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")

if __name__ == '__main__':
    creer_banques_base()
