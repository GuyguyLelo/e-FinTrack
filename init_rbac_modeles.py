"""
Script pour créer des permissions basées sur les modèles Django (idée géniale !)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.apps import apps
from rbac.models_modele import PermissionModele, RoleModele


def analyser_modeles_django():
    """Analyser tous les modèles Django pour créer automatiquement les permissions"""
    print("=== ANALYSE DES MODÈLES DJANGO ===")
    
    # Liste des applications à analyser
    apps_to_analyze = [
        'banques',
        'demandes', 
        'recettes',
        'clotures',
        'etats',
        'releves',
        'accounts',
        'rapports'
    ]
    
    modeles_trouves = {}
    
    for app_name in apps_to_analyze:
        try:
            app_config = apps.get_app_config(app_name)
            modeles_trouves[app_name] = []
            
            for model_name, model_class in app_config.models.items():
                if hasattr(model_class, '_meta'):
                    modeles_trouves[app_name].append({
                        'nom': model_name,
                        'classe': model_class,
                        'verbose_name': model_class._meta.verbose_name,
                        'verbose_name_plural': model_class._meta.verbose_name_plural,
                        'db_table': model_class._meta.db_table,
                        'fields': [field.name for field in model_class._meta.fields]
                    })
            
            print(f"✅ Application {app_name}: {len(modeles_trouves[app_name])} modèles")
            
        except LookupError:
            print(f"❌ Application {app_name}: non trouvée")
    
    return modeles_trouves


def creer_permissions_pour_modeles(modeles_par_app):
    """Créer automatiquement les permissions pour tous les modèles"""
    print("\\n=== CRÉATION AUTOMATIQUE DES PERMISSIONS ===")
    
    actions_possibles = ['liste', 'creer', 'modifier', 'supprimer', 'valider']
    
    for app_name, modeles in modeles_par_app.items():
        print(f"\\n📁 Application: {app_name}")
        
        for modele_info in modeles:
            modele_nom = modele_info['nom']
            verbose_name = modele_info['verbose_name']
            
            print(f"  📋 Modèle: {modele_nom} ({verbose_name})")
            
            for action in actions_possibles:
                # Créer la permission
                permission, created = PermissionModele.objects.get_or_create(
                    modele_django=modele_nom,
                    action=action,
                    app_label=app_name,
                    defaults={
                        'nom': f"{action.title()} {verbose_name}",
                        'description': f"Permet de {action} {verbose_name}",
                        'est_active': True
                    }
                )
                
                if created:
                    print(f"    ✅ Créée: {permission}")
                else:
                    print(f"    ℹ️  Existe: {permission}")
    
    print(f"\\n📊 Total permissions créées: {PermissionModele.objects.count()}")


def creer_roles_exemples():
    """Créer des rôles exemples basés sur les modèles"""
    print("\\n=== CRÉATION DES RÔLES EXEMPLES ===")
    
    # Rôle "Gestionnaire Dépenses"
    role_depenses, created = RoleModele.objects.get_or_create(
        nom="Gestionnaire Dépenses",
        code="GESTIONNAIRE_DEPENSE",  # Code plus court
        defaults={
            'description': 'Peut gérer les dépenses (DepenseFeuille)',
            'couleur': '#dc3545',
            'icone': 'bi-journal-text',
            'niveau_acces': 2
        }
    )
    
    if created:
        # Ajouter les permissions sur DepenseFeuille
        permissions_depenses = PermissionModele.objects.filter(
            modele_django='DepenseFeuille',
            action__in=['liste', 'creer', 'modifier', 'supprimer']
        )
        role_depenses.permissions_modeles.add(*permissions_depenses)
        print(f"✅ Rôle 'Gestionnaire Dépenses' créé avec {permissions_depenses.count()} permissions")
    
    # Rôle "Opérateur Saisie"
    role_operateur, created = RoleModele.objects.get_or_create(
        nom="Opérateur Saisie",
        code="OPERATEUR_SAISIE_DEP",  # Code plus court
        defaults={
            'description': 'Peut saisir et modifier les dépenses',
            'couleur': '#ffc107',
            'icone': 'bi-pencil-square',
            'niveau_acces': 1
        }
    )
    
    if created:
        # Ajouter les permissions limitées
        permissions_operateur = PermissionModele.objects.filter(
            modele_django='DepenseFeuille',
            action__in=['liste', 'creer', 'modifier']
        )
        role_operateur.permissions_modeles.add(*permissions_operateur)
        print(f"✅ Rôle 'Opérateur Saisie' créé avec {permissions_operateur.count()} permissions")
    
    # Rôle "Validateur Dépenses"
    role_validateur, created = RoleModele.objects.get_or_create(
        nom="Validateur Dépenses",
        code="VALIDATEUR_DEPENSE",  # Code plus court
        defaults={
            'description': 'Peut valider les dépenses',
            'couleur': '#28a745',
            'icone': 'bi-check-circle',
            'niveau_acces': 3
        }
    )
    
    if created:
        # Ajouter les permissions de validation
        permissions_validateur = PermissionModele.objects.filter(
            modele_django='DepenseFeuille',
            action__in=['liste', 'valider']
        )
        role_validateur.permissions_modeles.add(*permissions_validateur)
        print(f"✅ Rôle 'Validateur Dépenses' créé avec {permissions_validateur.count()} permissions")


def montrer_permissions_role(role_code):
    """Montrer les permissions d'un rôle par modèle"""
    try:
        role = RoleModele.objects.get(code=role_code)
        print(f"\\n=== PERMISSIONS DU RÔLE: {role.nom} ===")
        
        permissions_by_modele = role.get_permissions_by_modele()
        
        for modele, permissions in permissions_by_modele.items():
            print(f"\\n📋 Modèle: {modele}")
            for perm in permissions:
                print(f"  ✅ {perm.get_action_display()} - {perm.description}")
                print(f"     URL: {perm.url_pattern}")
        
    except RoleModele.DoesNotExist:
        print(f"❌ Rôle '{role_code}' non trouvé")


def main():
    """Fonction principale"""
    print("=== SYSTÈME RBAC BASÉ SUR LES MODÈLES DJANGO ===")
    print("Idée géniale de l'utilisateur !")
    
    # Étape 1: Analyser les modèles Django
    modeles_par_app = analyser_modeles_django()
    
    # Étape 2: Créer les permissions automatiquement
    creer_permissions_pour_modeles(modeles_par_app)
    
    # Étape 3: Créer des rôles exemples
    creer_roles_exemples()
    
    # Étape 4: Montrer un exemple
    montrer_permissions_role('GESTIONNAIRE_DEPENSES')
    
    print("\\n=== SYSTÈME PRÊT ! ===")
    print("Maintenant les permissions sont directement liées aux modèles Django !")
    print("Plus besoin de modules génériques !")


if __name__ == '__main__':
    main()
