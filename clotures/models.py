"""
Modèles pour la gestion des clôtures mensuelles
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()


class ClotureMensuelle(models.Model):
    """
    Gestion des clôtures mensuelles des recettes et dépenses
    """
    STATUT_CHOICES = [
        ('OUVERT', 'Ouvert'),
        ('CLOTURE', 'Clôturé'),
    ]
    
    MOIS_CHOICES = [(i, str(i)) for i in range(1, 13)]

    mois = models.PositiveSmallIntegerField(choices=MOIS_CHOICES, verbose_name="Mois")
    annee = models.PositiveIntegerField(verbose_name="Année")
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='OUVERT',
        verbose_name="Statut"
    )
    
    # Soldes d'ouverture
    solde_ouverture_fc = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Solde d'ouverture FC"
    )
    solde_ouverture_usd = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Solde d'ouverture USD"
    )
    
    # Soldes de la période
    total_recettes_fc = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total recettes FC"
    )
    total_recettes_usd = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total recettes USD"
    )
    total_depenses_fc = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total dépenses FC"
    )
    total_depenses_usd = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total dépenses USD"
    )
    
    # Solde net de la période
    solde_net_fc = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Solde net FC"
    )
    solde_net_usd = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Solde net USD"
    )
    
    # Informations de clôture
    date_cloture = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de clôture"
    )
    cloture_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clotures_effectuees',
        verbose_name="Clôturé par"
    )
    observations = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observations"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Clôture mensuelle"
        verbose_name_plural = "Clôtures mensuelles"
        unique_together = ['mois', 'annee']
        ordering = ['-annee', '-mois']

    def __str__(self):
        return f"Clôture {self.mois:02d}/{self.annee} - {self.statut}"

    def calculer_soldes(self):
        """Calculer les soldes de la période"""
        from demandes.models import DepenseFeuille
        from recettes.models import RecetteFeuille
        
        # Calculer les totaux des recettes
        recettes = RecetteFeuille.objects.filter(
            mois=self.mois,
            annee=self.annee
        )
        self.total_recettes_fc = recettes.aggregate(
            total=models.Sum('montant_fc')
        )['total'] or Decimal('0.00')
        self.total_recettes_usd = recettes.aggregate(
            total=models.Sum('montant_usd')
        )['total'] or Decimal('0.00')
        
        # Calculer les totaux des dépenses
        depenses = DepenseFeuille.objects.filter(
            mois=self.mois,
            annee=self.annee
        )
        self.total_depenses_fc = depenses.aggregate(
            total=models.Sum('montant_fc')
        )['total'] or Decimal('0.00')
        self.total_depenses_usd = depenses.aggregate(
            total=models.Sum('montant_usd')
        )['total'] or Decimal('0.00')
        
        # Calculer le solde net
        self.solde_net_fc = self.total_recettes_fc - self.total_depenses_fc
        self.solde_net_usd = self.total_recettes_usd - self.total_depenses_usd
        
        self.save()

    def cloturer(self, utilisateur, observations=""):
        """Clôturer la période"""
        if self.statut == 'CLOTURE':
            raise ValueError("Cette période est déjà clôturée")
        
        # Vérifier si la période peut être clôturée
        peut_cloturer, message = self.peut_etre_cloture()
        if not peut_cloturer:
            raise ValueError(message)
        
        # Recalculer les soldes
        self.calculer_soldes()
        
        # Mettre à jour les informations de clôture
        self.statut = 'CLOTURE'
        self.date_cloture = timezone.now()
        self.cloture_par = utilisateur
        self.observations = observations
        
        # Créer la période suivante avec le solde comme solde d'ouverture
        self._creer_periode_suivante()
        
        self.save()

    def _creer_periode_suivante(self):
        """Créer la période suivante avec le solde comme solde d'ouverture"""
        from django.utils import timezone
        
        # Calculer le mois et l'année suivants
        if self.mois == 12:
            mois_suivant = 1
            annee_suivante = self.annee + 1
        else:
            mois_suivant = self.mois + 1
            annee_suivante = self.annee
        
        # Vérifier si la période suivante existe déjà
        cloture_suivante, created = ClotureMensuelle.objects.get_or_create(
            mois=mois_suivant,
            annee=annee_suivante,
            defaults={
                'statut': 'OUVERT',
                'solde_ouverture_fc': self.solde_net_fc,
                'solde_ouverture_usd': self.solde_net_usd
            }
        )
        
        if not created:
            # Si la période existe déjà, mettre à jour les soldes d'ouverture
            cloture_suivante.solde_ouverture_fc = self.solde_net_fc
            cloture_suivante.solde_ouverture_usd = self.solde_net_usd
            cloture_suivante.save()

    def peut_etre_cloture(self):
        """Vérifier si la période peut être clôturée (uniquement en fin de mois)"""
        from django.utils import timezone
        from datetime import datetime
        
        # Si déjà clôturée, ne peut pas être re-clôturée
        if self.statut == 'CLOTURE':
            return False, "Cette période est déjà clôturée"
        
        # Vérifier si nous sommes en fin de mois
        today = timezone.now().date()
        current_year = today.year
        current_month = today.month
        
        # Si ce n'est pas la période actuelle, on ne peut pas clôturer
        if self.annee != current_year or self.mois != current_month:
            return False, "Seule la période actuelle peut être clôturée"
        
        # Obtenir le dernier jour du mois
        if self.mois == 2:  # Février
            # Vérifier année bissextile
            if (current_year % 4 == 0 and current_year % 100 != 0) or (current_year % 400 == 0):
                dernier_jour = 29
            else:
                dernier_jour = 28
        elif self.mois in [4, 6, 9, 11]:  # Mois de 30 jours
            dernier_jour = 30
        else:  # Mois de 31 jours
            dernier_jour = 31
        
        # Vérifier si nous sommes au dernier jour du mois
        if today.day != dernier_jour:
            return False, f"La clôture n'est autorisée qu'au {dernier_jour}ème jour du mois (nous sommes le {today.day})"
        
        return True, "La période peut être clôturée"

    def peut_etre_modifie(self):
        """Vérifier si la période peut être modifiée"""
        return self.statut == 'OUVERT'

    @classmethod
    def get_periode_actuelle(cls):
        """Obtenir la période actuelle (mois et année courants)"""
        from django.utils import timezone
        now = timezone.now()
        periode, created = cls.objects.get_or_create(
            mois=now.month,
            annee=now.year,
            defaults={'statut': 'OUVERT'}
        )
        return periode

    @classmethod
    def peut_cloturer(cls, utilisateur):
        """Vérifier si l'utilisateur peut clôturer des périodes"""
        return utilisateur.role in ['DG', 'CD_FINANCE']
