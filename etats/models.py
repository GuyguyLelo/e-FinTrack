"""
Modèles pour la gestion des états générés
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from accounts.models import User, Service
from banques.models import Banque, CompteBancaire
from demandes.models import NatureEconomique


class EtatGenerique(models.Model):
    """Modèle générique pour tous les types d'états générés"""
    
    TYPE_ETAT_CHOICES = [
        ('RELEVE_DEPENSE', 'Relevé de dépenses'),
        ('DEMANDE_PAIEMENT', 'Demandes de paiement'),
        ('DEPENSE', 'Dépenses'),
        ('RECETTE', 'Recettes'),
        ('PAIEMENT', 'Paiements'),
        ('Bilan', 'Bilan financier'),
        ('SOLDE_BANCAIRE', 'Solde bancaire'),
        ('SITUATION_FINANCIERE', 'Situation financière'),
    ]
    
    STATUT_CHOICES = [
        ('GENERATION', 'En cours de génération'),
        ('GENERE', 'Généré'),
        ('ERREUR', 'Erreur'),
    ]
    
    PERIODICITE_CHOICES = [
        ('JOURNALIER', 'Journalier'),
        ('HEBDOMADAIRE', 'Hebdomadaire'),
        ('MENSUEL', 'Mensuel'),
        ('TRIMESTRIEL', 'Trimestriel'),
        ('ANNUEL', 'Annuel'),
        ('PERSONNALISE', 'Personnalisé'),
    ]
    
    titre = models.CharField(max_length=200, verbose_name="Titre de l'état")
    type_etat = models.CharField(max_length=30, choices=TYPE_ETAT_CHOICES, verbose_name="Type d'état")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Période
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    periodicite = models.CharField(max_length=20, choices=PERIODICITE_CHOICES, default='PERSONNALISE')
    
    # Filtres
    services = models.ManyToManyField(Service, blank=True, verbose_name="Services")
    natures_economiques = models.ManyToManyField(NatureEconomique, blank=True, verbose_name="Articles Littera")
    banques = models.ManyToManyField(Banque, blank=True, verbose_name="Banques")
    comptes_bancaires = models.ManyToManyField(CompteBancaire, blank=True, verbose_name="Comptes bancaires")
    
    # Montants calculés
    total_usd = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Total USD")
    total_cdf = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Total CDF")
    total_general = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Total général")
    
    # Fichiers générés
    fichier_pdf = models.FileField(upload_to='etats/pdfs/', blank=True, null=True, verbose_name="Fichier PDF")
    fichier_excel = models.FileField(upload_to='etats/excels/', blank=True, null=True, verbose_name="Fichier Excel")
    
    # Métadonnées
    genere_par = models.ForeignKey(User, on_delete=models.PROTECT, related_name='etats_generes')
    date_generation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='GENERATION')
    
    # Paramètres supplémentaires (JSON)
    filtres_supplementaires = models.JSONField(default=dict, blank=True, verbose_name="Filtres supplémentaires")
    parametres_affichage = models.JSONField(default=dict, blank=True, verbose_name="Paramètres d'affichage")
    
    class Meta:
        verbose_name = "État généré"
        verbose_name_plural = "États générés"
        ordering = ['-date_generation']
        indexes = [
            models.Index(fields=['type_etat']),
            models.Index(fields=['date_debut', 'date_fin']),
            models.Index(fields=['statut']),
            models.Index(fields=['genere_par']),
        ]
    
    def __str__(self):
        return f"{self.titre} - {self.get_type_etat_display()} ({self.date_debut} au {self.date_fin})"
    
    def save(self, *args, **kwargs):
        # Calcul du total général
        self.total_general = self.total_usd + self.total_cdf
        super().save(*args, **kwargs)
    
    def get_nom_fichier(self, extension='pdf'):
        """Génère un nom de fichier pour l'état"""
        date_str = timezone.now().strftime('%Y%m%d_%H%M%S')
        titre_clean = self.titre.replace(' ', '_')
        return f"{self.type_etat}_{titre_clean}_{date_str}.{extension}"


class ConfigurationEtat(models.Model):
    """Configuration pour les types d'états"""
    
    type_etat = models.CharField(max_length=30, unique=True, choices=EtatGenerique.TYPE_ETAT_CHOICES)
    titre_par_defaut = models.CharField(max_length=200, verbose_name="Titre par défaut")
    description_template = models.TextField(blank=True, verbose_name="Template de description")
    
    # Champs à afficher
    champs_affiches = models.JSONField(default=list, verbose_name="Champs à afficher")
    filtres_disponibles = models.JSONField(default=list, verbose_name="Filtres disponibles")
    
    # Mise en forme
    template_pdf = models.CharField(max_length=100, default='etats/etat_pdf.html', verbose_name="Template PDF")
    template_excel = models.CharField(max_length=100, blank=True, verbose_name="Template Excel")
    
    # Paramètres par défaut
    periodicite_defaut = models.CharField(max_length=20, choices=EtatGenerique.PERIODICITE_CHOICES, default='MENSUEL')
    actif = models.BooleanField(default=True, verbose_name="Actif")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuration d'état"
        verbose_name_plural = "Configurations d'états"
    
    def __str__(self):
        return f"Configuration - {self.get_type_etat_display()}"


class HistoriqueGeneration(models.Model):
    """Historique des générations d'états"""
    
    etat = models.ForeignKey(EtatGenerique, on_delete=models.CASCADE, related_name='historique')
    action = models.CharField(max_length=50)  # 'GENERATION', 'VISUALISATION', 'TELECHARGEMENT'
    utilisateur = models.ForeignKey(User, on_delete=models.PROTECT)
    date_action = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Historique de génération"
        verbose_name_plural = "Historiques de générations"
        ordering = ['-date_action']
    
    def __str__(self):
        return f"{self.action} - {self.etat.titre} par {self.utilisateur.username}"
