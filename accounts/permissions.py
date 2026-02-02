"""
Décorateurs et mixins de permissions pour la gestion des accès
"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin pour vérifier les permissions basées sur les rôles"""
    
    required_roles = []
    permission_function = None
    
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        
        if self.permission_function:
            return getattr(user, self.permission_function)()
        elif self.required_roles:
            return user.role in self.required_roles
        
        return False
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        
        messages.error(self.request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('rapports:dashboard')


def role_required(roles=None, permission_function=None):
    """
    Décorateur pour vérifier les permissions basées sur les rôles
    
    Usage:
        @role_required(roles=['SUPER_ADMIN', 'ADMIN'])
        def ma_vue(request):
            pass
        
        @role_required(permission_function='peut_voir_tableau_bord')
        def ma_vue(request):
            pass
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if permission_function:
                if not getattr(request.user, permission_function)():
                    messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
                    return redirect('rapports:dashboard')
            elif roles:
                if request.user.role not in roles:
                    messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
                    return redirect('rapports:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Décorateurs spécifiques pour chaque type de permission
def super_admin_required(view_func):
    """Nécessite le rôle Super Admin"""
    return role_required(roles=['SUPER_ADMIN'])(view_func)


def admin_required(view_func):
    """Nécessite le rôle Admin ou Super Admin"""
    return role_required(roles=['SUPER_ADMIN', 'ADMIN'])(view_func)


def dg_required(view_func):
    """Nécessite le rôle DG ou Super Admin"""
    return role_required(roles=['SUPER_ADMIN', 'DG'])(view_func)


def df_required(view_func):
    """Nécessite le rôle DF ou Super Admin"""
    return role_required(roles=['SUPER_ADMIN', 'DF'])(view_func)


def cd_finance_required(view_func):
    """Nécessite le rôle CD Finance ou Super Admin"""
    return role_required(roles=['SUPER_ADMIN', 'CD_FINANCE'])(view_func)


def operateur_saisie_required(view_func):
    """Nécessite le rôle Opérateur de Saisie ou Super Admin"""
    return role_required(roles=['SUPER_ADMIN', 'OPERATEUR_SAISIE'])(view_func)


def agent_payeur_required(view_func):
    """Nécessite le rôle Agent Payeur ou Super Admin"""
    return role_required(roles=['SUPER_ADMIN', 'AGENT_PAYEUR'])(view_func)


def tableau_bord_required(view_func):
    """Nécessite la permission de voir le tableau de bord"""
    return role_required(permission_function='peut_voir_tableau_bord')(view_func)


def creer_entites_base_required(view_func):
    """Nécessite la permission de créer les entités de base"""
    return role_required(permission_function='peut_creer_entites_base')(view_func)


def valider_demandes_required(view_func):
    """Nécessite la permission de valider les demandes"""
    return role_required(permission_function='peut_valider_demandes')(view_func)


def effectuer_paiements_required(view_func):
    """Nécessite la permission d'effectuer les paiements"""
    return role_required(permission_function='peut_effectuer_paiements')(view_func)


def consulter_depenses_required(view_func):
    """Nécessite la permission de consulter les dépenses"""
    return role_required(permission_function='peut_consulter_depenses')(view_func)


def saisir_demandes_recettes_required(view_func):
    """Nécessite la permission de saisir des demandes et recettes"""
    return role_required(permission_function='peut_saisir_demandes_recettes')(view_func)


# Mixins spécifiques pour les vues basées sur les classes
class RoleRequiredMixin(RoleRequiredMixin):
    """Mixin pour les vues basées sur les classes avec vérification des rôles"""
    pass


class TableauBordMixin(RoleRequiredMixin):
    """Mixin pour l'accès au tableau de bord"""
    permission_function = 'peut_voir_tableau_bord'


class CreerEntitesBaseMixin(RoleRequiredMixin):
    """Mixin pour la création des entités de base"""
    permission_function = 'peut_creer_entites_base'


class ValiderDemandesMixin(RoleRequiredMixin):
    """Mixin pour la validation des demandes"""
    permission_function = 'peut_valider_demandes'


class EffectuerPaiementsMixin(RoleRequiredMixin):
    """Mixin pour l'effection des paiements"""
    permission_function = 'peut_effectuer_paiements'


class ConsulterDepensesMixin(RoleRequiredMixin):
    """Mixin pour la consultation des dépenses"""
    permission_function = 'peut_consulter_depenses'


class SaisirDemandesRecettesMixin(RoleRequiredMixin):
    """Mixin pour la saisie des demandes et recettes"""
    permission_function = 'peut_saisir_demandes_recettes'
