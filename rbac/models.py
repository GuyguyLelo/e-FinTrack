"""
Modèles pour la gestion dynamique des rôles et permissions
"""
from django.db import models
from django.conf import settings


class Permission(models.Model):
    """Modèle pour stocker les permissions du système"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la permission")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code de la permission")
    description = models.TextField(blank=True, verbose_name="Description")
    module = models.CharField(max_length=50, verbose_name="Module concerné")
    url_pattern = models.CharField(max_length=200, blank=True, verbose_name="Pattern URL")
    est_active = models.BooleanField(default=True, verbose_name="Permission active")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['module', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"


class Role(models.Model):
    """Modèle pour les rôles personnalisés"""
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom du rôle")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code du rôle")
    description = models.TextField(blank=True, verbose_name="Description")
    couleur = models.CharField(max_length=7, default="#007bff", verbose_name="Couleur (hex)")
    icone = models.CharField(max_length=50, default="bi-person", verbose_name="Icône Bootstrap")
    est_actif = models.BooleanField(default=True, verbose_name="Rôle actif")
    est_systeme = models.BooleanField(default=False, verbose_name="Rôle système (non modifiable)")
    date_creation = models.DateTimeField(auto_now_add=True)
    permissions = models.ManyToManyField('Permission', blank=True, verbose_name="Permissions")
    
    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"
    
    def a_permission(self, code_permission):
        """Vérifier si le rôle a une permission spécifique"""
        return self.permissions.filter(code=code_permission, est_active=True).exists()


# Supprimer la classe RolePermission car nous utilisons le M2M directement


class UserProfile(models.Model):
    """Profil utilisateur avec rôle personnalisé"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Utilisateur")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name="Rôle")
    service = models.ForeignKey('accounts.Service', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Service")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    est_actif = models.BooleanField(default=True, verbose_name="Profil actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.nom}"
    
    def a_permission(self, code_permission):
        """Vérifier si l'utilisateur a une permission via son rôle"""
        return self.role.a_permission(code_permission) if self.role else False
    
    def get_permissions_codes(self):
        """Obtenir la liste des codes de permissions de l'utilisateur"""
        if not self.role:
            return []
        return list(self.role.permissions.filter(est_active=True).values_list('code', flat=True))
