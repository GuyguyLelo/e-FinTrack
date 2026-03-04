#!/usr/bin/env python3
"""
Script pour synchroniser les données de local vers VPS
Exporte les utilisateurs et services de l'environnement local
"""
import os
import sys
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User, Service

def export_local_data():
    """Exporte les données de l'environnement local"""
    
    print("📤 EXPORTATION DES DONNÉES LOCALES")
    print("=" * 40)
    
    # Exporter les services
    services_data = []
    for service in Service.objects.all():
        services_data.append({
            "nom_service": service.nom_service,
            "description": service.description,
            "actif": service.actif,
        })
    
    # Exporter les utilisateurs
    users_data = []
    for user in User.objects.all():
        users_data.append({
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "actif": user.actif,
            "service": user.service.nom_service if user.service else None,
            "telephone": user.telephone,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
        })
    
    # Créer le fichier d'export
    export_data = {
        "export_date": datetime.now().isoformat(),
        "services": services_data,
        "users": users_data,
    }
    
    filename = f"local_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Données exportées dans: {filename}")
    print(f"   Services: {len(services_data)}")
    print(f"   Utilisateurs: {len(users_data)}")
    
    return filename

def generate_vps_import_script(export_file):
    """Génère le script d'importation pour le VPS"""
    
    script_content = f'''#!/usr/bin/env python3
"""
Script d'importation pour VPS
Généré automatiquement à partir des données locales
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User, Service

def import_from_local():
    """Importe les données depuis le fichier d'export local"""
    
    print("📥 IMPORTATION DES DONNÉES LOCALES VERS VPS")
    print("=" * 50)
    
    # Charger les données
    with open('{export_file}', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📅 Export du: {{data['export_date']}}")
    
    # 1. Importer les services
    print("\\n📋 IMPORTATION DES SERVICES:")
    for service_data in data['services']:
        service, created = Service.objects.get_or_create(
            nom_service=service_data['nom_service'],
            defaults={{
                'description': service_data['description'],
                'actif': service_data['actif'],
            }}
        )
        status = "✅ Créé" if created else "ℹ️  Existant"
        print(f"   {{status}}: {{service.nom_service}}")
    
    # 2. Importer les utilisateurs
    print("\\n👤 IMPORTATION DES UTILISATEURS:")
    for user_data in data['users']:
        user, created = User.objects.update_or_create(
            username=user_data['username'],
            defaults={{
                'email': user_data['email'],
                'role': user_data['role'],
                'actif': user_data['actif'],
                'telephone': user_data['telephone'],
                'is_superuser': user_data['is_superuser'],
                'is_staff': user_data['is_staff'],
            }}
        )
        
        # Assigner le service
        if user_data['service']:
            try:
                service = Service.objects.get(nom_service=user_data['service'])
                user.service = service
                user.save()
            except Service.DoesNotExist:
                print(f"   ⚠️  Service '{{user_data['service']}}' non trouvé pour {{user.username}}")
        
        status = "✅ Créé/Mis à jour" if created else "🔄 Mis à jour"
        print(f"   {{status}}: {{user.username}} ({{user.get_role_display()}})")
    
    print("\\n📊 RÉCAPITULATIF:")
    print(f"   Services: {{Service.objects.count()}}")
    print(f"   Utilisateurs: {{User.objects.count()}}")
    
    print("\\n✅ IMPORTATION TERMINÉE")

if __name__ == "__main__":
    try:
        import_from_local()
    except Exception as e:
        print(f"❌ ERREUR: {{e}}")
        import traceback
        traceback.print_exc()
'''
    
    script_filename = "import_local_data_to_vps.py"
    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Script d'importation généré: {script_filename}")
    return script_filename

if __name__ == "__main__":
    try:
        # Exporter les données locales
        export_file = export_local_data()
        
        # Générer le script d'importation
        import_script = generate_vps_import_script(export_file)
        
        print(f"\n🚀 PROCÉDURE DE SYNCHRONISATION:")
        print(f"1. Transférez ces fichiers sur le VPS:")
        print(f"   - {export_file}")
        print(f"   - {import_script}")
        print(f"")
        print(f"2. Sur le VPS, exécutez:")
        print(f"   python {import_script}")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
