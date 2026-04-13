from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse
from django.conf import settings


class SmartDashboardView(LoginRequiredMixin, TemplateView):
    """Tableau de bord intelligent qui affiche seulement les modules accessibles"""
    template_name = 'accounts/smart_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Informations sur l'utilisateur
        context['user_info'] = {
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'role_display': self.get_role_display(user),
            'role_badge_color': self.get_role_badge_color(user),
        }
        
        # Modules accessibles selon les permissions RBAC
        context['accessible_modules'] = self.get_accessible_modules(user)
        
        # Statistiques sur les permissions
        context['permissions_stats'] = {
            'total_modules': len(self.get_all_available_modules()),
            'accessible_count': len(context['accessible_modules']),
            'access_percentage': self.calculate_access_percentage(user),
        }
        
        return context
    
    def get_role_display(self, user):
        """Retourne l'affichage du rôle de l'utilisateur"""
        if hasattr(user, 'rbac_role_modele') and user.rbac_role_modele:
            return user.rbac_role_modele.nom
        elif hasattr(user, 'rbac_role') and user.rbac_role:
            return user.rbac_role.nom
        elif hasattr(user, 'get_role_display'):
            return user.get_role_display()
        return "Non défini"
    
    def get_role_badge_color(self, user):
        """Retourne la couleur du badge selon le rôle"""
        if hasattr(user, 'rbac_role_modele') and user.rbac_role_modele:
            return user.rbac_role_modele.couleur or '#007bff'
        elif hasattr(user, 'rbac_role') and user.rbac_role:
            return '#17a2b8'  # Bleu pour l'ancien système
        else:
            return '#6c757d'  # Gris par défaut
    
    def get_all_available_modules(self):
        """Retourne tous les modules disponibles dans le système"""
        return [
            {
                'id': 'tableau_bord',
                'name': 'Tableau de bord',
                'icon': 'bi-speedometer2',
                'url': '/',
                'description': 'Vue d\'ensemble des activités',
                'modele_django': 'Dashboard',
                'action': 'voir',
                'category': 'principal',
                'priority': 1,
            },
            {
                'id': 'banques',
                'name': 'Banques',
                'icon': 'bi-bank',
                'url': '/banques/',
                'description': 'Gestion des mouvements bancaires',
                'modele_django': 'mouvementbancaire',
                'action': 'liste',
                'category': 'finance',
                'priority': 2,
            },
            {
                'id': 'demandes',
                'name': 'Demandes',
                'icon': 'bi-file-text',
                'url': '/demandes/',
                'description': 'Gestion des demandes de paiement',
                'modele_django': 'paiement',
                'action': 'liste',
                'category': 'finance',
                'priority': 3,
            },
            {
                'id': 'recettes',
                'name': 'Recettes',
                'icon': 'bi-cash-stack',
                'url': '/recettes/',
                'description': 'Gestion des recettes',
                'modele_django': 'recette',
                'action': 'liste',
                'category': 'finance',
                'priority': 4,
            },
            {
                'id': 'depenses',
                'name': 'Dépenses',
                'icon': 'bi-wallet2',
                'url': '/demandes/depenses/',
                'description': 'Gestion des dépenses',
                'modele_django': 'relevedepense',
                'action': 'liste',
                'category': 'finance',
                'priority': 5,
            },
            {
                'id': 'clotures',
                'name': 'Clôtures',
                'icon': 'bi-calendar-check',
                'url': '/clotures/',
                'description': 'Gestion des clôtures mensuelles',
                'modele_django': 'cloturemensuelle',
                'action': 'liste',
                'category': 'administration',
                'priority': 6,
            },
            {
                'id': 'utilisateurs',
                'name': 'Utilisateurs',
                'icon': 'bi-people',
                'url': '/accounts/utilisateurs/',
                'description': 'Gestion des utilisateurs',
                'modele_django': 'User',
                'action': 'liste',
                'category': 'administration',
                'priority': 7,
            },
            {
                'id': 'services',
                'name': 'Services',
                'icon': 'bi-building',
                'url': '/accounts/services/',
                'description': 'Gestion des services',
                'modele_django': 'Service',
                'action': 'liste',
                'category': 'administration',
                'priority': 8,
            },
            {
                'id': 'etats',
                'name': 'États',
                'icon': 'bi-file-text',
                'url': '/etats/',
                'description': 'Génération des états financiers',
                'modele_django': 'etat',
                'action': 'liste',
                'category': 'reporting',
                'priority': 9,
            },
        ]
    
    def get_accessible_modules(self, user):
        """Retourne les modules accessibles par l'utilisateur selon ses permissions"""
        all_modules = self.get_all_available_modules()
        accessible_modules = []
        
        for module in all_modules:
            # Vérifier les permissions selon le système RBAC
            has_permission = False
            
            # Nouveau système RBAC (priorité)
            if hasattr(user, 'rbac_role_modele') and user.rbac_role_modele:
                if hasattr(user, 'has_permission_modele'):
                    has_permission = user.has_permission_modele(module['modele_django'], module['action'])
            
            # Ancien système RBAC (fallback)
            elif hasattr(user, 'rbac_role') and user.rbac_role:
                if hasattr(user, 'can_access_module'):
                    has_permission = user.can_access_module(module['id'])
            
            # Système legacy (fallback)
            else:
                # Pour les utilisateurs sans RBAC, utiliser la logique legacy
                if module['id'] == 'tableau_bord' and user.role in ['SUPER_ADMIN', 'DG', 'CD_FINANCE']:
                    has_permission = True
                elif module['id'] == 'utilisateurs' and user.role in ['SUPER_ADMIN', 'ADMIN']:
                    has_permission = True
                elif module['id'] == 'services' and user.role in ['SUPER_ADMIN', 'ADMIN']:
                    has_permission = True
                elif module['id'] in ['banques', 'demandes', 'recettes', 'depenses'] and user.role in ['SUPER_ADMIN', 'DG', 'DF', 'CD_FINANCE']:
                    has_permission = True
                elif module['id'] == 'clotures' and user.role in ['SUPER_ADMIN', 'DG', 'DF']:
                    has_permission = True
                elif module['id'] == 'etats' and user.role in ['SUPER_ADMIN', 'DG', 'DF', 'CD_FINANCE']:
                    has_permission = True
            
            if has_permission:
                accessible_modules.append(module)
        
        # Trier par priorité
        accessible_modules.sort(key=lambda x: x['priority'])
        return accessible_modules
    
    def calculate_access_percentage(self, user):
        """Calcule le pourcentage d'accès aux modules"""
        all_modules = self.get_all_available_modules()
        accessible_modules = self.get_accessible_modules(user)
        
        if not all_modules:
            return 0
        
        return round((len(accessible_modules) / len(all_modules)) * 100, 1)
