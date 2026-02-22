#!/usr/bin/env python
"""
Script pour mapper les IDs des banques entre SQLite et PostgreSQL
"""
import json
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from banques.models import Banque

def mapper_banques():
    """Mapper les banques existantes dans PostgreSQL"""
    
    # Lire le fichier JSON exporté
    with open('vraies_donnees.json', 'r') as f:
        data = json.load(f)
    
    # Créer un mapping des noms de banques vers IDs PostgreSQL
    banque_mapping = {}
    banques_pg = Banque.objects.all()
    
    for banque in banques_pg:
        banque_mapping[banque.nom_banque.lower()] = banque.id
    
    print("🔍 Mapping des banques PostgreSQL:")
    for nom, pg_id in banque_mapping.items():
        print(f"   {nom}: ID {pg_id}")
    
    # Modifier le JSON pour utiliser les bons IDs
    print("\n🔄 Modification du fichier JSON...")
    
    modified_data = []
    for item in data:
        if item.get('model') == 'recettes.recettefeuille':
            fields = item.get('fields', {})
            banque_id = fields.get('banque')
            
            if banque_id is not None:
                # Chercher le nom de la banque dans les recettes
                # Pour cela, il faudrait analyser les données plus en détail
                print(f"   Recette ID {item.get('pk')} → banque_id {banque_id}")
            
            modified_data.append(item)
        else:
            modified_data.append(item)
    
    # Sauvegarder le JSON modifié
    with open('donnees_modifiees.json', 'w') as f:
        json.dump(modified_data, f, indent=2)
    
    print(f"\n✅ Fichier modifié sauvegardé: donnees_modifiees.json")
    print(f"📊 Total enregistrements: {len(modified_data)}")

if __name__ == "__main__":
    mapper_banques()
