"""
Modèles pour la gestion des banques et comptes bancaires
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Banque(models.Model):
    """Modèle pour les banques partenaires"""
    nom_banque = models.CharField(max_length=200, unique=True)
    code_swift = models.CharField(max_length=11, blank=True, null=True, help_text="Code SWIFT/BIC")
    adresse = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Banque"
        verbose_name_plural = "Banques"
        ordering = ['nom_banque']
    
    def __str__(self):
        return self.nom_banque


class CompteBancaire(models.Model):
    """Modèle pour les comptes bancaires (USD et CDF)"""
    DEVISE_CHOICES = [
        ('USD', 'Dollar US (USD)'),
        ('CDF', 'Franc Congolais (CDF)'),
    ]
    
    banque = models.ForeignKey(Banque, on_delete=models.CASCADE, related_name='comptes')
    intitule_compte = models.CharField(max_length=200)
    numero_compte = models.CharField(max_length=50, unique=True)
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES)
    solde_initial = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    solde_courant = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    date_solde_courant = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de mise à jour du solde courant",
        help_text="Date de la dernière mise à jour du solde courant"
    )
    date_ouverture = models.DateField()
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Compte Bancaire"
        verbose_name_plural = "Comptes Bancaires"
        ordering = ['banque', 'devise', 'intitule_compte']
        unique_together = ['banque', 'numero_compte']
    
    def __str__(self):
        return f"{self.banque.nom_banque} - {self.intitule_compte} ({self.devise})"
    
    def mettre_a_jour_solde(self, montant, operation='depense'):
        """Met à jour le solde courant du compte"""
        from django.utils import timezone
        
        if operation == 'depense':
            self.solde_courant -= montant
        elif operation == 'recette':
            self.solde_courant += montant
        
        # Mettre à jour la date du solde courant
        self.date_solde_courant = timezone.now()
        
        self.save(update_fields=['solde_courant', 'date_solde_courant', 'date_modification'])

