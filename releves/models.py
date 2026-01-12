"""
Modèles pour la gestion des relevés bancaires
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User
from banques.models import Banque, CompteBancaire


class ReleveBancaire(models.Model):
    """Modèle pour les relevés bancaires reçus des banques"""
    DEVISE_CHOICES = [
        ('USD', 'Dollar US (USD)'),
        ('CDF', 'Franc Congolais (CDF)'),
    ]
    
    banque = models.ForeignKey(Banque, on_delete=models.PROTECT, related_name='releves')
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.PROTECT, related_name='releves')
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES)
    releve_pdf = models.FileField(upload_to='releves/pdfs/', blank=True, null=True)
    total_recettes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_depenses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    solde_banque = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    saisi_par = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='releves_saisis',
        limit_choices_to={'role': 'OPERATEUR_SAISIE'}
    )
    date_saisie = models.DateTimeField(auto_now_add=True)
    valide = models.BooleanField(default=False)
    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='releves_valides',
        limit_choices_to={'role__in': ['COMPTABLE', 'DF']}
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    observations = models.TextField(blank=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Relevé Bancaire"
        verbose_name_plural = "Relevés Bancaires"
        ordering = ['-periode_fin', '-date_saisie']
    
    def __str__(self):
        return f"Relevé {self.banque.nom_banque} - {self.periode_debut} au {self.periode_fin} ({self.devise})"
    
    def save(self, *args, **kwargs):
        # Mise à jour automatique de la devise selon le compte
        if self.compte_bancaire:
            self.devise = self.compte_bancaire.devise
        
        # Calcul automatique du solde
        self.solde_banque = self.total_recettes - self.total_depenses
        
        super().save(*args, **kwargs)
    
    def calculer_totaux(self):
        """Calcule les totaux à partir des mouvements"""
        self.total_recettes = sum(
            m.montant for m in self.mouvements.filter(type_mouvement='RECETTE')
        )
        self.total_depenses = sum(
            m.montant for m in self.mouvements.filter(type_mouvement='DEPENSE')
        )
        self.solde_banque = self.total_recettes - self.total_depenses
        self.save(update_fields=['total_recettes', 'total_depenses', 'solde_banque'])


class MouvementBancaire(models.Model):
    """Modèle pour les mouvements bancaires individuels"""
    TYPE_MOUVEMENT_CHOICES = [
        ('RECETTE', 'Recette'),
        ('DEPENSE', 'Dépense'),
    ]
    
    releve = models.ForeignKey(ReleveBancaire, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=10, choices=TYPE_MOUVEMENT_CHOICES)
    reference_operation = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    montant = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    devise = models.CharField(max_length=3)
    date_operation = models.DateField()
    beneficiaire_ou_source = models.CharField(max_length=200, blank=True)
    lie_a_recette = models.ForeignKey(
        'recettes.Recette',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_bancaires'
    )
    lie_a_demande = models.ForeignKey(
        'demandes.DemandePaiement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_bancaires'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mouvement Bancaire"
        verbose_name_plural = "Mouvements Bancaires"
        ordering = ['-date_operation', '-date_creation']
    
    def __str__(self):
        return f"{self.type_mouvement} - {self.montant} {self.devise} - {self.description[:50]}"
    
    def save(self, *args, **kwargs):
        # Mise à jour automatique de la devise selon le relevé
        if self.releve:
            self.devise = self.releve.devise
        super().save(*args, **kwargs)
        
        # Recalculer les totaux du relevé
        if self.releve:
            self.releve.calculer_totaux()

