#!/usr/bin/env python
"""
Script pour corriger les IDs de banques dans le JSON exporté
"""
import json

def corriger_ids_banques():
    """Corriger les IDs de banques dans le fichier JSON"""
    
    # Mapping des IDs corrects
    banque_id_mapping = {
        # Ancien ID SQLite → Nouvel ID PostgreSQL
        4: 1,  # BIC
        7: 2,  # BCDC  
        9: 3,  # RAWBANK
        6: 4,  # BANQUE COMMERCIALE
        5: 5,  # ECOBANK
        2: 6,  # FINBANK
        3: 7,  # STANBANK
    }
    
    # Lire le fichier JSON
    with open('vraies_donnees.json', 'r') as f:
        data = json.load(f)
    
    print("🔄 Correction des IDs de banques...")
    
    # Corriger les IDs de banques
    corrections_count = 0
    for item in data:
        if item.get('model') == 'recettes.recettefeuille':
            fields = item.get('fields', {})
            banque_id = fields.get('banque')
            
            if banque_id in banque_id_mapping:
                ancien_id = banque_id
                nouvel_id = banque_id_mapping[ancien_id]
                fields['banque'] = nouvel_id
                corrections_count += 1
                print(f"   Recette ID {item.get('pk')}: banque_id {ancien_id} → {nouvel_id}")
    
    # Sauvegarder le JSON corrigé
    with open('donnees_corrigees.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Fichier corrigé sauvegardé: donnees_corrigees.json")
    print(f"📊 Total corrections: {corrections_count}")
    print(f"📊 Total enregistrements: {len(data)}")

if __name__ == "__main__":
    corriger_ids_banques()
