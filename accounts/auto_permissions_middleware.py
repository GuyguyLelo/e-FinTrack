"""
Middleware pour donner automatiquement les permissions Django aux utilisateurs ADMIN
"""
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import User


class AutoPermissionsMiddleware:
    """
    Middleware qui donne automatiquement les permissions Django nécessaires
    aux utilisateurs avec des rôles spécifiques
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Ne s'applique qu'aux utilisateurs authentifiés
        if request.user.is_authenticated and hasattr(request.user, 'role'):
            self.ensure_permissions(request.user)
        
        response = self.get_response(request)
        return response
    
    def ensure_permissions(self, user):
        """Assure que l'utilisateur a les permissions nécessaires selon son rôle"""
        
        # Pour les utilisateurs ADMIN, donner les permissions de base
        if user.role == 'ADMIN' and user.user_permissions.count() == 0:
            self.give_admin_permissions(user)
        
        # Pour les SUPER_ADMIN, donner toutes les permissions
        elif user.role == 'SUPER_ADMIN' and not user.is_superuser:
            self.give_superadmin_permissions(user)
    
    def give_admin_permissions(self, user):
        """Donne les permissions nécessaires à un utilisateur ADMIN"""
        try:
            # Permissions sur les modèles User et Service
            content_types = ContentType.objects.filter(
                app_label='accounts',
                model__in=['user', 'service']
            )
            
            # Permissions sur NatureEconomique
            nature_ct = ContentType.objects.filter(
                app_label='demandes',
                model='natureeconomique'
            ).first()
            
            if nature_ct:
                content_types = list(content_types) + [nature_ct]
            
            # Ajouter toutes les permissions (view, add, change) pour ces modèles
            for ct in content_types:
                perms = Permission.objects.filter(content_type=ct)
                user.user_permissions.add(*perms)
            
            print(f"Permissions ADMIN ajoutées pour {user.username}")
            
        except Exception as e:
            print(f"Erreur lors de l'ajout des permissions pour {user.username}: {e}")
    
    def give_superadmin_permissions(self, user):
        """Donne les permissions de superadmin à un utilisateur"""
        try:
            # Rendre l'utilisateur superuser
            user.is_superuser = True
            user.is_staff = True
            user.save()
            
            print(f"Permissions SUPER_ADMIN ajoutées pour {user.username}")
            
        except Exception as e:
            print(f"Erreur lors de l'ajout des permissions superadmin pour {user.username}: {e}")
