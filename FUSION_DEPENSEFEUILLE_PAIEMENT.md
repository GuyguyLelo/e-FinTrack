# Documentation - Fusion DepenseFeuille et Paiement

## 📋 Vue d'ensemble

La table `DepenseFeuille` a été fusionnée avec la fonctionnalité de paiement pour permettre deux modes de fonctionnement :

1. **Mode Direct** : Saisie simple comme dans le tableau_bord_feuille actuel
2. **Mode Workflow** : Processus complet Demande → Relevé → Paiement

## 🔄 Modes de Fonctionnement

### Mode Direct (Tableau bord)
- **URL** : `/demandes/depenses/feuille/creer/direct/`
- **Utilisation** : Saisie rapide des dépenses sans validation
- **Champs** : Mois, année, date, service, nature économique, libellé, banque, montants, observation
- **Idéal pour** : Saisie quotidienne, dépenses récurrentes

### Mode Workflow (Demande → Relevé → Paiement)
- **URL** : `/demandes/depenses/feuille/creer/workflow/`
- **Utilisation** : Processus complet avec traçabilité
- **Champs supplémentaires** : 
  - `demande` : Lien vers une demande de paiement existante
  - `releve_depense` : Lien vers un relevé de dépenses
  - `paiement_par` : Utilisateur qui a effectué le paiement
  - `beneficiaire` : Bénéficiaire du paiement
  - `date_paiement` : Date effective du paiement
- **Idéal pour** : Dépenses importantes, audits, traçabilité complète

## 🗃️ Structure de la Table DepenseFeuille

### Champs existants (mode direct)
```python
mois = models.PositiveSmallIntegerField()
annee = models.PositiveIntegerField()
date = models.DateField()
nature_economique = ForeignKey(NatureEconomique)
service_beneficiaire = ForeignKey(Service)
libelle_depenses = models.CharField()
banque = ForeignKey(Banque)
montant_fc = models.DecimalField()
montant_usd = models.DecimalField()
observation = models.TextField()
```

### Nouveaux champs (mode workflow)
```python
releve_depense = ForeignKey(ReleveDepense, null=True, blank=True)
demande = ForeignKey(DemandePaiement, null=True, blank=True)
paiement_par = ForeignKey(User, null=True, blank=True)
beneficiaire = models.CharField(max_length=200, null=True, blank=True)
date_paiement = models.DateTimeField(null=True, blank=True)
reference_paiement = models.CharField(max_length=50, null=True, blank=True)
```

## 🎯 Propriétés et Méthodes

### Propriétés utiles
```python
depense.is_mode_workflow     # True si utilise le mode workflow
depense.is_mode_direct       # True si utilise le mode direct
depense.est_payee           # Toujours True pour DepenseFeuille
depense.montant_total       # Somme des montants FC et USD
```

### Méthodes utiles
```python
depense.get_montant_in_devise('CDF')  # Retourne le montant CDF
depense.get_montant_in_devise('USD')  # Retourne le montant USD
depense.can_be_deleted_by(user)      # Vérifie les permissions
```

## 📝 Formulaires

### DepenseFeuilleForm
Formulaire de base avec tous les champs (optionnels pour workflow)

### DepenseFeuilleDirectForm
Formulaire spécialisé mode direct (cache les champs workflow)

### DepenseFeuilleWorkflowForm
Formulaire spécialisé mode workflow (champs workflow obligatoires)

## 🌐 URLs Disponibles

```
/demandes/depenses/feuille/                           # Liste
/demandes/depenses/feuille/creer/                     # Mode par défaut (direct)
/demandes/depenses/feuille/creer/direct/              # Mode direct
/demandes/depenses/feuille/creer/workflow/            # Mode workflow
/demandes/depenses/feuille/<id>/                      # Détail
/demandes/depenses/feuille/<id>/modifier/             # Modification
```

## 🔧 Migration

La migration `0002_depensefeuille_beneficiaire_and_more.py` a été appliquée pour ajouter les nouveaux champs.

## 🎨 Interface

Le formulaire inclut un sélecteur de mode qui permet de basculer entre :
- **Direct** : Formulaire simple, saisie rapide
- **Workflow** : Formulaire complet avec champs de traçabilité

## 📊 Affichage dans les Listes

Dans les listes, les dépenses s'affichent différemment selon le mode :
- `[DIRECT]` : Mode direct
- `[PAYÉ]` : Mode workflow avec référence de paiement

## 🔒 Permissions

Les permissions sont gérées selon le rôle de l'utilisateur et le mode de la dépense :
- **Mode workflow** : Plus restrictif (DG, DF principalement)
- **Mode direct** : Plus flexible (DG, DF, CD_FINANCE)

## 🚀 Utilisation Recommandée

1. **Pour les dépenses quotidiennes** : Utiliser le mode direct
2. **Pour les dépenses importantes** : Utiliser le mode workflow
3. **Pour les audits** : Le mode workflow offre une meilleure traçabilité
4. **Pour la saisie rapide** : Le mode direct est plus efficace

Cette approche hybride permet de conserver la flexibilité du tableau_bord_feuille tout en offrant la rigueur du processus de validation quand nécessaire.
