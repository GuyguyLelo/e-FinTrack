"""
Modèles pour la gestion des demandes de paiement
"""
from django.db import models, transaction
from django.db.models import Max
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from accounts.models import User, Service
from banques.models import Banque


class NomenclatureDepense(models.Model):
    """Modèle pour la nomenclature des dépenses (plan comptable)"""
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('DEPASSE', 'Dépassé'),
    ]
    
    annee = models.IntegerField(verbose_name="Année", help_text="Année d'application de cette nomenclature")
    date_publication = models.DateField(verbose_name="Date de publication", help_text="Date de publication de cette nomenclature")
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='EN_COURS',
        verbose_name="Statut",
        help_text="Statut de la nomenclature (en cours ou dépassé)"
    )
    
    class Meta:
        verbose_name = "Nomenclature de Dépense"
        verbose_name_plural = "Nomenclatures de Dépenses"
        ordering = ['-annee', '-date_publication']
        unique_together = [['annee', 'date_publication']]  # Une nomenclature unique par année et date de publication
        indexes = [
            models.Index(fields=['annee']),
            models.Index(fields=['statut']),
            models.Index(fields=['date_publication']),
        ]
    
    def __str__(self):
        return f"Nomenclature {self.annee} - {self.date_publication} - {self.get_statut_display()}"


class DemandePaiement(models.Model):
    """Modèle pour les demandes de paiement"""
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDEE_DG', 'Validée par le DG'),
        ('VALIDEE_DF', 'Validée par le DF'),
        ('PAYEE', 'Payée'),
        ('REJETEE', 'Rejetée'),
    ]
    
    DEVISE_CHOICES = [
        ('USD', 'Dollar US (USD)'),
        ('CDF', 'Franc Congolais (CDF)'),
    ]
    
    reference = models.CharField(max_length=50, unique=True, editable=False)
    service_demandeur = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='demandes')
    nomenclature = models.ForeignKey(
        NomenclatureDepense, 
        on_delete=models.PROTECT, 
        related_name='demandes',
        null=True,
        blank=True,
        verbose_name="Nomenclature de dépense"
    )
    nature_economique = models.ForeignKey(
        'NatureEconomique',
        on_delete=models.SET_NULL,
        related_name='demandes',
        null=True,
        blank=True,
        verbose_name="Nature économique"
    )
    description = models.TextField()
    montant = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    montant_deja_paye = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Montant déjà payé",
        help_text="Montant déjà payé pour cette demande"
    )
    reste_a_payer = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Reste à payer",
        help_text="Montant restant à payer pour cette demande"
    )
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES)
    date_demande = models.DateField(verbose_name="Date de demande", null=True, blank=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    pieces_justificatives = models.FileField(upload_to='demandes/pieces_justificatives/', blank=True, null=True)
    cree_par = models.ForeignKey(User, on_delete=models.PROTECT, related_name='demandes_creees')
    approuve_par = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='demandes_approuvees'
    )
    date_approbation = models.DateTimeField(null=True, blank=True)
    commentaire_rejet = models.TextField(blank=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Demande de Paiement"
        verbose_name_plural = "Demandes de Paiement"
        ordering = ['-date_soumission']
    
    def __str__(self):
        return f"{self.reference} - {self.montant} {self.devise}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            # Génération automatique de la référence
            count = DemandePaiement.objects.count() + 1
            self.reference = f"DEM-{count:06d}"
        
        # Correction automatique des montants incohérents
        if self.montant_deja_paye > self.montant:
            self.montant_deja_paye = self.montant
        
        # Calcul automatique du reste à payer
        self.reste_a_payer = self.montant - self.montant_deja_paye
        
        # Mise à jour du statut si la demande est entièrement payée
        if self.reste_a_payer <= 0 and self.montant_deja_paye > 0:
            self.statut = 'PAYEE'
            self.montant_deja_paye = self.montant
            self.reste_a_payer = Decimal('0.00')
        
        super().save(*args, **kwargs)


class ReleveDepense(models.Model):
    """Modèle pour les relevés de dépenses consolidés"""
    DEVISE_CHOICES = [
        ('USD', 'Dollar US (USD)'),
        ('CDF', 'Franc Congolais (CDF)'),
    ]
    
    numero = models.CharField(max_length=50, unique=True, editable=False, verbose_name="Numéro de relevé", blank=True, null=True)
    periode = models.DateField(help_text="Période concernée")
    demandes = models.ManyToManyField(DemandePaiement, related_name='releves_depense')
    
    # Montants par devise
    montant_cdf = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant CDF")
    montant_usd = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant USD")
    
    # IPR (3%)
    ipr_cdf = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="IPR 3% CDF")
    ipr_usd = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="IPR 3% USD")
    
    # Net à payer
    net_a_payer_cdf = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Net à payer CDF")
    net_a_payer_usd = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Net à payer USD")
    
    # Observation
    observation = models.TextField(blank=True, null=True, verbose_name="Observation")
    
    # Champs de compatibilité (à supprimer plus tard)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False)
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES, blank=True, null=True, editable=False)
    
    valide_par = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='releves_depense_valides',
        limit_choices_to={'role__in': ['DAF', 'DG']}
    )
    date_validation = models.DateTimeField(auto_now_add=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Validation des dépenses
    depenses_validees = models.BooleanField(default=False, verbose_name="Dépenses validées")
    depenses_validees_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='releves_depenses_validees',
        limit_choices_to={'role__in': ['DAF', 'DG', 'COMPTABLE']},
        verbose_name="Dépenses validées par"
    )
    date_validation_depenses = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation des dépenses")
    
    class Meta:
        verbose_name = "Relevé de Dépense"
        verbose_name_plural = "Relevés de Dépense"
        ordering = ['-periode']
        unique_together = ['periode']
    
    def __str__(self):
        return f"{self.numero} - {self.periode} - {self.get_total_general()} total"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            # Génération automatique du numéro de relevé dans une transaction
            with transaction.atomic():
                # Trouver le prochain numéro disponible
                max_numero = ReleveDepense.objects.exclude(numero__isnull=True).aggregate(
                    max_num=Max('numero')
                )['max_num']
                
                if max_numero:
                    # Extraire le numéro et l'incrémenter
                    try:
                        last_num = int(max_numero.split('-')[-1])
                        next_num = last_num + 1
                    except (ValueError, IndexError):
                        # Si le format n'est pas correct, compter les relevés
                        next_num = ReleveDepense.objects.exclude(numero__isnull=True).count() + 1
                else:
                    next_num = 1
                
                # Vérifier que le numéro n'existe pas déjà (pour éviter les conflits)
                numero = f"REL-{next_num:06d}"
                while ReleveDepense.objects.filter(numero=numero).exists():
                    next_num += 1
                    numero = f"REL-{next_num:06d}"
                
                self.numero = numero
        super().save(*args, **kwargs)
    
    def ajouter_demandes_securise(self, demandes_queryset):
        """
        Méthode sécurisée pour ajouter des demandes à un relevé
        Vérifie qu'elles ne sont pas déjà dans un autre relevé et qu'elles sont validées
        """
        from django.core.exceptions import ValidationError
        
        # Filtrer uniquement les demandes validées et non déjà dans un relevé
        demandes_valides = demandes_queryset.filter(
            statut__in=['VALIDEE_DG', 'VALIDEE_DF', 'PAYEE']
        ).exclude(
            releves_depense__isnull=False
        )
        
        # Vérifier s'il y a des demandes déjà dans un autre relevé (sauf celui-ci si on modifie)
        if self.pk:
            demandes_problematiques = demandes_queryset.filter(
                releves_depense__isnull=False
            ).exclude(releves_depense__pk=self.pk)
        else:
            demandes_problematiques = demandes_queryset.filter(
                releves_depense__isnull=False
            )
        
        if demandes_problematiques.exists():
            references = [d.reference for d in demandes_problematiques]
            raise ValidationError(
                f"Les demandes suivantes sont déjà dans un autre relevé : {', '.join(references)}"
            )
        
        # Ajouter uniquement les demandes valides
        self.demandes.set(demandes_valides)
        return demandes_valides
    
    def calculer_total(self):
        """Calcule tous les montants du relevé"""
        # Filtrer uniquement les demandes validées
        demandes_validees = self.demandes.filter(
            statut__in=['VALIDEE_DG', 'VALIDEE_DF', 'PAYEE']
        )
        
        # Calculer les montants par devise
        montant_cdf = sum(demande.montant for demande in demandes_validees if demande.devise == 'CDF')
        montant_usd = sum(demande.montant for demande in demandes_validees if demande.devise == 'USD')
        
        # Calculer l'IPR (3%)
        ipr_cdf = montant_cdf * Decimal('0.03')
        ipr_usd = montant_usd * Decimal('0.03')
        
        # Calculer le net à payer (montant - IPR)
        net_a_payer_cdf = montant_cdf - ipr_cdf
        net_a_payer_usd = montant_usd - ipr_usd
        
        # Mettre à jour les champs
        self.montant_cdf = montant_cdf
        self.montant_usd = montant_usd
        self.ipr_cdf = ipr_cdf
        self.ipr_usd = ipr_usd
        self.net_a_payer_cdf = net_a_payer_cdf
        self.net_a_payer_usd = net_a_payer_usd
        
        # Compatibilité avec l'ancien système
        self.total = montant_cdf + montant_usd
        
        self.save(update_fields=['montant_cdf', 'montant_usd', 'ipr_cdf', 'ipr_usd', 
                                'net_a_payer_cdf', 'net_a_payer_usd', 'total'])
    
    def get_total_general(self):
        """Calcule le total général (CDF + USD)"""
        return self.net_a_payer_cdf + self.net_a_payer_usd


class Depense(models.Model):
    """Modèle pour les dépenses historiques importées"""
    code_depense = models.CharField(max_length=50, verbose_name="Code Dépense", db_index=True)
    mois = models.IntegerField(verbose_name="Mois", null=True, blank=True)
    annee = models.IntegerField(verbose_name="Année", null=True, blank=True)
    date_depense = models.DateField(verbose_name="Date de la dépense", null=True, blank=True)
    date_demande = models.DateField(verbose_name="Date de demande", null=True, blank=True)
    nomenclature = models.ForeignKey(
        NomenclatureDepense,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='depenses',
        verbose_name="Nomenclature"
    )
    libelle_depenses = models.TextField(verbose_name="Libellé des dépenses")
    banque = models.ForeignKey(
        Banque,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='depenses',
        verbose_name="Banque"
    )
    montant_fc = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant en CDF"
    )
    montant_usd = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant en USD"
    )
    observation = models.TextField(blank=True, verbose_name="Observation")
    piece_jointe = models.FileField(
        upload_to='depenses/pieces_jointes/',
        blank=True,
        null=True,
        verbose_name="Pièce jointe"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"
        ordering = ['-date_depense', '-annee', '-mois', 'code_depense']
        indexes = [
            models.Index(fields=['code_depense']),
            models.Index(fields=['annee', 'mois']),
            models.Index(fields=['date_depense']),
            models.Index(fields=['banque']),
        ]
    
    def __str__(self):
        return f"{self.code_depense} - {self.libelle_depenses[:50]}"
    
    @property
    def total_fc(self):
        """Retourne le montant total en CDF"""
        return self.montant_fc
    
    @property
    def total_usd(self):
        """Retourne le montant total en USD"""
        return self.montant_usd
    
    @property
    def has_amount(self):
        """Vérifie si la dépense a un montant (CDF ou USD)"""
        return self.montant_fc > Decimal('0.00') or self.montant_usd > Decimal('0.00')


class NatureEconomique(models.Model):
    code = models.CharField(max_length=20, unique=True)
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )

    class Meta:
        verbose_name = "Nature économique"
        verbose_name_plural = "Natures économiques"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.titre}"


class Cheque(models.Model):
    """Modèle pour les chèques générés à partir des relevés de dépense"""
    STATUT_CHOICES = [
        ('GENERE', 'Généré'),
        ('EMIS', 'Émis'),
        ('ENCAISSE', 'Encaissé'),
        ('ANNULE', 'Annulé'),
    ]
    
    numero_cheque = models.CharField(max_length=50, unique=True, editable=False, verbose_name="Numéro de chèque")
    releve_depense = models.OneToOneField(
        ReleveDepense,
        on_delete=models.CASCADE,
        related_name='cheque',
        verbose_name="Relevé de dépense"
    )
    banque = models.ForeignKey(
        Banque,
        on_delete=models.PROTECT,
        related_name='cheques',
        verbose_name="Banque"
    )
    montant_cdf = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant CDF")
    montant_usd = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Montant USD")
    date_emission = models.DateField(verbose_name="Date d'émission", null=True, blank=True)
    date_encaissement = models.DateField(verbose_name="Date d'encaissement", null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='GENERE', verbose_name="Statut")
    beneficiaire = models.CharField(max_length=200, blank=True, verbose_name="Bénéficiaire")
    observation = models.TextField(blank=True, null=True, verbose_name="Observation")
    cree_par = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cheques_crees',
        verbose_name="Créé par"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Chèque"
        verbose_name_plural = "Chèques"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Chèque {self.numero_cheque} - {self.releve_depense.numero} - {self.banque.nom_banque}"
    
    def save(self, *args, **kwargs):
        if not self.numero_cheque:
            # Génération automatique du numéro de chèque
            with transaction.atomic():
                max_numero = Cheque.objects.exclude(numero_cheque__isnull=True).aggregate(
                    max_num=Max('numero_cheque')
                )['max_num']
                
                if max_numero:
                    try:
                        last_num = int(max_numero.split('-')[-1])
                        next_num = last_num + 1
                    except (ValueError, IndexError):
                        next_num = Cheque.objects.exclude(numero_cheque__isnull=True).count() + 1
                else:
                    next_num = 1
                
                numero = f"CHQ-{next_num:06d}"
                while Cheque.objects.filter(numero_cheque=numero).exists():
                    next_num += 1
                    numero = f"CHQ-{next_num:06d}"
                
                self.numero_cheque = numero
        
        # Copier les montants du relevé si non définis
        if not self.montant_cdf and not self.montant_usd:
            self.montant_cdf = self.releve_depense.net_a_payer_cdf
            self.montant_usd = self.releve_depense.net_a_payer_usd
        
        super().save(*args, **kwargs)
    
    def get_montant_total(self):
        """Calcule le montant total du chèque"""
        return self.montant_cdf + self.montant_usd


class Paiement(models.Model):
    """Modèle pour gérer les paiements des demandes"""
    DEVISE_CHOICES = [
        ('USD', 'Dollar US (USD)'),
        ('CDF', 'Franc Congolais (CDF)'),
    ]
    
    reference = models.CharField(
        max_length=50, 
        unique=True, 
        editable=False,
        verbose_name="Référence du paiement"
    )
    releve_depense = models.ForeignKey(
        ReleveDepense,
        on_delete=models.PROTECT,
        related_name='paiements',
        verbose_name="Relevé de dépenses",
        null=True,
        blank=True
    )
    demande = models.ForeignKey(
        DemandePaiement,
        on_delete=models.PROTECT,
        related_name='paiements',
        verbose_name="Demande de paiement"
    )
    montant_paye = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant payé"
    )
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES)
    date_paiement = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de paiement"
    )
    paiement_par = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='paiements_effectues',
        limit_choices_to={'role__in': ['COMPTABLE', 'DAF', 'DG']},
        verbose_name="Effectué par"
    )
    observations = models.TextField(
        blank=True,
        verbose_name="Observations"
    )

    beneficiaire = models.CharField(max_length=50, verbose_name="Beneficiaire")
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']
        indexes = [
            models.Index(fields=['releve_depense']),
            models.Index(fields=['demande']),
            models.Index(fields=['date_paiement']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.montant_paye} {self.devise} - {self.demande.reference}"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            # Génération automatique de la référence
            count = Paiement.objects.count() + 1
            self.reference = f"PAY-{count:06d}"
        
        # Synchroniser la devise avec la demande
        if self.demande:
            self.devise = self.demande.devise
        
        super().save(*args, **kwargs)
        
        # Mettre à jour la demande après le paiement
        if self.demande:
            self.demande.montant_deja_paye += self.montant_paye
            self.demande.save()
        
        # Vérifier si toutes les demandes du relevé sont payées
        self.verifier_et_archiver_releve()
    
    def verifier_et_archiver_releve(self):
        """Vérifie si toutes les demandes liées à ce relevé sont payées et archive le relevé si c'est le cas"""
        if not self.releve_depense:
            return
            
        releve = self.releve_depense
        
        # Récupérer toutes les demandes de ce relevé
        demandes_liees = releve.demandes.all()
        
        # Vérifier si toutes les demandes sont entièrement payées
        toutes_payees = all(
            demande.reste_a_payer <= 0 
            for demande in demandes_liees
        )
        
        if toutes_payees:
            # Archiver le relevé de dépenses (ajouter un champ archive si nécessaire)
            print(f"Toutes les demandes du relevé {releve.periode} sont payées")
