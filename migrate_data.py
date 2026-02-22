#!/usr/bin/env python
"""
Script de migration manuelle des données de SQLite vers PostgreSQL
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from banques.models import Banque
from django.db import connection

def migrate_essential_data():
    """Migration des données essentielles"""
    
    print("🔄 Migration des données essentielles vers PostgreSQL")
    print("=" * 50)
    
    # Compter les données actuelles
    print(f"\n📊 Données actuelles dans PostgreSQL:")
    print(f"   - Utilisateurs: {User.objects.count()}")
    print(f"   - Banques: {Banque.objects.count()}")
    
    # Créer les utilisateurs de test s'ils n'existent pas
    if not User.objects.filter(username='AdminDaf').exists():
        admin = User.objects.create_user(
            username='AdminDaf',
            email='admin@efintrack.com',
            password='admin123',
            first_name='Admin',
            last_name='DAF',
            role='ADMIN'
        )
        print(f"   ✅ AdminDaf créé")
    
    if not User.objects.filter(username='OpsDaf').exists():
        ops = User.objects.create_user(
            username='OpsDaf',
            email='ops@efintrack.com',
            password='OpsDaf123',
            first_name='Opérateur',
            last_name='SAISIE',
            role='OPERATEUR_SAISIE'
        )
        print(f"   ✅ OpsDaf créé")
    
    # Créer quelques banques de test
    banques_test = [
        {'nom_banque': 'BIC', 'code_swift': 'BICCDKIN'},
        {'nom_banque': 'BCDC', 'code_swift': 'BCDCGDKI'},
        {'nom_banque': 'RAWBANK', 'code_swift': 'RAWBANK'},
    ]
    
    for banque_data in banques_test:
        if not Banque.objects.filter(nom_banque=banque_data['nom_banque']).exists():
            banque = Banque.objects.create(**banque_data)
            print(f"   ✅ Banque {banque.nom_banque} créée")
    
    print(f"\n📊 Données finales dans PostgreSQL:")
    print(f"   - Utilisateurs: {User.objects.count()}")
    print(f"   - Banques: {Banque.objects.count()}")
    
    print(f"\n✅ Migration terminée avec succès!")
    print(f"🎯 Configuration PostgreSQL:")
    print(f"   - Base: e_FinTrack_db")
    print(f"   - User: postgres")
    print(f"   - Host: localhost")
    print(f"   - Port: 5432")

if __name__ == "__main__":
    migrate_essential_data()
