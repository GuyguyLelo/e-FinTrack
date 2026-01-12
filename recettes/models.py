"""
Modèles pour la gestion des recettes
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User
from banques.models import Banque, CompteBancaire


class Recette(models.Model):
    """Modèle pour les recettes encaissées"""
    SOURCE_CHOICES = [
        ('DROITS_ADMINISTRATIFS', 'Droits administratifs'),
        ('REDEVANCES', 'Redevances'),
        ('PARTICIPATIONS', 'Participations'),
        ('AUTRES', 'Autres'),
    ]
    
    reference = models.CharField(max_length=50, unique=True, editable=False)
    banque = models.ForeignKey(Banque, on_delete=models.PROTECT, related_name='recettes')
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.PROTECT, related_name='recettes')
    source_recette = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    description = models.TextField()
    montant_usd = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="Montant USD"
    )
    montant_cdf = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="Montant CDF"
    )
    date_encaissement = models.DateField()
    piece_jointe = models.FileField(upload_to='recettes/pieces_jointes/', blank=True, null=True)
    enregistre_par = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='recettes_enregistrees',
        limit_choices_to={'role__in': ['COMPTABLE', 'OPERATEUR_SAISIE']}
    )
    valide = models.BooleanField(default=False)
    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recettes_validees',
        limit_choices_to={'role': 'COMPTABLE'}
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Recette"
        verbose_name_plural = "Recettes"
        ordering = ['-date_encaissement', '-date_creation']
    
    def __str__(self):
        montants = []
        if self.montant_usd > 0:
            montants.append(f"{self.montant_usd} USD")
        if self.montant_cdf > 0:
            montants.append(f"{self.montant_cdf} CDF")
        return f"{self.reference} - {', '.join(montants) if montants else '0.00'}"
    
    def get_total_usd(self):
        """Retourne le montant total en USD"""
        return self.montant_usd
    
    def get_total_cdf(self):
        """Retourne le montant total en CDF"""
        return self.montant_cdf
    
    def has_montant(self):
        """Vérifie si au moins un montant est renseigné"""
        return self.montant_usd > 0 or self.montant_cdf > 0
    
    def save(self, *args, **kwargs):
        if not self.reference:
            # Génération automatique de la référence
            count = Recette.objects.count() + 1
            self.reference = f"REC-{count:06d}"
        
        is_new = self.pk is None
        was_validated = False
        if not is_new:
            try:
                old_instance = Recette.objects.get(pk=self.pk)
                was_validated = old_instance.valide
            except Recette.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Mise à jour du solde du compte bancaire lors de la validation
        if self.valide and (is_new or not was_validated):
            # Mettre à jour le solde USD si le compte est en USD
            if self.montant_usd > 0 and self.compte_bancaire.devise == 'USD':
                self.compte_bancaire.mettre_a_jour_solde(self.montant_usd, operation='recette')
            # Mettre à jour le solde CDF si le compte est en CDF
            if self.montant_cdf > 0 and self.compte_bancaire.devise == 'CDF':
                self.compte_bancaire.mettre_a_jour_solde(self.montant_cdf, operation='recette')

