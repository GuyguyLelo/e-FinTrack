"""
Modèles pour l'application accounts
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from rbac.models_modele import UserPermissionMixin


class Service(models.Model):
    """Modèle pour les services de la DGRAD avec structure hiérarchique"""
    nom_service = models.CharField(max_length=200, unique=True)
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
        ordering = ['nom_service']
    
    def __str__(self):
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


class User(AbstractUser, UserPermissionMixin):
    """
    Modèle utilisateur personnalisé avec rôles DGRAD
    """
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('DG', 'Directeur Général'),
        ('DIRECTEUR', 'Directeur'),
        ('DF', 'Directeur Financier'),
        ('CD_FINANCE', 'Chef de Division Finance'),
        ('OPERATEUR_SAISIE', 'Opérateur de Saisie'),
        ('AGENT_PAYEUR', 'Agent Payeur'),
        ('OpsDaf', 'Opérateur DAF'),
        ('DirDaf', 'Direction DAF'),
        ('DivDaf', 'Division DAF'),
        ('AdminDaf', 'Admin DAF'),
    ]
    
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='OPERATEUR_SAISIE')
    rbac_role = models.ForeignKey(
        'rbac.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Rôle RBAC",
        related_name='users'
    )
    rbac_role_modele = models.ForeignKey(
        'rbac.RoleModele',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Rôle RBAC (basé sur modèles)",
        related_name='users_modele'
    )
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
    
    def sync_rbac_role(self):
        """Synchroniser automatiquement le rôle RBAC avec le rôle existant"""
        try:
            from rbac.models import Role
            rbac_role = Role.objects.get(code=self.role)
            self.rbac_role = rbac_role
            self.save(update_fields=['rbac_role'])
        except Role.DoesNotExist:
            # Si le rôle RBAC n'existe pas, le créer
            pass
    
    def get_rbac_permissions(self):
        """Obtenir les permissions RBAC de l'utilisateur"""
        if self.rbac_role:
            return self.rbac_role.permissions.all()
        return Permission.objects.none()
    
    def has_rbac_permission(self, permission_code):
        """Vérifier si l'utilisateur a une permission RBAC spécifique"""
        if self.rbac_role:
            return self.rbac_role.permissions.filter(code=permission_code).exists()
        return False
    
    @property
    def is_comptable(self):
        """Rôles pouvant valider les recettes (CD Finance, DF, DG, Admin)."""
        return self.role in ['SUPER_ADMIN', 'ADMIN', 'DG', 'DF', 'CD_FINANCE']
    
    # Permissions d'accès - Configurées pour correspondre au template
    def peut_voir_tableau_bord(self):
        """Vérifie si l'utilisateur peut voir le tableau de bord standard"""
        return self.role in ['SUPER_ADMIN', 'DG', 'DF', 'CD_FINANCE']
    
    def peut_acceder_tableau_bord_feuilles(self):
        """Vérifie si l'utilisateur peut accéder au tableau de bord feuilles (DAF)"""
        return self.role in ['SUPER_ADMIN', 'OpsDaf', 'DirDaf', 'DivDaf', 'AdminDaf', 'DG', 'DF', 'CD_FINANCE']
    
    def peut_voir_menu_depenses_daf(self):
        """Vérifie si l'utilisateur peut voir le menu gestion dépenses DAF"""
        return self.role in ['SUPER_ADMIN', 'OpsDaf']
    
    def peut_voir_menu_recettes_daf(self):
        """Vérifie si l'utilisateur peut voir le menu gestion recettes DAF"""
        return self.role in ['SUPER_ADMIN', 'OpsDaf']
    
    def peut_voir_menu_etats_daf(self):
        """Vérifie si l'utilisateur peut voir le menu états DAF"""
        return self.role in ['SUPER_ADMIN', 'OpsDaf', 'CD_FINANCE']
    
    def peut_voir_menu_clotures(self):
        """Vérifie si l'utilisateur peut voir le menu clôtures"""
        return self.role in ['SUPER_ADMIN', 'DirDaf', 'DivDaf']
    
    def peut_gerer_natures_services_daf(self):
        """Vérifie si l'utilisateur peut gérer les natures et services DAF"""
        return self.role in ['SUPER_ADMIN', 'AdminDaf']
    
    def peut_gerer_natures_services_admin(self):
        """Vérifie si l'utilisateur peut gérer les natures et services (ADMIN)"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    def peut_gerer_utilisateurs(self):
        """Vérifie si l'utilisateur peut gérer les utilisateurs"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    def peut_voir_menu_demandes_admin(self):
        """Vérifie si l'utilisateur peut voir le menu demandes (ADMIN)"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    def peut_voir_menu_recettes_admin(self):
        """Vérifie si l'utilisateur peut voir le menu recettes (ADMIN)"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    def peut_voir_menu_paiements_admin(self):
        """Vérifie si l'utilisateur peut voir le menu paiements (ADMIN)"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
    def peut_voir_menu_demandes_dg(self):
        """Vérifie si l'utilisateur peut voir le menu demandes (DG)"""
        return self.role in ['SUPER_ADMIN', 'DG']
    
    def peut_voir_menu_paiements_dg(self):
        """Vérifie si l'utilisateur peut voir le menu paiements (DG)"""
        return self.role in ['SUPER_ADMIN', 'DG']
    
    def peut_valider_demandes_dg(self):
        """Vérifie si l'utilisateur peut valider les demandes (DG)"""
        return self.role in ['SUPER_ADMIN', 'DG']
    
    def peut_voir_menu_demandes_df(self):
        """Vérifie si l'utilisateur peut voir le menu demandes (DF)"""
        return self.role in ['SUPER_ADMIN', 'DF']
    
    def peut_voir_menu_recettes_df(self):
        """Vérifie si l'utilisateur peut voir le menu recettes (DF)"""
        return self.role in ['SUPER_ADMIN', 'DF']
    
    def peut_voir_menu_paiements_df(self):
        """Vérifie si l'utilisateur peut voir le menu paiements (DF)"""
        return self.role in ['SUPER_ADMIN', 'DF']
    
    def peut_voir_menu_demandes_cdf(self):
        """Vérifie si l'utilisateur peut voir le menu demandes (CD_FINANCE)"""
        return self.role in ['SUPER_ADMIN', 'CD_FINANCE']
    
    def peut_voir_menu_recettes_cdf(self):
        """Vérifie si l'utilisateur peut voir le menu recettes (CD_FINANCE)"""
        return self.role in ['SUPER_ADMIN', 'CD_FINANCE']
    
    def peut_voir_menu_paiements_cdf(self):
        """Vérifie si l'utilisateur peut voir le menu paiements (CD_FINANCE)"""
        return self.role in ['SUPER_ADMIN', 'CD_FINANCE']
    
    def peut_creer_releves_cdf(self):
        """Vérifie si l'utilisateur peut créer des relevés (CD_FINANCE)"""
        return self.role in ['SUPER_ADMIN', 'CD_FINANCE']
    
    def peut_voir_menu_depenses_operateur(self):
        """Vérifie si l'utilisateur peut voir le menu dépenses (OPERATEUR_SAISIE)"""
        return self.role in ['SUPER_ADMIN', 'OPERATEUR_SAISIE']
    
    def peut_voir_menu_recettes_operateur(self):
        """Vérifie si l'utilisateur peut voir le menu recettes (OPERATEUR_SAISIE)"""
        return self.role in ['SUPER_ADMIN', 'OPERATEUR_SAISIE']
    
    def peut_voir_menu_paiements_agent(self):
        """Vérifie si l'utilisateur peut voir le menu paiements (AGENT_PAYEUR)"""
        return self.role in ['SUPER_ADMIN', 'AGENT_PAYEUR']
    
    def peut_valider_paiements_agent(self):
        """Vérifie si l'utilisateur peut valider les paiements (AGENT_PAYEUR)"""
        return self.role in ['SUPER_ADMIN', 'AGENT_PAYEUR']
    
    def peut_voir_paiements(self):
        """Vérifie si l'utilisateur peut voir le menu paiements (tous les rôles concernés)"""
        return self.role in ['SUPER_ADMIN', 'ADMIN', 'DG', 'DF', 'CD_FINANCE', 'AGENT_PAYEUR']
    
    def peut_acceder_admin_django(self):
        """Vérifie si l'utilisateur peut accéder à l'administration Django"""
        return self.role in ['SUPER_ADMIN', 'ADMIN']
    
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

