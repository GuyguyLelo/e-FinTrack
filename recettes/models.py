"""
Modèles pour la gestion des recettes
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User
from banques.models import Banque, CompteBancaire


class SourceRecette(models.Model):
    """Modèle pour gérer les sources des recettes"""
    code = models.CharField(max_length=30, unique=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Source de recette"
        verbose_name_plural = "Sources de recettes"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"

    def natural_key(self):
        return [self.code]

    @classmethod
    def get_by_natural_key(cls, code):
        return cls.objects.get(code=code)
    
    @classmethod
    def get_sources_par_defaut(cls):
        """Crée les sources par défaut si elles n'existent pas"""
        sources_defaut = [
            ('DROITS_ADMINISTRATIFS', 'Droits administratifs', 'Frais administratifs et droits divers'),
            ('REDEVANCES', 'Redevances', 'Revenus des redevances et royalties'),
            ('PARTICIPATIONS', 'Participations', 'Revenus de participation et dividendes'),
            ('AUTRES', 'Autres', 'Autres sources de revenus non classifiées'),
        ]
        
        for code, nom, description in sources_defaut:
            cls.objects.get_or_create(
                code=code,
                defaults={'nom': nom, 'description': description}
            )

class Recette(models.Model):
    """Modèle pour les recettes encaissées"""
    
    reference = models.CharField(max_length=50, unique=True, editable=False)
    banque = models.ForeignKey(Banque, on_delete=models.CASCADE, related_name='recettes')
    compte_bancaire = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE, related_name='recettes', null=True, blank=True)
    source_recette = models.ForeignKey(SourceRecette, on_delete=models.PROTECT, related_name='recettes', null=True, blank=True)
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
        
        # Mise à jour automatique des soldes lors de l'enregistrement de la recette
        # Cette mise à jour cumule automatiquement le montant dans le solde consolidé du tableau de bord
        # Mettre à jour les comptes bancaires pour toutes les recettes enregistrées (validées ou non)
        # Vérifier si c'est une nouvelle recette ou si la recette vient d'être validée
        recette_a_traiter = is_new or (self.valide and not was_validated)
        
        if recette_a_traiter:
            # Utiliser une transaction pour garantir la cohérence
            from django.db import transaction
            import logging
            logger = logging.getLogger(__name__)
            
            try:
                with transaction.atomic():
                    # Vérifier que la banque est définie
                    if not self.banque:
                        logger.error(f"Recette {self.reference}: Aucune banque définie, impossible de mettre à jour le solde")
                        return
                    
                    # Trouver automatiquement les comptes bancaires appropriés selon la banque sélectionnée
                    if self.montant_usd > 0:
                        # Trouver un compte USD pour cette banque
                        # Note: select_for_update() peut ne pas fonctionner avec SQLite, mais on l'utilise quand même pour la compatibilité
                        try:
                            compte_usd = CompteBancaire.objects.select_for_update().filter(
                                banque=self.banque, 
                                devise='USD', 
                                actif=True
                            ).first()
                        except Exception:
                            # Fallback si select_for_update() ne fonctionne pas (ex: SQLite)
                            compte_usd = CompteBancaire.objects.filter(
                                banque=self.banque, 
                                devise='USD', 
                                actif=True
                            ).first()
                        
                        if compte_usd:
                            # Rafraîchir le compte pour avoir le solde le plus récent
                            compte_usd.refresh_from_db()
                            solde_avant = compte_usd.solde_courant
                            # Ajouter le montant au solde du compte (cumul dans le solde consolidé)
                            compte_usd.mettre_a_jour_solde(self.montant_usd, operation='recette')
                            logger.info(f"Recette {self.reference}: Solde USD mis à jour de {solde_avant} à {compte_usd.solde_courant} pour le compte {compte_usd.intitule_compte}")
                            # Associer la recette à ce compte
                            if not self.compte_bancaire or self.compte_bancaire != compte_usd:
                                self.compte_bancaire = compte_usd
                                # Utiliser update pour éviter un appel récursif à save()
                                Recette.objects.filter(pk=self.pk).update(compte_bancaire=compte_usd)
                        else:
                            logger.warning(f"Recette {self.reference}: Aucun compte USD actif trouvé pour la banque {self.banque.nom_banque}")
                    
                    if self.montant_cdf > 0:
                        # Trouver un compte CDF pour cette banque
                        try:
                            compte_cdf = CompteBancaire.objects.select_for_update().filter(
                                banque=self.banque, 
                                devise='CDF', 
                                actif=True
                            ).first()
                        except Exception:
                            # Fallback si select_for_update() ne fonctionne pas (ex: SQLite)
                            compte_cdf = CompteBancaire.objects.filter(
                                banque=self.banque, 
                                devise='CDF', 
                                actif=True
                            ).first()
                        
                        if compte_cdf:
                            # Rafraîchir le compte pour avoir le solde le plus récent
                            compte_cdf.refresh_from_db()
                            solde_avant = compte_cdf.solde_courant
                            # Ajouter le montant au solde du compte (cumul dans le solde consolidé)
                            compte_cdf.mettre_a_jour_solde(self.montant_cdf, operation='recette')
                            logger.info(f"Recette {self.reference}: Solde CDF mis à jour de {solde_avant} à {compte_cdf.solde_courant} pour le compte {compte_cdf.intitule_compte}")
                            # Si pas déjà associé à un compte USD, associer à ce compte CDF
                            if not self.compte_bancaire or (self.compte_bancaire and self.compte_bancaire.devise != 'USD'):
                                if self.compte_bancaire != compte_cdf:
                                    self.compte_bancaire = compte_cdf
                                    # Utiliser update pour éviter un appel récursif à save()
                                    Recette.objects.filter(pk=self.pk).update(compte_bancaire=compte_cdf)
                        else:
                            logger.warning(f"Recette {self.reference}: Aucun compte CDF actif trouvé pour la banque {self.banque.nom_banque}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du solde pour la recette {self.reference}: {str(e)}", exc_info=True)
                # Ne pas lever l'exception pour ne pas bloquer la sauvegarde de la recette
        
        # Si une recette validée est modifiée et dévalidée, retirer le montant du solde
        elif not is_new and was_validated and not self.valide:
            # Retirer le montant du solde si la recette était validée et ne l'est plus
            if self.compte_bancaire:
                from django.db import transaction
                with transaction.atomic():
                    compte = CompteBancaire.objects.select_for_update().get(pk=self.compte_bancaire.pk)
                    compte.refresh_from_db()
                    if self.montant_usd > 0 and compte.devise == 'USD':
                        compte.mettre_a_jour_solde(self.montant_usd, operation='depense')
                    elif self.montant_cdf > 0 and compte.devise == 'CDF':
                        compte.mettre_a_jour_solde(self.montant_cdf, operation='depense')
    
    def delete(self, *args, **kwargs):
        """Surcharge de la méthode delete pour mettre à jour le solde du compte bancaire"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Si la recette est validée, on met à jour le solde en retirant les montants
        if self.valide and self.compte_bancaire:
            from django.db import transaction
            try:
                with transaction.atomic():
                    compte = CompteBancaire.objects.select_for_update().get(pk=self.compte_bancaire.pk)
                    compte.refresh_from_db()
                    solde_avant = compte.solde_courant
                    
                    # Retirer les montants du solde (opération inverse de la création)
                    if self.montant_usd > 0 and compte.devise == 'USD':
                        compte.mettre_a_jour_solde(self.montant_usd, operation='depense')
                        logger.info(f"Suppression recette {self.reference}: Solde USD mis à jour de {solde_avant} à {compte.solde_courant} pour le compte {compte.intitule_compte}")
                    elif self.montant_cdf > 0 and compte.devise == 'CDF':
                        compte.mettre_a_jour_solde(self.montant_cdf, operation='depense')
                        logger.info(f"Suppression recette {self.reference}: Solde CDF mis à jour de {solde_avant} à {compte.solde_courant} pour le compte {compte.intitule_compte}")
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du solde pour la suppression de la recette {self.reference}: {str(e)}", exc_info=True)
        
        # Appel de la méthode delete originale
        super().delete(*args, **kwargs)


class RecetteFeuille(models.Model):
    """
    Ligne de recette correspondant à la feuille RECETTES du fichier Excel (DATADAF).
    Structure : MOIS, ANNEE, DATE, LIBELLE RECETTE, BANQUE, MONTANT FC, MONTANT $us
    """
    MOIS_CHOICES = [(i, str(i)) for i in range(1, 13)]

    mois = models.PositiveSmallIntegerField(choices=MOIS_CHOICES, verbose_name="Mois")
    annee = models.PositiveIntegerField(verbose_name="Année")
    date = models.DateField(verbose_name="Date")
    libelle_recette = models.CharField(max_length=500, verbose_name="Libellé recette")
    banque = models.ForeignKey(
        Banque,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recette_feuilles',
        verbose_name="Banque"
    )
    montant_fc = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant FC"
    )
    montant_usd = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant $us"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recette (feuille)"
        verbose_name_plural = "Recettes (feuille)"
        ordering = ['-date', '-date_creation']

    def __str__(self):
        nom_banque = self.banque.nom_banque if self.banque else ""
        return f"{self.date} - {self.libelle_recette[:50]} - {nom_banque}"

