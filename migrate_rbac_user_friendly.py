"""
Script de migration vers un système RBAC convivial pour utilisateurs non-techniques
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from rbac.models import Permission as OldPermission, Role as OldRole
from rbac.models_improved import CategoriePermission, Permission as NewPermission, Role as NewRole


def creer_categories_par_defaut():
    """Créer les catégories de permissions par défaut"""
    categories_data = [
        {
            'nom': 'Banques',
            'description': 'Gestion des banques et comptes bancaires',
            'icone': 'bi-bank',
            'ordre': 1
        },
        {
            'nom': 'Clôtures',
            'description': 'Gestion des clôtures comptables',
            'icone': 'bi-calendar-check',
            'ordre': 2
        },
        {
            'nom': 'Demandes',
            'description': 'Gestion des demandes de paiement',
            'icone': 'bi-file-earmark-text',
            'ordre': 3
        },
        {
            'nom': 'Recettes',
            'description': 'Gestion des recettes',
            'icone': 'bi-cash-stack',
            'ordre': 4
        },
        {
            'nom': 'États',
            'description': 'Génération des états financiers',
            'icone': 'bi-file-text',
            'ordre': 5
        },
        {
            'nom': 'Utilisateurs',
            'description': 'Gestion des utilisateurs et rôles',
            'icone': 'bi-people',
            'ordre': 6
        },
        {
            'nom': 'Tableau de bord',
            'description': 'Accès au tableau de bord',
            'icone': 'bi-speedometer2',
            'ordre': 7
        }
    ]
    
    categories = {}
    for cat_data in categories_data:
        categorie, created = CategoriePermission.objects.get_or_create(
            nom=cat_data['nom'],
            defaults=cat_data
        )
        categories[cat_data['nom']] = categorie
        print(f"{'✅ Créée' if created else 'ℹ️  Existe'} : {categorie.nom}")
    
    return categories


def migrer_permissions(categories):
    """Migrer les permissions existantes vers le nouveau système"""
    print("\n=== MIGRATION DES PERMISSIONS ===")
    
    # Mapping des modules vers catégories
    module_to_categorie = {
        'banques': 'Banques',
        'clotures': 'Clôtures',
        'demandes': 'Demandes',
        'recettes': 'Recettes',
        'etats': 'États',
        'utilisateurs': 'Utilisateurs',
        'tableau_bord': 'Tableau de bord',
        'permissions': 'Utilisateurs',
        'paiements': 'Demandes',
        'releves': 'Demandes'
    }
    
    for old_perm in OldPermission.objects.filter(est_active=True):
        # Trouver la catégorie correspondante
        categorie_nom = module_to_categorie.get(old_perm.module, 'Autres')
        categorie = categories.get(categorie_nom)
        
        if not categorie:
            print(f"⚠️  Catégorie non trouvée pour le module {old_perm.module}")
            continue
        
        # Extraire l'action du code
        action = 'voir'  # défaut
        for action_candidate in ['creer', 'modifier', 'supprimer', 'valider', 'effectuer', 'generer', 'voir']:
            if action_candidate in old_perm.code.lower():
                action = action_candidate
                break
        
        # Créer la nouvelle permission
        new_perm, created = NewPermission.objects.get_or_create(
            code=old_perm.code,
            defaults={
                'nom': old_perm.nom,
                'description': old_perm.description,
                'categorie': categorie,
                'action': action,
                'module': old_perm.module,
                'url_pattern': old_perm.url_pattern,
                'est_active': old_perm.est_active
            }
        )
        
        print(f"{'✅ Migrée' if created else 'ℹ️  Existe'} : {new_perm.nom} → {categorie.nom}")


def creer_roles_exemples(categories):
    """Créer des rôles exemples pour les utilisateurs non-techniques"""
    print("\n=== CRÉATION DES RÔLES EXEMPLES ===")
    
    roles_data = [
        {
            'nom': 'Gestionnaire Banques',
            'description': 'Peut gérer complètement les banques et comptes',
            'categorie': categories['Banques'],
            'icone': 'bi-bank',
            'couleur': '#007bff',
            'niveau_acces': 2,
            'permissions_codes': ['voir_banques', 'creer_banques', 'modifier_banques']
        },
        {
            'nom': 'Comptable',
            'description': 'Gère les recettes, demandes et états financiers',
            'categorie': categories['Recettes'],
            'icone': 'bi-calculator',
            'couleur': '#28a745',
            'niveau_acces': 3,
            'permissions_codes': ['voir_recettes', 'creer_recettes', 'modifier_recettes', 
                                'voir_demandes', 'creer_demandes', 'voir_etats', 'generer_etats']
        },
        {
            'nom': 'Directeur Financier',
            'description': 'Accès complet à toutes les fonctionnalités financières',
            'categorie': categories['Tableau de bord'],
            'icone': 'bi-briefcase',
            'couleur': '#dc3545',
            'niveau_acces': 5,
            'permissions_codes': ['voir_tableau_bord', 'voir_banques', 'voir_clotures', 
                                'voir_demandes', 'voir_recettes', 'voir_etats', 
                                'valider_demandes', 'effectuer_clotures']
        },
        {
            'nom': 'Opérateur Saisie',
            'description': 'Saisie des demandes et recettes quotidiennes',
            'categorie': categories['Demandes'],
            'icone': 'bi-pencil-square',
            'couleur': '#ffc107',
            'niveau_acces': 1,
            'permissions_codes': ['voir_demandes', 'creer_demandes', 'modifier_demandes',
                                'voir_recettes', 'creer_recettes']
        }
    ]
    
    for role_data in roles_data:
        role, created = NewRole.objects.get_or_create(
            nom=role_data['nom'],
            defaults={k: v for k, v in role_data.items() if k != 'permissions_codes'}
        )
        
        # Ajouter les permissions
        if created:
            for perm_code in role_data['permissions_codes']:
                try:
                    perm = NewPermission.objects.get(code=perm_code)
                    role.permissions.add(perm)
                except NewPermission.DoesNotExist:
                    print(f"⚠️  Permission {perm_code} non trouvée pour le rôle {role.nom}")
        
        print(f"{'✅ Créé' if created else 'ℹ️  Existe'} : {role.nom} ({role.permissions.count()} permissions)")


def main():
    """Fonction principale de migration"""
    print("=== MIGRATION VERS SYSTÈME RBAC CONVIVIAL ===")
    
    # Étape 1 : Créer les catégories
    categories = creer_categories_par_defaut()
    
    # Étape 2 : Migrer les permissions
    migrer_permissions(categories)
    
    # Étape 3 : Créer les rôles exemples
    creer_roles_exemples(categories)
    
    print("\n=== MIGRATION TERMINÉE ===")
    print("Le nouveau système est prêt pour les utilisateurs non-techniques !")


if __name__ == '__main__':
    main()
