#!/usr/bin/env python
"""
Script pour importer les natures économiques depuis SQLite vers PostgreSQL
en gérant la structure hiérarchique
"""
import json
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from demandes.models import NatureEconomique

def importer_natures_sqlite():
    """Importer les natures économiques depuis SQLite en gérant la hiérarchie"""
    
    # Lire le fichier JSON exporté depuis SQLite
    with open('natures_sqlite.json', 'r') as f:
        data = json.load(f)
    
    print("🔄 Importation des natures économiques depuis SQLite...")
    
    # Dictionnaire pour mapper les anciens PK vers les nouveaux
    pk_mapping = {}
    
    # Trier par code_parent pour créer les parents d'abord
    natures = [item for item in data if item.get('model') == 'demandes.natureeconomique']
    
    # Séparer les racines (sans parent) et les enfants
    racines = []
    enfants = []
    
    for nature in natures:
        fields = nature.get('fields', {})
        if fields.get('parent') is None:
            racines.append(nature)
        else:
            enfants.append(nature)
    
    print(f"   📊 Natures trouvées: {len(natures)}")
    print(f"   🌳 Racines: {len(racines)}")
    print(f"   👶 Enfants: {len(enfants)}")
    
    # Importer les racines d'abord
    print("\n🌳 Importation des natures racines...")
    for nature in racines:
        fields = nature.get('fields', {})
        try:
            nouvelle_nature = NatureEconomique.objects.create(
                code=fields.get('code'),
                titre=fields.get('titre'),
                description=fields.get('description', ''),
                code_parent=fields.get('code_parent', ''),
                active=fields.get('active', True),
                parent=None  # Pas de parent pour les racines
            )
            pk_mapping[nature.get('pk')] = nouvelle_nature.id
            print(f"   ✅ {fields.get('code')} - {fields.get('titre')}")
        except Exception as e:
            print(f"   ❌ Erreur {fields.get('code')}: {e}")
    
    # Importer les enfants en utilisant le mapping
    print("\n👶 Importation des natures enfants...")
    for nature in enfants:
        fields = nature.get('fields', {})
        old_parent_pk = fields.get('parent')
        new_parent_id = pk_mapping.get(old_parent_pk)
        
        if new_parent_id:
            try:
                nouvelle_nature = NatureEconomique.objects.create(
                    code=fields.get('code'),
                    titre=fields.get('titre'),
                    description=fields.get('description', ''),
                    code_parent=fields.get('code_parent', ''),
                    active=fields.get('active', True),
                    parent_id=new_parent_id
                )
                pk_mapping[nature.get('pk')] = nouvelle_nature.id
                print(f"   ✅ {fields.get('code')} - {fields.get('titre')} (parent: {new_parent_id})")
            except Exception as e:
                print(f"   ❌ Erreur {fields.get('code')}: {e}")
        else:
            print(f"   ⚠️ Parent non trouvé pour {fields.get('code')}")
    
    print(f"\n📊 Résultat final:")
    print(f"   Total natures dans PostgreSQL: {NatureEconomique.objects.count()}")
    print(f"   Mapping PK créé: {len(pk_mapping)} entrées")

if __name__ == "__main__":
    importer_natures_sqlite()
