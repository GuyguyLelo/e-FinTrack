"""
Système RBAC basé sur les modèles Django (idée géniale de l'utilisateur)
"""
from django.db import models
from django.apps import apps


class PermissionModele(models.Model):
    """Permission basée sur un modèle Django spécifique"""
    
    # Champs pour utilisateurs non-techniques
    nom = models.CharField(max_length=100, verbose_name="Nom de la permission")
    description = models.TextField(verbose_name="Description")
    
    # LIEN DIRECT AVEC LE MODÈLE DJANGO !
    modele_django = models.CharField(max_length=100, verbose_name="Modèle Django")
    app_label = models.CharField(max_length=50, verbose_name="Application Django")
    
    # Actions possibles sur le modèle
    action = models.CharField(max_length=20, choices=[
        ('liste', 'Voir la liste'),
        ('creer', 'Créer'),
        ('modifier', 'Modifier'),
        ('supprimer', 'Supprimer'),
        ('valider', 'Valider'),
        ('exporter', 'Exporter'),
        ('importer', 'Importer'),
    ], verbose_name="Action")
    
    # Champs techniques (générés automatiquement)
    code = models.CharField(max_length=50, unique=True, verbose_name="Code technique")
    url_pattern = models.CharField(max_length=200, blank=True, verbose_name="Pattern URL")
    est_active = models.BooleanField(default=True, verbose_name="Permission active")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Permission de modèle"
        verbose_name_plural = "Permissions de modèles"
        ordering = ['modele_django', 'action']
        unique_together = ['modele_django', 'action']  # Une seule action par modèle
    
    def __str__(self):
        return f"{self.get_action_display()} {self.modele_django}"
    
    def save(self, *args, **kwargs):
        # GÉNÉRATION AUTOMATIQUE DU CODE
        if not self.code:
            self.code = f"{self.action}_{self.modele_django.lower()}"
        
        # GÉNÉRATION AUTOMATIQUE DE L'URL
        if not self.url_pattern:
            self.url_pattern = self.generer_url_pattern()
        
        super().save(*args, **kwargs)
    
    def generer_url_pattern(self):
        """Génère l'URL pattern automatiquement selon le modèle et l'action"""
        # Mapping des actions vers patterns URL
        patterns = {
            'liste': f"/{self.app_label}/{self.modele_django.lower()}/",
            'creer': f"/{self.app_label}/{self.modele_django.lower()}/creer/",
            'modifier': f"/{self.app_label}/{self.modele_django.lower()}/<int:pk>/modifier/",
            'supprimer': f"/{self.app_label}/{self.modele_django.lower()}/<int:pk>/supprimer/",
            'valider': f"/{self.app_label}/{self.modele_django.lower()}/<int:pk>/valider/",
            'exporter': f"/{self.app_label}/{self.modele_django.lower()}/exporter/",
            'importer': f"/{self.app_label}/{self.modele_django.lower()}/importer/",
        }
        return patterns.get(self.action, "")
    
    def get_modele_info(self):
        """Retourne les informations du modèle Django"""
        try:
            app_config = apps.get_app_config(self.app_label)
            model_class = app_config.get_model(self.modele_django)
            
            if model_class:
                return {
                    'nom': model_class._meta.verbose_name,
                    'nom_plural': model_class._meta.verbose_name_plural,
                    'app_label': model_class._meta.app_label,
                    'db_table': model_class._meta.db_table,
                    'fields': [field.name for field in model_class._meta.fields],
                }
        except LookupError:
            pass
        
        return None


class RoleModele(models.Model):
    """Rôle avec permissions basées sur les modèles"""
    
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom du rôle")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code du rôle")
    description = models.TextField(verbose_name="Description du rôle")
    
    # Champs UI/UX
    couleur = models.CharField(max_length=7, default="#007bff", verbose_name="Couleur")
    icone = models.CharField(max_length=50, default="bi-person", verbose_name="Icône")
    
    # Champs de contrôle
    est_actif = models.BooleanField(default=True, verbose_name="Rôle actif")
    est_systeme = models.BooleanField(default=False, verbose_name="Rôle système")
    niveau_acces = models.IntegerField(default=1, verbose_name="Niveau d'accès")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # LIEN DIRECT AVEC LES PERMISSIONS DE MODÈLES
    permissions_modeles = models.ManyToManyField('PermissionModele', verbose_name="Permissions des modèles")
    
    class Meta:
        verbose_name = "Rôle (basé sur modèles)"
        verbose_name_plural = "Rôles (basés sur modèles)"
        ordering = ['niveau_acces', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Limiter le code à 20 caractères max
            self.code = self.nom.upper().replace(' ', '_')[:20]
        super().save(*args, **kwargs)
    
    def a_permission_modele(self, modele_django, action):
        """Vérifier si le rôle a une permission sur un modèle spécifique"""
        return self.permissions_modeles.filter(
            modele_django=modele_django, 
            action=action, 
            est_active=True
        ).exists()
    
    def get_permissions_by_modele(self):
        """Retourne les permissions groupées par modèle"""
        permissions_by_modele = {}
        for perm in self.permissions_modeles.filter(est_active=True):
            if perm.modele_django not in permissions_by_modele:
                permissions_by_modele[perm.modele_django] = []
            permissions_by_modele[perm.modele_django].append(perm)
        return permissions_by_modele


# MÉTHODES POUR L'UTILISATEUR

class UserPermissionMixin:
    """Mixin pour ajouter les méthodes de permissions basées sur les modèles à l'utilisateur"""
    
    def has_permission_modele(self, modele_django, action):
        """Vérifie si l'utilisateur a une permission sur un modèle"""
        if not hasattr(self, 'rbac_role') or not self.rbac_role:
            return False
        
        return self.rbac_role.a_permission_modele(modele_django, action)
    
    def can_view_modele(self, modele_django):
        """Peut voir la liste du modèle"""
        return self.has_permission_modele(modele_django, 'liste')
    
    def can_create_modele(self, modele_django):
        """Peut créer une instance du modèle"""
        return self.has_permission_modele(modele_django, 'creer')
    
    def can_edit_modele(self, modele_django):
        """Peut modifier une instance du modèle"""
        return self.has_permission_modele(modele_django, 'modifier')
    
    def can_delete_modele(self, modele_django):
        """Peut supprimer une instance du modèle"""
        return self.has_permission_modele(modele_django, 'supprimer')
    
    def can_validate_modele(self, modele_django):
        """Peut valider une instance du modèle"""
        return self.has_permission_modele(modele_django, 'valider')
    
    def get_accessible_modeles(self):
        """Retourne la liste des modèles accessibles à l'utilisateur"""
        if not hasattr(self, 'rbac_role') or not self.rbac_role:
            return []
        
        permissions = self.rbac_role.permissions_modeles.filter(est_active=True)
        return list(set(perm.modele_django for perm in permissions))
