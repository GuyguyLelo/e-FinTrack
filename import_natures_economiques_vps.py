#!/usr/bin/env python3
"""
Script d'importation des natures économiques pour VPS
Généré automatiquement depuis les données locales
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from demandes.models import NatureEconomique

def import_natures_economiques():
    """Importe les natures économiques depuis le fichier d'export"""
    
    print("📥 IMPORTATION DES NATURES ÉCONOMIQUES - VPS")
    print("=" * 50)
    
    # Charger les données
    with open('natures_economiques_export_20260305_145642.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📅 Export du: {data['export_date']}")
    print(f"📊 Total à importer: {data['total_count']}")
    
    # Compter les existantes
    existantes_avant = NatureEconomique.objects.count()
    print(f"📋 Natures existantes avant: {existantes_avant}")
    
    # Importer les natures
    importees = 0
    mises_a_jour = 0
    erreurs = []
    
    for nature_data in data['natures_economiques']:
        try:
            # Chercher si la nature existe déjà
            nature_existante = NatureEconomique.objects.filter(code=nature_data['code']).first()
            
            if nature_existante:
                # Mettre à jour
                nature_existante.titre = nature_data['titre']
                nature_existante.description = nature_data['description']
                nature_existante.code_parent = nature_data['code_parent']
                nature_existante.active = nature_data['active']
                
                # Gérer la relation parent
                if nature_data['parent_code']:
                    parent = NatureEconomique.objects.filter(code=nature_data['parent_code']).first()
                    nature_existante.parent = parent
                else:
                    nature_existante.parent = None
                
                nature_existante.save()
                mises_a_jour += 1
                print(f"  🔄 Mise à jour: {nature_data['code']} - {nature_data['titre']}")
                
            else:
                # Créer nouvelle
                nouvelle_nature = NatureEconomique(
                    code=nature_data['code'],
                    titre=nature_data['titre'],
                    description=nature_data['description'],
                    code_parent=nature_data['code_parent'],
                    active=nature_data['active']
                )
                
                # Gérer la relation parent
                if nature_data['parent_code']:
                    parent = NatureEconomique.objects.filter(code=nature_data['parent_code']).first()
                    nouvelle_nature.parent = parent
                
                nouvelle_nature.save()
                importees += 1
                print(f"  ✅ Importée: {nature_data['code']} - {nature_data['titre']}")
                
        except Exception as e:
            erreurs.append((nature_data['code'], str(e)))
            print(f"  ❌ Erreur: {nature_data['code']} - {e}")
    
    # Statistiques finales
    print(f"\n📈 RÉSULTATS:")
    print(f"   Importées: {importees}")
    print(f"   Mises à jour: {mises_a_jour}")
    print(f"   Erreurs: {len(erreurs)}")
    
    if erreurs:
        print(f"\n❌ DÉTAIL DES ERREURS:")
        for code, erreur in erreurs:
            print(f"   {code}: {erreur}")
    
    # Vérification finale
    total_final = NatureEconomique.objects.count()
    print(f"\n📊 Total final: {total_final} natures")
    
    print(f"\n✅ IMPORTATION TERMINÉE")

if __name__ == "__main__":
    try:
        import_natures_economiques()
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
