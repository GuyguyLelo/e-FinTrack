"""
Modèles pour le rapprochement bancaire
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User
from banques.models import Banque, CompteBancaire
from releves.models import ReleveBancaire


class RapprochementBancaire(models.Model):
    """Modèle pour le rapprochement bancaire automatique"""
    DEVISE_CHOICES = [
        ('USD', 'Dollar US (USD)'),
        ('CDF', 'Franc Congolais (CDF)'),
    ]
    
    banque = models.ForeignKey(Banque, on_delete=models.PROTECT, related_name='rapprochements')
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.PROTECT, related_name='rapprochements')
    periode_mois = models.IntegerField(validators=[MinValueValidator(1)])
    periode_annee = models.IntegerField()
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES)
    solde_banque = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    solde_interne = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    ecart = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    releve_bancaire = models.ForeignKey(
        ReleveBancaire,
        on_delete=models.PROTECT,
        related_name='rapprochements',
        null=True,
        blank=True
    )
    observateur = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='rapprochements_observes',
        limit_choices_to={'role': 'AUDITEUR'}
    )
    commentaire = models.TextField(blank=True)
    valide = models.BooleanField(default=False)
    date_rapprochement = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rapprochement Bancaire"
        verbose_name_plural = "Rapprochements Bancaires"
        ordering = ['-periode_annee', '-periode_mois']
        unique_together = ['banque', 'compte_bancaire', 'periode_mois', 'periode_annee']
    
    def __str__(self):
        return f"Rapprochement {self.banque.nom_banque} - {self.periode_mois}/{self.periode_annee} ({self.devise})"
    
    def save(self, *args, **kwargs):
        # Calcul automatique de l'écart
        self.ecart = self.solde_banque - self.solde_interne
        
        # Mise à jour automatique de la devise selon le compte
        if self.compte_bancaire:
            self.devise = self.compte_bancaire.devise
        
        super().save(*args, **kwargs)
    
    def calculer_solde_interne(self):
        """Calcule le solde interne à partir des recettes et dépenses validées"""
        from django.db.models import Q
        from recettes.models import Recette
        from releves.models import MouvementBancaire
        
        # Calculer les recettes validées pour cette période
        recettes = Recette.objects.filter(
            compte_bancaire=self.compte_bancaire,
            valide=True,
            devise=self.devise,
            date_encaissement__year=self.periode_annee,
            date_encaissement__month=self.periode_mois
        )
        total_recettes = sum(r.montant for r in recettes)
        
        # Calculer les dépenses pour cette période (via mouvements bancaires)
        mouvements_depenses = MouvementBancaire.objects.filter(
            releve__compte_bancaire=self.compte_bancaire,
            type_mouvement='DEPENSE',
            devise=self.devise,
            date_operation__year=self.periode_annee,
            date_operation__month=self.periode_mois
        )
        total_depenses = sum(m.montant for m in mouvements_depenses)
        
        # Calculer le solde de début de période
        # Chercher le rapprochement de la période précédente
        rapprochement_precedent = RapprochementBancaire.objects.filter(
            compte_bancaire=self.compte_bancaire,
            devise=self.devise
        ).exclude(pk=self.pk).filter(
            Q(periode_annee__lt=self.periode_annee) |
            Q(periode_annee=self.periode_annee, periode_mois__lt=self.periode_mois)
        ).order_by('-periode_annee', '-periode_mois').first()
        
        if rapprochement_precedent and rapprochement_precedent.solde_interne:
            solde_debut = rapprochement_precedent.solde_interne
        else:
            # Sinon, utiliser le solde initial du compte
            solde_debut = self.compte_bancaire.solde_initial
        
        # Solde interne = solde début + recettes - dépenses
        self.solde_interne = solde_debut + total_recettes - total_depenses
        self.ecart = self.solde_banque - self.solde_interne
        self.save(update_fields=['solde_interne', 'ecart'])

