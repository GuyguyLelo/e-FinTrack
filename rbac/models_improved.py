"""
Modèles améliorés pour la gestion des permissions avec interface utilisateur simple
"""
from django.db import models
from django.conf import settings


class CategoriePermission(models.Model):
    """Catégories de permissions pour les utilisateurs non-techniques"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    description = models.TextField(verbose_name="Description")
    icone = models.CharField(max_length=50, default="bi-folder", verbose_name="Icône Bootstrap")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    est_active = models.BooleanField(default=True, verbose_name="Catégorie active")
    
    class Meta:
        verbose_name = "Catégorie de permission"
        verbose_name_plural = "Catégories de permissions"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom


class Permission(models.Model):
    """Modèle amélioré pour les permissions avec interface utilisateur simple"""
    # Champs pour utilisateurs non-techniques
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la permission")
    description = models.TextField(verbose_name="Description")
    categorie = models.ForeignKey(CategoriePermission, on_delete=models.CASCADE, verbose_name="Catégorie")
    
    # Champs techniques (gérés automatiquement)
    code = models.CharField(max_length=50, unique=True, verbose_name="Code technique")
    module = models.CharField(max_length=50, verbose_name="Module technique")
    action = models.CharField(max_length=20, choices=[
        ('voir', 'Voir'),
        ('creer', 'Créer'),
        ('modifier', 'Modifier'),
        ('supprimer', 'Supprimer'),
        ('valider', 'Valider'),
        ('effectuer', 'Effectuer'),
        ('generer', 'Générer'),
    ], verbose_name="Action")
    
    # Champs optionnels
    url_pattern = models.CharField(max_length=200, blank=True, verbose_name="Pattern URL (optionnel)")
    est_active = models.BooleanField(default=True, verbose_name="Permission active")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['categorie__ordre', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"
    
    def save(self, *args, **kwargs):
        # Générer automatiquement le code si non fourni
        if not self.code:
            self.code = f"{self.action}_{self.categorie.nom.lower().replace(' ', '_')}"
        
        # Générer automatiquement le module si non fourni
        if not self.module:
            self.module = self.categorie.nom.lower().replace(' ', '_')
        
        super().save(*args, **kwargs)


class Role(models.Model):
    """Modèle amélioré pour les rôles avec interface utilisateur simple"""
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom du rôle")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code du rôle")
    description = models.TextField(verbose_name="Description du rôle")
    categorie = models.ForeignKey(CategoriePermission, on_delete=models.SET_NULL, null=True, blank=True, 
                               verbose_name="Catégorie principale", help_text="Catégorie principale de ce rôle")
    
    # Champs UI/UX
    couleur = models.CharField(max_length=7, default="#007bff", verbose_name="Couleur (hex)")
    icone = models.CharField(max_length=50, default="bi-person", verbose_name="Icône Bootstrap")
    
    # Champs de contrôle
    est_actif = models.BooleanField(default=True, verbose_name="Rôle actif")
    est_systeme = models.BooleanField(default=False, verbose_name="Rôle système (non modifiable)")
    niveau_acces = models.IntegerField(default=1, verbose_name="Niveau d'accès", 
                                     help_text="1=Bas, 5=Élevé")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    permissions = models.ManyToManyField('Permission', blank=True, verbose_name="Permissions")
    
    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['niveau_acces', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"
    
    def save(self, *args, **kwargs):
        # Générer automatiquement le code si non fourni
        if not self.code:
            self.code = self.nom.upper().replace(' ', '_')[:20]
        super().save(*args, **kwargs)
    
    def a_permission(self, code_permission):
        """Vérifier si le rôle a une permission spécifique"""
        return self.permissions.filter(code=code_permission, est_active=True).exists()
    
    def get_permissions_by_category(self):
        """Retourner les permissions groupées par catégorie"""
        permissions_by_category = {}
        for perm in self.permissions.filter(est_active=True):
            if perm.categorie not in permissions_by_category:
                permissions_by_category[perm.categorie] = []
            permissions_by_category[perm.categorie].append(perm)
        return permissions_by_category
