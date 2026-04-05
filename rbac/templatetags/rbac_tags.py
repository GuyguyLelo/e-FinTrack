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
    
    # Mapping des modules vers les permissions requises
    module_permissions = {
        'banques': ['creer_banques', 'modifier_banques', 'voir_banques'],
        'clotures': ['effectuer_clotures', 'rouvrir_clotures', 'voir_clotures'],
        'demandes': ['creer_demandes', 'modifier_demandes', 'valider_demandes'],
        'recettes': ['creer_recettes', 'modifier_recettes', 'voir_recettes'],
        'etats': ['voir_etats'],
        'tableau_bord': ['voir_tableau_bord'],
    }
    
    required_permissions = module_permissions.get(module_name, [])
    
    for perm_code in required_permissions:
        try:
            if user.has_rbac_permission(perm_code):
                return True
        except:
            continue
    
    return False


@register.simple_tag
def get_user_menu_title(user):
    """Retourne le titre du menu pour l'utilisateur"""
    if user and user.is_authenticated and user.rbac_role:
        return user.rbac_role.nom
    return "Menu"
