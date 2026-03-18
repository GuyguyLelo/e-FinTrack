#!/usr/bin/env python
"""
Script pour créer une structure hiérarchique de services
"""
import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
django.setup()

from accounts.models import Service

def create_hierarchical_services():
    """Créer une structure hiérarchique de services"""
    
    print("🏗️  Création de la structure hiérarchique des services...")
    
    # Services racine
    services_data = [
        {
            'code_service': 'DIR_GEN',
            'nom_service': 'Direction Générale',
            'description': 'Direction générale de la DGRAD',
            'parent_service': None,
            'actif': True
        },
        {
            'code_service': 'DIR_FIN',
            'nom_service': 'Direction Financière',
            'description': 'Direction financière de la DGRAD',
            'parent_service': None,
            'actif': True
        },
        {
            'code_service': 'DIR_ADMIN',
            'nom_service': 'Direction Administrative',
            'description': 'Direction administrative de la DGRAD',
            'parent_service': None,
            'actif': True
        }
    ]
    
    # Créer les services racine
    root_services = {}
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            nom_service=service_data['nom_service'],
            defaults=service_data
        )
        root_services[service_data['code_service']] = service
        print(f"  ✅ Service racine: {service.nom_service} ({'créé' if created else 'existant'})")
    
    # Services enfants pour Direction Générale
    dg_children = [
        {
            'code_service': 'CAB_DIR',
            'nom_service': 'Cabinet du Directeur Général',
            'description': 'Cabinet du Directeur Général',
            'parent_service': root_services['DIR_GEN'],
            'actif': True
        },
        {
            'code_service': 'COMM',
            'nom_service': 'Service Communication',
            'description': 'Service communication et relations publiques',
            'parent_service': root_services['DIR_GEN'],
            'actif': True
        }
    ]
    
    # Services enfants pour Direction Financière
    fin_children = [
        {
            'code_service': 'DIV_BUDG',
            'nom_service': 'Division Budget',
            'description': 'Division gestion budgétaire',
            'parent_service': root_services['DIR_FIN'],
            'actif': True
        },
        {
            'code_service': 'DIV_COMPTA',
            'nom_service': 'Division Comptabilité',
            'description': 'Division comptabilité générale',
            'parent_service': root_services['DIR_FIN'],
            'actif': True
        },
        {
            'code_service': 'DIV_TRES',
            'nom_service': 'Division Trésorerie',
            'description': 'Division gestion trésorerie',
            'parent_service': root_services['DIR_FIN'],
            'actif': True
        }
    ]
    
    # Services enfants pour Direction Administrative
    admin_children = [
        {
            'code_service': 'DIV_RH',
            'nom_service': 'Division Ressources Humaines',
            'description': 'Division gestion des ressources humaines',
            'parent_service': root_services['DIR_ADMIN'],
            'actif': True
        },
        {
            'code_service': 'DIV_MAT',
            'nom_service': 'Division Matériels',
            'description': 'Division gestion des matériels',
            'parent_service': root_services['DIR_ADMIN'],
            'actif': True
        }
    ]
    
    # Créer tous les services enfants
    all_children = dg_children + fin_children + admin_children
    
    for service_data in all_children:
        service, created = Service.objects.get_or_create(
            nom_service=service_data['nom_service'],
            defaults=service_data
        )
        print(f"  📁 Service enfant: {service.nom_service} ({'créé' if created else 'existant'})")
        
        # Mettre à jour le parent si nécessaire
        if service.parent_service != service_data['parent_service']:
            service.parent_service = service_data['parent_service']
            service.save()
            print(f"    🔗 Parent mis à jour: {service.parent_service.nom_service}")
    
    # Sous-services pour Division Comptabilité
    div_compta = Service.objects.get(code_service='DIV_COMPTA')
    sub_compta_children = [
        {
            'code_service': 'SERV_COMPTA_GEN',
            'nom_service': 'Service Comptabilité Générale',
            'description': 'Service comptabilité générale',
            'parent_service': div_compta,
            'actif': True
        },
        {
            'code_service': 'SERV_COMPTA_ANAL',
            'nom_service': 'Service Comptabilité Analytique',
            'description': 'Service comptabilité analytique',
            'parent_service': div_compta,
            'actif': True
        }
    ]
    
    for service_data in sub_compta_children:
        service, created = Service.objects.get_or_create(
            nom_service=service_data['nom_service'],
            defaults=service_data
        )
        print(f"    📄 Sous-service: {service.nom_service} ({'créé' if created else 'existant'})")
        
        # Mettre à jour le parent si nécessaire
        if service.parent_service != service_data['parent_service']:
            service.parent_service = service_data['parent_service']
            service.save()
            print(f"      🔗 Parent mis à jour: {service.parent_service.nom_service}")
    
    # Afficher la structure complète
    print("\n📊 Structure hiérarchique créée:")
    print("=" * 50)
    
    def print_service_tree(service, indent=0):
        """Afficher l'arborescence des services"""
        prefix = "  " * indent
        if service.code_service:
            print(f"{prefix}📁 [{service.code_service}] {service.nom_service}")
        else:
            print(f"{prefix}📁 {service.nom_service}")
        
        children = service.services_enfants.filter(actif=True).order_by('nom_service')
        for child in children:
            print_service_tree(child, indent + 1)
    
    # Afficher les services racine et leurs enfants
    for root_service in Service.objects.filter(parent_service=None, actif=True).order_by('nom_service'):
        print_service_tree(root_service)
    
    print("\n✨ Structure hiérarchique des services créée avec succès!")
    print(f"📈 Total services: {Service.objects.count()}")
    print(f"🌳 Services racine: {Service.objects.filter(parent_service=None).count()}")
    
    # Afficher quelques statistiques
    print("\n📊 Statistiques:")
    for service in Service.objects.all():
        if service.has_children:
            child_count = service.services_enfants.count()
            total_descendants = len(service.get_all_children())
            print(f"  📁 {service.nom_service}: {child_count} enfants directs, {total_descendants} descendants totaux")

if __name__ == "__main__":
    create_hierarchical_services()
