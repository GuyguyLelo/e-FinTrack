"""
Modèles pour la gestion des utilisateurs et rôles
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Service(models.Model):
    """Modèle pour les services de la DGRAD"""
    nom_service = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['nom_service']
    
    def __str__(self):
        return self.nom_service


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec rôles DGRAD
    """
    ROLE_CHOICES = [
        ('DG', 'Directeur Général'),
        ('DAF', 'Directeur Administratif et Financier'),
        ('DF', 'Directeur Financier'),
        ('COMPTABLE', 'Comptable'),
        ('CHEF_SERVICE', 'Chef de Service'),
        ('AUDITEUR', 'Auditeur'),
        ('OPERATEUR_SAISIE', 'Opérateur de Saisie'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OPERATEUR_SAISIE')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='membres')
    telephone = models.CharField(max_length=20, blank=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_dg(self):
        return self.role == 'DG'
    
    @property
    def is_daf(self):
        return self.role == 'DAF'
    
    @property
    def is_df(self):
        return self.role == 'DF'
    
    @property
    def is_comptable(self):
        return self.role == 'COMPTABLE'
    
    @property
    def is_chef_service(self):
        return self.role == 'CHEF_SERVICE'
    
    @property
    def is_auditeur(self):
        return self.role == 'AUDITEUR'
    
    @property
    def is_operateur_saisie(self):
        return self.role == 'OPERATEUR_SAISIE'
    
    def peut_valider_depense(self):
        """Vérifie si l'utilisateur peut valider une dépense"""
        return self.role in ['DG', 'DAF', 'DF']
    
    def peut_valider_releve(self):
        """Vérifie si l'utilisateur peut valider un relevé bancaire"""
        return self.role in ['COMPTABLE', 'DF']
    
    def peut_valider_rapprochement(self):
        """Vérifie si l'utilisateur peut valider un rapprochement"""
        return self.role == 'AUDITEUR'
    
    def peut_consulter_tout(self):
        """Vérifie si l'utilisateur peut tout consulter"""
        return self.role in ['DG', 'DAF', 'DF', 'AUDITEUR']

