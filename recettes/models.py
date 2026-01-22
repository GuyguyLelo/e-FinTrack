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
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.PROTECT, related_name='recettes', null=True, blank=True)
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
        
        # Mise à jour automatique des soldes lors de la validation
        if self.valide and (is_new or not was_validated):
            # Trouver automatiquement les comptes bancaires appropriés selon la banque sélectionnée
            if self.montant_usd > 0 and self.banque:
                # Trouver un compte USD pour cette banque
                compte_usd = CompteBancaire.objects.filter(
                    banque=self.banque, 
                    devise='USD', 
                    actif=True
                ).first()
                if compte_usd:
                    compte_usd.mettre_a_jour_solde(self.montant_usd, operation='recette')
                    # Associer la recette à ce compte
                    self.compte_bancaire = compte_usd
                    self.save(update_fields=['compte_bancaire'])
            
            if self.montant_cdf > 0 and self.banque:
                # Trouver un compte CDF pour cette banque
                compte_cdf = CompteBancaire.objects.filter(
                    banque=self.banque, 
                    devise='CDF', 
                    actif=True
                ).first()
                if compte_cdf:
                    compte_cdf.mettre_a_jour_solde(self.montant_cdf, operation='recette')
                    # Si pas déjà associé à un compte USD, associer à ce compte CDF
                    if not self.compte_bancaire or self.compte_bancaire.devise != 'USD':
                        self.compte_bancaire = compte_cdf
                        self.save(update_fields=['compte_bancaire'])

