# 📋 Workflow Complet : De la Demande au Paiement

## Table des matières
1. [Vue d'ensemble du processus](#vue-densemble-du-processus)
2. [Étape 1 : Création de la demande](#étape-1--création-de-la-demande)
3. [Étape 2 : Validation de la demande](#étape-2--validation-de-la-demande)
4. [Étape 3 : Création du relevé de dépense](#étape-3--création-du-relevé-de-dépense)
5. [Étape 4 : Validation des dépenses](#étape-4--validation-des-dépenses)
6. [Étape 5 : Génération du chèque](#étape-5--génération-du-chèque)
7. [États et statuts](#états-et-statuts)
8. [Rôles et permissions](#rôles-et-permissions)
9. [Schéma visuel du workflow](#schéma-visuel-du-workflow)
10. [Exemples pratiques](#exemples-pratiques)

---

## Vue d'ensemble du processus

Le système de gestion financière suit un workflow séquentiel complet :

```
CRÉATION → VALIDATION → RELEVÉ → VALIDATION DÉPENSES → GÉNÉRATION CHÈQUE → PAIEMENT
```

### Modèles impliqués
1. **DemandePaiement** : La demande initiale
2. **ReleveDepense** : Le relevé consolidé
3. **Depense** : La dépense validée
4. **Cheque** : Le chèque généré

---

## Étape 1 : Création de la demande

### Qui peut créer ?
- ✅ **Chef de Service** (CHEF_SERVICE)
- ✅ **Directeur Général** (DG)
- ✅ **Directeur Administratif et Financier** (DAF)
- ✅ **Directeur Financier** (DF)

### Processus

**URL** : `/demandes/creer/`  
**Vue** : `DemandePaiementCreateView`  
**Template** : `demandes/demande_form.html`

#### Informations requises :
- **Service demandeur** : Service qui fait la demande (auto-rempli pour chef de service)
- **Nature économique** : Classification comptable
- **Nomenclature** : Plan comptable (optionnel)
- **Date de demande** : Date de la demande
- **Description** : Détails de la demande
- **Montant** : Montant demandé
- **Devise** : CDF ou USD
- **Pièces justificatives** : Documents d'appui (optionnel)

#### Comportement automatique :
- ✅ Génération automatique de la référence : `DEM-000001`, `DEM-000002`, etc.
- ✅ Statut initial : `EN_ATTENTE`
- ✅ Enregistrement du créateur (`cree_par`)
- ✅ Date de soumission automatique

#### Code de génération de référence :
```python
def save(self, *args, **kwargs):
    if not self.reference:
        count = DemandePaiement.objects.count() + 1
        self.reference = f"DEM-{count:06d}"
    super().save(*args, **kwargs)
```

### État après création
```
DemandePaiement {
    reference: "DEM-000001"
    statut: "EN_ATTENTE"
    montant: 1000.00
    devise: "USD"
    cree_par: <User>
    date_soumission: <DateTime>
    approuve_par: None
    date_approbation: None
}
```

---

## Étape 2 : Validation de la demande

### Qui peut valider ?
- ✅ **Directeur Général** (DG) → Statut : `VALIDEE_DG`
- ✅ **Directeur Financier** (DF) → Statut : `VALIDEE_DF`
- ✅ **Directeur Administratif et Financier** (DAF) → Peut valider comme DG ou DF

### Processus

**URL** : `/demandes/<pk>/valider/`  
**Vue** : `DemandePaiementValidationView`  
**Template** : `demandes/demande_validation.html`

#### Actions possibles :

1. **Validation par le DG**
   - Statut → `VALIDEE_DG`
   - `approuve_par` = utilisateur validant
   - `date_approbation` = maintenant
   - `commentaire_rejet` = vide

2. **Validation par le DF**
   - Statut → `VALIDEE_DF`
   - `approuve_par` = utilisateur validant
   - `date_approbation` = maintenant
   - `commentaire_rejet` = vide

3. **Rejet**
   - Statut → `REJETEE`
   - `commentaire_rejet` = commentaire obligatoire
   - `approuve_par` = utilisateur rejetant
   - `date_approbation` = maintenant

#### Vérifications de sécurité :
- ✅ Seules les demandes en `EN_ATTENTE` peuvent être validées
- ✅ L'utilisateur doit avoir la permission `peut_valider_depense()`
- ✅ Les demandes rejetées ne peuvent plus être modifiées

### État après validation
```
DemandePaiement {
    reference: "DEM-000001"
    statut: "VALIDEE_DG" ou "VALIDEE_DF"
    approuve_par: <User (DG ou DF)>
    date_approbation: <DateTime>
    commentaire_rejet: ""
}
```

---

## Étape 3 : Création du relevé de dépense

### Qui peut créer ?
- ✅ **Directeur Administratif et Financier** (DAF)
- ✅ **Directeur Général** (DG)
- ✅ **Directeur Financier** (DF)

### Processus

#### Méthode 1 : Création automatique (recommandée)

**URL** : `/demandes/releves/generer/`  
**Vue** : `ReleveDepenseAutoCreateView`  
**Template** : `demandes/releve_auto_form.html`

**Processus** :
1. Sélection d'une période (mois)
2. Le système récupère automatiquement toutes les demandes :
   - ✅ Validées (`VALIDEE_DG`, `VALIDEE_DF`, `PAYEE`)
   - ✅ Non incluses dans un autre relevé
   - ✅ Correspondant à la période sélectionnée (basé sur `date_demande` ou `date_soumission`)
3. Création automatique du relevé avec toutes ces demandes
4. Calcul automatique des totaux (montant, IPR 3%, net à payer)

#### Méthode 2 : Création manuelle

**URL** : `/demandes/releves/creer/`  
**Vue** : `ReleveDepenseCreateView`  
**Template** : `demandes/releve_form.html`

**Processus** :
1. Sélection manuelle de la période
2. Sélection manuelle des demandes validées
3. Le système vérifie que les demandes ne sont pas déjà dans un relevé
4. Calcul automatique des totaux

### Calculs automatiques

Le système calcule automatiquement :

```python
# Pour chaque devise (CDF et USD)
montant_cdf = sum(demande.montant for demande in demandes if demande.devise == 'CDF')
montant_usd = sum(demande.montant for demande in demandes if demande.devise == 'USD')

# IPR (3%)
ipr_cdf = montant_cdf * Decimal('0.03')
ipr_usd = montant_usd * Decimal('0.03')

# Net à payer (montant - IPR)
net_a_payer_cdf = montant_cdf - ipr_cdf
net_a_payer_usd = montant_usd - ipr_usd
```

### Génération automatique du numéro

```python
def save(self, *args, **kwargs):
    if not self.numero:
        max_numero = ReleveDepense.objects.exclude(numero__isnull=True).aggregate(
            max_num=Max('numero')
        )['max_num']
        
        if max_numero:
            last_num = int(max_numero.split('-')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        self.numero = f"REL-{next_num:06d}"
    super().save(*args, **kwargs)
```

### Filtrage des demandes

**Liste des demandes disponibles** (`/demandes/releves/`) :
- ✅ Affiche uniquement les demandes validées
- ❌ Exclut automatiquement les demandes déjà dans un relevé
- ✅ Groupe par code de nature économique
- ✅ Affiche les sous-totaux par groupe

**Code de filtrage** :
```python
queryset = DemandePaiement.objects.filter(
    statut__in=['VALIDEE_DG', 'VALIDEE_DF', 'PAYEE']
).exclude(
    releves_depense__isnull=False  # Exclure celles déjà dans un relevé
)
```

### État après création
```
ReleveDepense {
    numero: "REL-000001"
    periode: <Date>
    demandes: [<DemandePaiement>, ...]
    montant_cdf: 0.00
    montant_usd: 1000.00
    ipr_cdf: 0.00
    ipr_usd: 30.00
    net_a_payer_cdf: 0.00
    net_a_payer_usd: 970.00
    valide_par: <User>
    depenses_validees: False
    date_creation: <DateTime>
}
```

---

## Étape 4 : Validation des dépenses

### Qui peut valider ?
- ✅ **Directeur Administratif et Financier** (DAF)
- ✅ **Directeur Général** (DG)
- ✅ **Directeur Financier** (DF)

### Processus

**URL** : `/demandes/releves/<pk>/valider-depenses/`  
**Vue** : `ReleveDepenseValiderDepensesView`  
**Méthode** : POST uniquement

**Processus détaillé** :

1. **Vérifications préalables** :
   - ✅ Les dépenses ne sont pas déjà validées
   - ✅ L'utilisateur a les permissions
   - ✅ Le relevé contient au moins une demande

2. **Création des objets Depense** :
   Pour chaque demande du relevé :
   ```python
   # Génération du code de dépense unique
   code_depense = f"DEP-{annee}-{mois:02d}-{numero:04d}"
   # Exemple: DEP-2024-01-0001
   
   # Création de l'objet Depense
   Depense.objects.create(
       code_depense=code_depense,
       mois=mois,
       annee=annee,
       date_depense=demande.date_demande or demande.date_soumission.date(),
       date_demande=demande.date_demande,
       nomenclature=demande.nomenclature,
       libelle_depenses=demande.description,
       montant_fc=demande.montant if demande.devise == 'CDF' else Decimal('0.00'),
       montant_usd=demande.montant if demande.devise == 'USD' else Decimal('0.00'),
       observation=f'Dépense validée depuis le relevé {releve.numero} - Demande {demande.reference}'
   )
   ```

3. **Marquage du relevé** :
   ```python
   releve.depenses_validees = True
   releve.depenses_validees_par = request.user
   releve.date_validation_depenses = timezone.now()
   releve.save()
   ```

### Génération du code de dépense

Le code suit le format : `DEP-YYYY-MM-NNNN`

- **YYYY** : Année (ex: 2024)
- **MM** : Mois sur 2 chiffres (ex: 01, 02, ..., 12)
- **NNNN** : Numéro séquentiel sur 4 chiffres (ex: 0001, 0002, ...)

**Exemple** :
- `DEP-2024-01-0001` : Première dépense de janvier 2024
- `DEP-2024-01-0002` : Deuxième dépense de janvier 2024
- `DEP-2024-02-0001` : Première dépense de février 2024

### État après validation
```
ReleveDepense {
    numero: "REL-000001"
    depenses_validees: True
    depenses_validees_par: <User>
    date_validation_depenses: <DateTime>
}

Depense {
    code_depense: "DEP-2024-01-0001"
    libelle_depenses: "..."
    montant_usd: 1000.00
    observation: "Dépense validée depuis le relevé REL-000001 - Demande DEM-000001"
    ...
}
```

---

## Étape 5 : Génération du chèque

### Qui peut générer ?
- ✅ **Tous les utilisateurs authentifiés** (accès à la fonctionnalité)

### Processus

**URL** : `/demandes/cheques/pdf/?releve_id=<pk>&banque_id=<pk>`  
**Vue** : `ChequePDFView`

**Étapes** :

1. **Sélection de la banque** :
   - Si `banque_id` n'est pas fourni, affichage d'un modal de sélection
   - Liste des banques actives disponibles

2. **Création ou récupération du chèque** :
   ```python
   cheque, created = Cheque.objects.get_or_create(
       releve_depense=releve,
       defaults={
           'banque': banque,
           'montant_cdf': releve.net_a_payer_cdf,
           'montant_usd': releve.net_a_payer_usd,
           'cree_par': request.user,
           'statut': 'GENERE'
       }
   )
   ```

3. **Génération automatique du numéro** :
   ```python
   def save(self, *args, **kwargs):
       if not self.numero_cheque:
           # Génération automatique: CHQ-000001, CHQ-000002, etc.
           numero = f"CHQ-{next_num:06d}"
           self.numero_cheque = numero
       super().save(*args, **kwargs)
   ```

4. **Génération du PDF** :
   - Création d'un document PDF avec ReportLab
   - Contenu :
     - Titre "CHÈQUE"
     - Numéro de chèque
     - Informations de la banque
     - Numéro de relevé
     - Montants (CDF et USD)
     - Montant en lettres (français)
     - Date
     - Bénéficiaire (si renseigné)
     - Observations (si renseigné)

### Statuts du chèque

- **GENERE** : Chèque généré (statut initial)
- **EMIS** : Chèque émis
- **ENCAISSE** : Chèque encaissé
- **ANNULE** : Chèque annulé

### Accès depuis l'interface

**Depuis la liste des relevés créés** (`/demandes/releves/crees/`) :
- Bouton avec icône de chèque dans la colonne "Actions"
- Génère directement le PDF

**Depuis le détail d'un relevé** (`/demandes/releves/<pk>/`) :
- Bouton "Imprimer chèque"
- Génère le PDF avec sélection de la banque

### État après génération
```
Cheque {
    numero_cheque: "CHQ-000001"
    releve_depense: <ReleveDepense (REL-000001)>
    banque: <Banque>
    montant_cdf: 0.00
    montant_usd: 970.00
    statut: "GENERE"
    cree_par: <User>
    date_creation: <DateTime>
    date_emission: None
    date_encaissement: None
}
```

---

## États et statuts

### Statuts de DemandePaiement

| Statut | Description | Qui peut changer | Étape suivante |
|--------|-------------|------------------|----------------|
| `EN_ATTENTE` | Demande créée, en attente de validation | Créateur peut modifier | Validation par DG/DF |
| `VALIDEE_DG` | Validée par le Directeur Général | DG, DAF | Inclure dans un relevé |
| `VALIDEE_DF` | Validée par le Directeur Financier | DF, DAF | Inclure dans un relevé |
| `PAYEE` | Payée | DAF, DF | - |
| `REJETEE` | Rejetée avec commentaire | DG, DF, DAF | - |

### États de ReleveDepense

| Champ | Valeur | Description |
|-------|--------|-------------|
| `depenses_validees` | `False` | Dépenses non encore validées |
| `depenses_validees` | `True` | Dépenses validées, objets `Depense` créés |
| `depenses_validees_par` | `<User>` | Utilisateur qui a validé |
| `date_validation_depenses` | `<DateTime>` | Date de validation |

### Statuts de Cheque

| Statut | Description | Peut être changé en |
|--------|-------------|---------------------|
| `GENERE` | Chèque généré (PDF créé) | EMIS, ANNULE |
| `EMIS` | Chèque émis | ENCAISSE, ANNULE |
| `ENCAISSE` | Chèque encaissé | - |
| `ANNULE` | Chèque annulé | - |

---

## Rôles et permissions

### Directeur Général (DG)
- ✅ Créer des demandes
- ✅ Valider des demandes → `VALIDEE_DG`
- ✅ Créer des relevés
- ✅ Valider les dépenses d'un relevé
- ✅ Générer des chèques
- ✅ Consulter tous les modules

### Directeur Administratif et Financier (DAF)
- ✅ Créer des demandes
- ✅ Valider des demandes → `VALIDEE_DG` ou `VALIDEE_DF`
- ✅ Créer des relevés
- ✅ Valider les dépenses d'un relevé
- ✅ Générer des chèques
- ✅ Consulter tous les modules

### Directeur Financier (DF)
- ✅ Créer des demandes
- ✅ Valider des demandes → `VALIDEE_DF`
- ✅ Créer des relevés
- ✅ Valider les dépenses d'un relevé
- ✅ Générer des chèques
- ✅ Consulter tous les modules

### Comptable (COMPTABLE)
- ❌ Créer des demandes (sauf si chef de service)
- ❌ Valider des demandes
- ❌ Créer des relevés
- ✅ Valider les dépenses d'un relevé
- ✅ Générer des chèques
- ✅ Consulter les demandes

### Chef de Service (CHEF_SERVICE)
- ✅ Créer des demandes (uniquement pour son service)
- ❌ Valider des demandes
- ❌ Créer des relevés
- ❌ Valider les dépenses
- ✅ Consulter ses demandes
- ✅ Modifier ses demandes en attente

### Opérateur de Saisie (OPERATEUR_SAISIE)
- ❌ Créer des demandes
- ❌ Valider des demandes
- ❌ Créer des relevés
- ❌ Valider les dépenses
- ✅ Consulter (selon permissions)

---

## Schéma visuel du workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    ÉTAPE 1 : CRÉATION                        │
│  Chef de Service crée une DemandePaiement                   │
│  • Statut: EN_ATTENTE                                        │
│  • Référence auto: DEM-000001                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   ÉTAPE 2 : VALIDATION                       │
│  DG ou DF valide la DemandePaiement                         │
│  • Statut: VALIDEE_DG ou VALIDEE_DF                         │
│  • approuve_par: <User>                                      │
│  • date_approbation: <DateTime>                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            ÉTAPE 3 : CRÉATION DU RELEVÉ                      │
│  DAF/DG/DF crée un ReleveDepense                            │
│  • Numéro auto: REL-000001                                   │
│  • Inclut plusieurs demandes validées                        │
│  • Calcule: montant, IPR 3%, net à payer                    │
│  • depenses_validees: False                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            ÉTAPE 4 : VALIDATION DES DÉPENSES                 │
│  DAF/DG/DF valide les dépenses                              │
│  • Crée des objets Depense pour chaque demande               │
│  • Code auto: DEP-YYYY-MM-NNNN                              │
│  • depenses_validees: True                                   │
│  • depenses_validees_par: <User>                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            ÉTAPE 5 : GÉNÉRATION DU CHÈQUE                    │
│  Utilisateur génère le PDF du chèque                        │
│  • Sélection de la banque                                    │
│  • Crée ou récupère l'objet Cheque                          │
│  • Numéro auto: CHQ-000001                                   │
│  • Statut: GENERE                                            │
│  • Génère le PDF avec montants en lettres                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  ÉTAPE 6 : PAIEMENT                          │
│  (Gestion manuelle du statut du chèque)                     │
│  • Statut: EMIS → ENCAISSE                                   │
│  • Ou: ANNULE                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Exemples pratiques

### Exemple 1 : Workflow complet simple

**1. Création** :
- Chef de Service crée une demande de 1000 USD
- Référence générée : `DEM-000001`
- Statut : `EN_ATTENTE`

**2. Validation** :
- DG valide la demande
- Statut : `VALIDEE_DG`
- `approuve_par` = DG
- `date_approbation` = 2024-01-15 10:30:00

**3. Création du relevé** :
- DAF crée automatiquement un relevé pour janvier 2024
- Numéro : `REL-000001`
- Inclut `DEM-000001`
- Montant USD : 1000.00
- IPR USD (3%) : 30.00
- Net à payer USD : 970.00

**4. Validation des dépenses** :
- DAF valide les dépenses du relevé
- Crée `Depense` : `DEP-2024-01-0001`
- Montant USD : 1000.00
- `depenses_validees` = True

**5. Génération du chèque** :
- Utilisateur génère le PDF du chèque
- Sélectionne la banque "BCDC"
- Crée `Cheque` : `CHQ-000001`
- Montant USD : 970.00
- Statut : `GENERE`
- PDF téléchargé

### Exemple 2 : Plusieurs demandes dans un relevé

**Demandes validées** :
- `DEM-000001` : 500 USD
- `DEM-000002` : 300 USD
- `DEM-000003` : 200 USD

**Relevé créé** : `REL-000001`
- Montant total USD : 1000.00
- IPR USD (3%) : 30.00
- Net à payer USD : 970.00

**Dépenses créées** :
- `DEP-2024-01-0001` : 500 USD (depuis DEM-000001)
- `DEP-2024-01-0002` : 300 USD (depuis DEM-000002)
- `DEP-2024-01-0003` : 200 USD (depuis DEM-000003)

**Chèque généré** : `CHQ-000001`
- Montant total USD : 970.00 (net à payer du relevé)

### Exemple 3 : Rejet d'une demande

**1. Création** :
- Demande `DEM-000004` créée : 2000 USD
- Statut : `EN_ATTENTE`

**2. Rejet** :
- DF rejette la demande
- Statut : `REJETEE`
- `commentaire_rejet` : "Budget insuffisant pour ce mois"
- `approuve_par` = DF

**3. Conséquence** :
- La demande ne peut plus être modifiée
- Elle n'apparaît pas dans les relevés
- Elle reste dans l'historique avec le statut "REJETEE"

---

## Points importants

### Sécurité et intégrité

1. **Une demande ne peut être dans qu'un seul relevé à la fois** :
   - Le système vérifie avant l'ajout
   - Les demandes déjà dans un relevé sont exclues automatiquement

2. **Validation unique** :
   - Les dépenses d'un relevé ne peuvent être validées qu'une seule fois
   - Le bouton disparaît après validation

3. **Traçabilité complète** :
   - Qui a créé : `cree_par`
   - Qui a validé : `approuve_par`, `depenses_validees_par`
   - Quand : `date_soumission`, `date_approbation`, `date_validation_depenses`

### Calculs automatiques

- ✅ IPR : Toujours 3% du montant
- ✅ Net à payer : Montant - IPR
- ✅ Totaux : Somme automatique par devise
- ✅ Numéros : Génération automatique séquentielle

### Filtrage intelligent

- ✅ Seules les demandes validées apparaissent pour créer un relevé
- ✅ Seules les demandes non dans un relevé sont affichées par défaut
- ✅ Mode historique disponible pour voir toutes les demandes

---

**Dernière mise à jour** : 2024  
**Auteur** : Documentation système e-Finance DAF  
**Version** : 1.0

