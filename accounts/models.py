"""
Modèles pour la gestion des utilisateurs et rôles
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Service(models.Model):
    """Modèle pour les services de la DGRAD avec structure hiérarchique"""
    nom_service = models.CharField(max_length=200, unique=True)
    code_service = models.CharField(max_length=20, blank=True, null=True, verbose_name="Code service")
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    parent_service = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Service parent",
        related_name='services_enfants'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['code_service', 'nom_service']
    
    def __str__(self):
        if self.code_service:
            return f"{self.code_service} - {self.nom_service}"
        return self.nom_service
    
    @property
    def has_children(self):
        """Vérifier si le service a des services enfants"""
        return self.services_enfants.exists()
    
    @property
    def level(self):
        """Calculer le niveau hiérarchique du service"""
        level = 0
        current = self.parent_service
        while current:
            level += 1
            current = current.parent_service
        return level
    
    def get_hierarchy_path(self):
        """Obtenir le chemin hiérarchique complet du service"""
        path = [self.nom_service]
        current = self.parent_service
        while current:
            path.append(current.nom_service)
            current = current.parent_service
        return " > ".join(reversed(path))
    
    def get_all_children(self):
        """Obtenir tous les services enfants (récursivement)"""
        children = []
        for child in self.services_enfants.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé avec rôles DGRAD
    """
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('DG', 'Directeur Général'),
        ('DF', 'Directeur Financier'),
        ('CD_FINANCE', 'Chef de Division Finance'),
        ('OPERATEUR_SAISIE', 'Opérateur de Saisie'),
        ('AGENT_PAYEUR', 'Agent Payeur'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OPERATEUR_SAISIE')
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
    def is_super_admin(self):
        return self.role == 'SUPER_ADMIN'
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN'
    
    @property
    def is_dg(self):
        return self.role == 'DG'
    
    @property
    def is_df(self):
        return self.role == 'DF'
    
    @property
    def is_cd_finance(self):
        return self.role == 'CD_FINANCE'
    
    @property
    def is_operateur_saisie(self):
        return self.role == 'OPERATEUR_SAISIE'
    
    @property
    def is_agent_payeur(self):
        return self.role == 'AGENT_PAYEUR'
    
    @property
    def is_comptable(self):
        """Rôles pouvant valider les recettes (CD Finance, DF, DG, Admin)."""
        return self.role in ['SUPER_ADMIN', 'ADMIN', 'DG', 'DF', 'CD_FINANCE']
    
    # Permissions d'accès
    def peut_voir_tableau_bord(self):
        """Vérifie si l'utilisateur peut voir le tableau de bord"""
        return self.role in ['SUPER_ADMIN', 'DG', 'DF', 'CD_FINANCE']
    
    def peut_creer_entites_base(self):
        """Vérifie si l'utilisateur peut créer les entités de base (banques, comptes, utilisateurs, services, nature économique)"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    def peut_voir_tout_sans_modification(self):
        """Vérifie si l'utilisateur peut tout voir sans modification"""
        return self.role in ['SUPER_ADMIN', 'DG', 'DF']
    
    def peut_valider_demandes(self):
        """Vérifie si l'utilisateur peut valider les demandes"""
        return self.role in ['SUPER_ADMIN', 'DG']
    
    def peut_valider_depense(self):
        """Vérifie si l'utilisateur peut valider les dépenses dans les relevés"""
        return self.role in ['SUPER_ADMIN', 'DG']
    
    def peut_effectuer_paiements(self):
        """Vérifie si l'utilisateur peut effectuer les paiements"""
        return self.role in ['SUPER_ADMIN', 'AGENT_PAYEUR']
    
    def peut_voir_paiements(self):
        """Vérifie si l'utilisateur peut voir les paiements"""
        return self.role in ['SUPER_ADMIN', 'DG', 'DF', 'CD_FINANCE', 'AGENT_PAYEUR']
    
    def peut_creer_releves(self):
        """Vérifie si l'utilisateur peut créer des relevés"""
        return self.role in ['SUPER_ADMIN', 'CD_FINANCE']
    
    def peut_consulter_depenses(self):
        """Vérifie si l'utilisateur peut consulter les dépenses"""
        return self.role in ['SUPER_ADMIN', 'DG', 'DF', 'CD_FINANCE', 'OPERATEUR_SAISIE']
    
    def peut_voir_menu_depenses(self):
        """Vérifie si l'utilisateur peut voir le menu Dépenses (opérateur, CD Finance, DG, DF)"""
        return self.role in ['SUPER_ADMIN', 'DG', 'DF', 'CD_FINANCE', 'OPERATEUR_SAISIE']
    
    def peut_creer_etats(self):
        """Vérifie si l'utilisateur peut créer des états"""
        return self.role in ['SUPER_ADMIN', 'CD_FINANCE']
    
    def peut_saisir_demandes_recettes(self):
        """Vérifie si l'utilisateur peut saisir des demandes et recettes"""
        return self.role in ['SUPER_ADMIN', 'OPERATEUR_SAISIE', 'ADMIN', 'DG', 'CD_FINANCE']
    
    def peut_acceder_admin_django(self):
        """Vérifie si l'utilisateur peut accéder à l'administration Django"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    def peut_voir_menu_demandes(self):
        """Vérifie si l'utilisateur peut voir le menu demandes"""
        return self.role in ['SUPER_ADMIN', 'DG', 'DF', 'CD_FINANCE', 'AGENT_PAYEUR', 'OPERATEUR_SAISIE']
    
    def peut_voir_menu_paiements(self):
        """Vérifie si l'utilisateur peut voir le menu paiements"""
        return self.role in ['SUPER_ADMIN', 'DG', 'DF', 'CD_FINANCE', 'AGENT_PAYEUR']
    
    def peut_voir_menu_recettes(self):
        """Vérifie si l'utilisateur peut voir le menu recettes"""
        return self.role in ['SUPER_ADMIN', 'DG', 'CD_FINANCE', 'OPERATEUR_SAISIE']
    
    def peut_voir_menu_etats(self):
        """Vérifie si l'utilisateur peut voir le menu états"""
        return self.role in ['SUPER_ADMIN', 'CD_FINANCE']
    
    def peut_voir_menu_banques(self):
        """Vérifie si l'utilisateur peut voir le menu banques"""
        return self.role in ['SUPER_ADMIN']
    
    def peut_voir_uniquement_tableau_bord_feuille(self):
        """Vérifie si l'utilisateur ne peut voir que le tableau de bord feuille"""
        return self.role in ['DG', 'CD_FINANCE']
    
    def peut_ajouter_nature_economique(self):
        """Vérifie si l'utilisateur peut ajouter des natures économiques"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    def peut_ajouter_recette_depense(self):
        """Vérifie si l'utilisateur peut ajouter des recettes et dépenses"""
        return self.role in ['SUPER_ADMIN', 'ADMIN', 'OPERATEUR_SAISIE']
    
    def peut_generer_etats(self):
        """Vérifie si l'utilisateur peut générer les états"""
        return self.role in ['SUPER_ADMIN', 'ADMIN', 'OPERATEUR_SAISIE']

