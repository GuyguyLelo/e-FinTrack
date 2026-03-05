#!/usr/bin/env python3
"""
Script pour exporter les natures économiques du projet local
"""
import os
import sys
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from demandes.models import NatureEconomique

def export_natures_economiques():
    """Exporte toutes les natures économiques avec leurs relations"""
    
    print("📤 EXPORTATION DES NATURES ÉCONOMIQUES")
    print("=" * 50)
    
    # Récupérer toutes les natures
    natures = NatureEconomique.objects.all()
    print(f"📊 Total: {natures.count()} natures économiques")
    
    # Préparer les données pour l'export
    natures_data = []
    
    for nature in natures:
        nature_dict = {
            'id': nature.id,
            'code': nature.code,
            'titre': nature.titre,
            'description': nature.description,
            'code_parent': nature.code_parent,
            'active': nature.active,
            'parent_code': nature.parent.code if nature.parent else None,
            'parent_titre': nature.parent.titre if nature.parent else None,
        }
        natures_data.append(nature_dict)
    
    # Créer le fichier d'export
    export_data = {
        'export_date': datetime.now().isoformat(),
        'total_count': len(natures_data),
        'natures_economiques': natures_data,
    }
    
    # Sauvegarder en JSON
    filename = f"natures_economiques_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exporté dans: {filename}")
    
    # Statistiques
    print(f"\n📈 STATISTIQUES:")
    print(f"   Total: {len(natures_data)}")
    
    # Compter les catégories principales
    racines = [n for n in natures_data if n['code_parent'] is None]
    print(f"   Catégories principales: {len(racines)}")
    
    # Compter les actives/inactives
    actives = [n for n in natures_data if n['active']]
    inactives = [n for n in natures_data if not n['active']]
    print(f"   Actives: {len(actives)}")
    print(f"   Inactives: {len(inactives)}")
    
    # Afficher les catégories principales
    print(f"\n📋 CATÉGORIES PRINCIPALES:")
    for racine in sorted(racines, key=lambda x: x['code']):
        print(f"   {racine['code']} | {racine['titre']}")
    
    return filename

def generate_import_script(export_file):
    """Génère le script d'importation pour le VPS"""
    
    script_content = f'''#!/usr/bin/env python3
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
    with open('{export_file}', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📅 Export du: {{data['export_date']}}")
    print(f"📊 Total à importer: {{data['total_count']}}")
    
    # Compter les existantes
    existantes_avant = NatureEconomique.objects.count()
    print(f"📋 Natures existantes avant: {{existantes_avant}}")
    
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
                print(f"  🔄 Mise à jour: {{nature_data['code']}} - {{nature_data['titre']}}")
                
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
                print(f"  ✅ Importée: {{nature_data['code']}} - {{nature_data['titre']}}")
                
        except Exception as e:
            erreurs.append((nature_data['code'], str(e)))
            print(f"  ❌ Erreur: {{nature_data['code']}} - {{e}}")
    
    # Statistiques finales
    print(f"\\n📈 RÉSULTATS:")
    print(f"   Importées: {{importees}}")
    print(f"   Mises à jour: {{mises_a_jour}}")
    print(f"   Erreurs: {{len(erreurs)}}")
    
    if erreurs:
        print(f"\\n❌ DÉTAIL DES ERREURS:")
        for code, erreur in erreurs:
            print(f"   {{code}}: {{erreur}}")
    
    # Vérification finale
    total_final = NatureEconomique.objects.count()
    print(f"\\n📊 Total final: {{total_final}} natures")
    
    print(f"\\n✅ IMPORTATION TERMINÉE")

if __name__ == "__main__":
    try:
        import_natures_economiques()
    except Exception as e:
        print(f"❌ ERREUR: {{e}}")
        import traceback
        traceback.print_exc()
'''
    
    script_filename = "import_natures_economiques_vps.py"
    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Script d'importation généré: {script_filename}")
    return script_filename

if __name__ == "__main__":
    try:
        # Exporter les données
        export_file = export_natures_economiques()
        
        # Générer le script d'importation
        import_script = generate_import_script(export_file)
        
        print(f"\n🚀 PROCÉDURE DE TRANSFERT VERS VPS:")
        print(f"1. Transférez ces fichiers sur le VPS:")
        print(f"   - {export_file}")
        print(f"   - {import_script}")
        print(f"")
        print(f"2. Sur le VPS, exécutez:")
        print(f"   python {import_script}")
        print(f"")
        print(f"3. Vérifiez l'importation:")
        print(f"   python manage.py shell -c 'from demandes.models import NatureEconomique; print(NatureEconomique.objects.count())'")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
