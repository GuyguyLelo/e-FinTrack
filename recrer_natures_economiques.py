#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

def recreer_natures_economiques():
    """Recrée les natures économiques de base"""
    
    print("=== Recréation des Natures Économiques ===\n")
    
    try:
        from demandes.models import NatureEconomique
        
        # Natures économiques de base
        natures_data = [
            {
                'code': '100',
                'titre': 'Charges de Personnel',
                'description': 'Salaires, primes, indemnités et charges sociales',
                'parent': None
            },
            {
                'code': '110',
                'titre': 'Salaires et Appointements',
                'description': 'Rémunérations du personnel permanent',
                'parent': '100'
            },
            {
                'code': '120',
                'titre': 'Primes et Indemnités',
                'description': 'Primes de performance, indemnités de transport, etc.',
                'parent': '100'
            },
            {
                'code': '200',
                'titre': 'Charges de Fonctionnement',
                'description': 'Frais de fonctionnement courant',
                'parent': None
            },
            {
                'code': '210',
                'titre': 'Frais de Bureau',
                'description': 'Fournitures de bureau, matériel, etc.',
                'parent': '200'
            },
            {
                'code': '220',
                'titre': 'Frais de Déplacement',
                'description': 'Missions, transport, hébergement',
                'parent': '200'
            },
            {
                'code': '300',
                'titre': 'Charges Financières',
                'description': 'Intérêts, commissions et frais bancaires',
                'parent': None
            },
            {
                'code': '400',
                'titre': 'Investissements',
                'description': 'Acquisitions d\'immobilisations et équipements',
                'parent': None
            },
            {
                'code': '500',
                'titre': 'Autres Charges',
                'description': 'Charges diverses non classées ailleurs',
                'parent': None
            }
        ]
        
        # Dictionnaire pour stocker les objets créés
        natures_dict = {}
        
        # Créer les natures économiques
        for nature_data in natures_data:
            parent_obj = None
            if nature_data['parent']:
                parent_obj = natures_dict.get(nature_data['parent'])
            
            nature, created = NatureEconomique.objects.get_or_create(
                code=nature_data['code'],
                defaults={
                    'titre': nature_data['titre'],
                    'description': nature_data['description'],
                    'parent': parent_obj
                }
            )
            
            natures_dict[nature_data['code']] = nature
            
            if created:
                print(f"✅ Nature créée: {nature.code} - {nature.titre}")
            else:
                print(f"ℹ️  Nature existante: {nature.code} - {nature.titre}")
        
        print(f"\n📊 Total natures économiques: {NatureEconomique.objects.count()}")
        print("\n🎉 Natures économiques recréées avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la recréation: {e}")

if __name__ == '__main__':
    recreer_natures_economiques()
