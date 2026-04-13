"""
Template tags pour le système RBAC
"""
from django import template

register = template.Library()


@register.filter
def has_rbac_permission(user, permission_code):
    """Vérifie si l'utilisateur a une permission RBAC spécifique"""
    if not user or not user.is_authenticated:
        return False
    
    try:
        return user.has_rbac_permission(permission_code)
    except:
        return False


@register.filter
def can_access_module(user, module_name):
    """Vérifie si l'utilisateur peut accéder à un module spécifique"""
    if not user or not user.is_authenticated:
        return False
    
    # Mapping des modules vers les permissions requises (nouveau système RBAC)
    module_permissions = {
        'banques': ('mouvementbancaire', 'liste'),
        'clotures': ('cloturemensuelle', 'liste'),
        'demandes': ('paiement', 'liste'),
        'recettes': ('recette', 'liste'),
        'depenses': ('relevedepense', 'liste'),
        'etats': ('etat', 'liste'),
        'tableau_bord': ('Dashboard', 'voir'),
    }
    
    required_permission = module_permissions.get(module_name)
    if not required_permission:
        return False
    
    modele_django, action = required_permission
    
    # Essayer avec le nouveau système RBAC (basé sur les modèles)
    if hasattr(user, 'rbac_role_modele') and user.rbac_role_modele:
        if hasattr(user, 'has_permission_modele'):
            return user.has_permission_modele(modele_django, action)
    
    # Essayer avec l'ancien système RBAC
    if hasattr(user, 'rbac_role') and user.rbac_role:
        if hasattr(user, 'has_rbac_permission'):
            # Mapping pour l'ancien système
            legacy_mapping = {
                'banques': 'voir_banques',
                'clotures': 'voir_clotures',
                'demandes': 'voir_demandes',
                'recettes': 'voir_recettes',
                'depenses': 'voir_depenses',
                'etats': 'voir_etats',
                'tableau_bord': 'voir_tableau_bord',
            }
            legacy_perm = legacy_mapping.get(module_name)
            if legacy_perm:
                return user.has_rbac_permission(legacy_perm)
    
    return False


@register.simple_tag
def generate_dynamic_menu(user):
    """Génère dynamiquement le menu selon les permissions de l'utilisateur"""
    if not user or not user.is_authenticated:
        return ""
    
    if not hasattr(user, 'rbac_role_modele') or not user.rbac_role_modele:
        return ""
    
    # Mapping des permissions vers les informations de menu
    menu_items = {
        'user': {
            'url': '/accounts/utilisateurs/',
            'icon': 'bi-people',
            'label': 'Gestion des Utilisateurs',
            'description': 'Gérer les utilisateurs du système'
        },
        'mouvementbancaire': {
            'url': '/banques/',
            'icon': 'bi-bank',
            'label': 'Banques',
            'description': 'Gérer les mouvements bancaires'
        },
        'paiement': {
            'url': '/demandes/',
            'icon': 'bi-file-earmark-text',
            'label': 'Demandes',
            'description': 'Gérer les demandes de paiement'
        },
        'recette': {
            'url': '/recettes/feuille/',
            'icon': 'bi-cash-stack',
            'label': 'Recettes',
            'description': 'Gérer les recettes'
        },
        'relevedepense': {
            'url': '/demandes/depenses/feuille/',
            'icon': 'bi-wallet2',
            'label': 'Dépenses',
            'description': 'Gérer les dépenses'
        },
        'cloturemensuelle': {
            'url': '/clotures/',
            'icon': 'bi-calendar-check',
            'label': 'Clôtures',
            'description': 'Gérer les clôtures mensuelles'
        },
        'Dashboard': {
            'url': '/',
            'icon': 'bi-speedometer2',
            'label': 'Tableau de bord',
            'description': 'Tableau de bord principal'
        },
        'etat': {
            'url': '/tableau-bord-feuilles/etats-depenses/',
            'icon': 'bi-file-text',
            'label': 'États',
            'description': 'Générer les états financiers'
        }
    }
    
    menu_html = ""
    
    # Obtenir toutes les permissions du rôle
    if hasattr(user, 'rbac_role_modele') and user.rbac_role_modele:
        permissions = user.rbac_role_modele.permissions_modeles.all()
        
        # Générer les items de menu dynamiquement
        for permission in permissions:
            modele = permission.modele_django
            action = permission.action
            
            # Vérifier si on a une action de type 'liste' pour afficher le menu
            if action in ['liste', 'voir'] and modele in menu_items:
                item = menu_items[modele]
                menu_html += f'<a class="nav-link" href="{item["url"]}"><i class="{item["icon"]}"></i> {item["label"]}</a>'
    
    return menu_html


@register.simple_tag
def get_user_menu_title(user):
    """Retourne le titre du menu pour l'utilisateur"""
    if user and user.is_authenticated:
        if hasattr(user, 'rbac_role_modele') and user.rbac_role_modele:
            return user.rbac_role_modele.nom
        elif hasattr(user, 'rbac_role') and user.rbac_role:
            return user.rbac_role.nom
    return "Menu"
