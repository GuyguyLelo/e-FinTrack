# Documentation : Relevé de Dépense et Réimpression

## Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Modèles impliqués](#modèles-impliqués)
3. [Relation Many-to-Many](#relation-many-to-many)
4. [Utilisation pratique](#utilisation-pratique)
5. [Réimpression des relevés](#réimpression-des-relevés)
6. [Exemples de code](#exemples-de-code)

---

## Vue d'ensemble

Le système de relevé de dépense permet de :
- **Créer des relevés** consolidant plusieurs demandes de paiement
- **Générer des PDF/Excel** avec mise en forme professionnelle
- **Réimprimer des relevés** existants à partir de leur numéro unique
- **Traçabilité complète** : chaque relevé a un numéro unique et conserve les demandes associées

---

## Modèles impliqués

### 1. Modèle `ReleveDepense`

**Fichier** : `demandes/models.py`

**Description** : Représente un relevé de dépense consolidé qui regroupe plusieurs demandes de paiement.

**Champs principaux** :
```python
class ReleveDepense(models.Model):
    numero = models.CharField(...)  # Numéro unique (ex: REL-000001)
    periode = models.DateField(...)  # Période du relevé
    demandes = models.ManyToManyField(DemandePaiement, ...)  # Relation avec les demandes
    
    # Montants calculés
    montant_cdf = models.DecimalField(...)
    montant_usd = models.DecimalField(...)
    ipr_cdf = models.DecimalField(...)  # IPR 3%
    ipr_usd = models.DecimalField(...)
    net_a_payer_cdf = models.DecimalField(...)
    net_a_payer_usd = models.DecimalField(...)
    
    # Métadonnées
    valide_par = models.ForeignKey(User, ...)
    date_creation = models.DateTimeField(auto_now_add=True)
    observation = models.TextField(...)
```

**Caractéristiques** :
- ✅ Numéro unique généré automatiquement : `REL-000001`, `REL-000002`, etc.
- ✅ Un seul relevé par période (contrainte `unique_together = ['periode']`)
- ✅ Calcul automatique des totaux via la méthode `calculer_total()`

### 2. Modèle `DemandePaiement`

**Fichier** : `demandes/models.py`

**Description** : Représente une demande de paiement individuelle.

**Champs principaux** :
```python
class DemandePaiement(models.Model):
    reference = models.CharField(...)  # Référence unique (ex: DEM-000001)
    nature_economique = models.ForeignKey('NatureEconomique', ...)  # Code de nature
    montant = models.DecimalField(...)
    devise = models.CharField(...)  # USD ou CDF
    statut = models.CharField(...)  # EN_ATTENTE, VALIDEE_DG, VALIDEE_DF, PAYEE, etc.
    # ... autres champs
```

**Caractéristiques** :
- ✅ Référence unique générée automatiquement
- ✅ Peut être associée à plusieurs relevés (relation Many-to-Many)
- ✅ Accès inverse aux relevés via `demande.releves_depense.all()`

---

## Relation Many-to-Many

### Définition

La relation entre `ReleveDepense` et `DemandePaiement` est une **relation Many-to-Many** (Plusieurs-à-plusieurs) :

- **Un relevé** peut contenir **plusieurs demandes**
- **Une demande** peut appartenir à **plusieurs relevés** (en théorie)

### Champ de liaison

**Dans le modèle `ReleveDepense`** (ligne 125) :
```python
demandes = models.ManyToManyField(
    DemandePaiement, 
    related_name='releves_depense'
)
```

**Explication** :
- `demandes` : nom du champ dans `ReleveDepense`
- `DemandePaiement` : modèle cible
- `related_name='releves_depense'` : permet l'accès inverse depuis `DemandePaiement`

### Table de liaison dans la base de données

Django crée automatiquement une table intermédiaire :

**Nom de la table** : `demandes_relevedepense_demandes`

**Structure** :
```
┌─────────────────────┬──────────────────────┐
│ relevedepense_id    │ demandepaiement_id   │
├─────────────────────┼──────────────────────┤
│ 1                   │ 5                    │
│ 1                   │ 6                    │
│ 1                   │ 7                    │
│ 2                   │ 8                    │
│ 2                   │ 9                    │
└─────────────────────┴──────────────────────┘
```

---

## Utilisation pratique

### 1. Accéder aux demandes d'un relevé

```python
# Récupérer un relevé
releve = ReleveDepense.objects.get(numero="REL-000001")

# Accéder aux demandes associées
demandes = releve.demandes.all()

# Filtrer les demandes
demandes_usd = releve.demandes.filter(devise='USD')
demandes_cdf = releve.demandes.filter(devise='CDF')

# Compter les demandes
nombre_demandes = releve.demandes.count()
```

### 2. Accéder aux relevés d'une demande

```python
# Récupérer une demande
demande = DemandePaiement.objects.get(reference="DEM-000001")

# Accéder aux relevés qui contiennent cette demande
releves = demande.releves_depense.all()

# Vérifier si une demande est dans un relevé
releve = ReleveDepense.objects.get(numero="REL-000001")
if demande in releve.demandes.all():
    print("La demande est dans ce relevé")
```

### 3. Créer un relevé et y ajouter des demandes

```python
# Créer un relevé
releve = ReleveDepense.objects.create(
    periode=date(2024, 1, 1),
    valide_par=user,
    observation="Relevé du mois de janvier"
)

# Ajouter des demandes
demandes = DemandePaiement.objects.filter(statut='VALIDEE_DG')
releve.demandes.set(demandes)  # Remplace toutes les demandes
# OU
releve.demandes.add(*demandes)  # Ajoute les demandes
# OU
releve.demandes.add(demande1, demande2)  # Ajoute des demandes spécifiques

# Calculer les totaux
releve.calculer_total()
```

### 4. Retirer une demande d'un relevé

```python
releve = ReleveDepense.objects.get(numero="REL-000001")
demande = DemandePaiement.objects.get(reference="DEM-000001")

# Retirer la demande
releve.demandes.remove(demande)

# Recalculer les totaux
releve.calculer_total()
```

---

## Réimpression des relevés

### Vue de réimpression : `ReleveDepenseReprintPDFView`

**Fichier** : `demandes/views.py` (ligne 885)

**URL** : `/demandes/releves/reimprimer/pdf/?numero=REL-000001`

### Logique de réimpression

#### Étape 1 : Récupération du relevé par numéro
```python
releve = ReleveDepense.objects.get(numero=numero)
```
- Recherche le relevé avec le numéro fourni
- Si introuvable → message d'erreur

#### Étape 2 : Récupération des demandes associées
```python
demandes = releve.demandes.all().select_related(
    'service_demandeur', 'cree_par', 'approuve_par', 'nature_economique'
).order_by('nature_economique__code', '-date_soumission')
```
- Accède aux demandes via la relation Many-to-Many (`releve.demandes`)
- `select_related()` optimise les requêtes SQL
- Tri par code de nature économique puis par date

#### Étape 3 : Calcul des totaux
```python
montant_cdf = sum(d.montant for d in demandes if d.devise == 'CDF')
montant_usd = sum(d.montant for d in demandes if d.devise == 'USD')
ipr_cdf = montant_cdf * Decimal('0.03')
ipr_usd = montant_usd * Decimal('0.03')
net_a_payer_cdf = montant_cdf + ipr_cdf
net_a_payer_usd = montant_usd + ipr_usd
```

#### Étape 4 : Groupement par code de nature économique
```python
demandes_par_code = defaultdict(list)
for demande in demandes:
    code = demande.nature_economique.code if demande.nature_economique else 'Sans code'
    demandes_par_code[code].append(demande)
```

#### Étape 5 : Calcul des sous-totaux par code
```python
sous_totaux = {}
for code, demandes_groupe in demandes_par_code.items():
    montant_usd_groupe = sum(d.montant for d in demandes_groupe if d.devise == 'USD')
    montant_cdf_groupe = sum(d.montant for d in demandes_groupe if d.devise == 'CDF')
    # ... calculs IPR et net à payer
```

#### Étape 6 : Génération du PDF
- Utilise ReportLab pour créer le PDF
- Affiche le numéro du relevé dans le titre : `RELEVÉ DE DÉPENSE N° REL-000001 DU 15/01/2024`
- Même format que lors de la création initiale

### Avantages de la réimpression

✅ **Fidélité** : Les données sont exactement les mêmes qu'à la création  
✅ **Traçabilité** : Chaque relevé a un numéro unique  
✅ **Performance** : Les données sont déjà stockées, pas besoin de recalculer depuis toutes les demandes  
✅ **Historique** : Possibilité de réimprimer des relevés anciens

---

## Exemples de code

### Exemple 1 : Créer un relevé automatiquement

```python
from demandes.models import ReleveDepense, DemandePaiement
from django.utils import timezone
from decimal import Decimal

# Récupérer les demandes validées
demandes_validees = DemandePaiement.objects.filter(
    statut__in=['VALIDEE_DG', 'VALIDEE_DF', 'PAYEE']
)

# Créer le relevé
periode = timezone.now().date().replace(day=1)
releve = ReleveDepense.objects.create(
    periode=periode,
    valide_par=request.user,
    observation="Relevé généré automatiquement"
)

# Ajouter les demandes
releve.demandes.set(demandes_validees)

# Calculer les totaux
releve.calculer_total()

print(f"Relevé créé : {releve.numero}")
print(f"Nombre de demandes : {releve.demandes.count()}")
print(f"Total CDF : {releve.montant_cdf}")
print(f"Total USD : {releve.montant_usd}")
```

### Exemple 2 : Lister tous les relevés avec leurs demandes

```python
releves = ReleveDepense.objects.all().prefetch_related('demandes')

for releve in releves:
    print(f"\nRelevé {releve.numero} - Période : {releve.periode}")
    print(f"Nombre de demandes : {releve.demandes.count()}")
    print(f"Total général : {releve.get_total_general()}")
    
    for demande in releve.demandes.all():
        print(f"  - {demande.reference} : {demande.montant} {demande.devise}")
```

### Exemple 3 : Trouver tous les relevés contenant une demande spécifique

```python
demande = DemandePaiement.objects.get(reference="DEM-000001")

# Accéder aux relevés via le related_name
releves = demande.releves_depense.all()

print(f"La demande {demande.reference} est dans {releves.count()} relevé(s) :")
for releve in releves:
    print(f"  - {releve.numero} (Période : {releve.periode})")
```

### Exemple 4 : Vérifier si une demande peut être ajoutée à un relevé

```python
def peut_ajouter_demande(releve, demande):
    """Vérifie si une demande peut être ajoutée à un relevé"""
    # Vérifier que la demande est validée
    if demande.statut not in ['VALIDEE_DG', 'VALIDEE_DF', 'PAYEE']:
        return False, "La demande n'est pas validée"
    
    # Vérifier que la demande n'est pas déjà dans le relevé
    if demande in releve.demandes.all():
        return False, "La demande est déjà dans ce relevé"
    
    return True, "OK"

# Utilisation
releve = ReleveDepense.objects.get(numero="REL-000001")
demande = DemandePaiement.objects.get(reference="DEM-000001")

peut_ajouter, message = peut_ajouter_demande(releve, demande)
if peut_ajouter:
    releve.demandes.add(demande)
    releve.calculer_total()
    print("Demande ajoutée avec succès")
else:
    print(f"Erreur : {message}")
```

### Exemple 5 : Calculer les statistiques d'un relevé

```python
def statistiques_releve(releve):
    """Calcule les statistiques d'un relevé"""
    demandes = releve.demandes.all()
    
    stats = {
        'total_demandes': demandes.count(),
        'demandes_usd': demandes.filter(devise='USD').count(),
        'demandes_cdf': demandes.filter(devise='CDF').count(),
        'montant_total_usd': sum(d.montant for d in demandes if d.devise == 'USD'),
        'montant_total_cdf': sum(d.montant for d in demandes if d.devise == 'CDF'),
        'codes_nature': demandes.values_list('nature_economique__code', flat=True).distinct()
    }
    
    return stats

# Utilisation
releve = ReleveDepense.objects.get(numero="REL-000001")
stats = statistiques_releve(releve)

print(f"Statistiques du relevé {releve.numero}:")
print(f"  Total demandes : {stats['total_demandes']}")
print(f"  Demandes USD : {stats['demandes_usd']}")
print(f"  Demandes CDF : {stats['demandes_cdf']}")
print(f"  Montant total USD : {stats['montant_total_usd']}")
print(f"  Montant total CDF : {stats['montant_total_cdf']}")
print(f"  Codes de nature : {list(stats['codes_nature'])}")
```

---

## Schéma de la relation

```
┌─────────────────────────────────┐
│      ReleveDepense              │
│  ───────────────────────────    │
│  • numero (REL-000001)          │
│  • periode                      │
│  • montant_cdf                  │
│  • montant_usd                  │
│  • ipr_cdf                      │
│  • ipr_usd                      │
│  • net_a_payer_cdf              │
│  • net_a_payer_usd              │
│  • valide_par                   │
│  • date_creation                │
│                                 │
│  ┌───────────────────────────┐  │
│  │ demandes (ManyToMany)     │  │◄──┐
│  └───────────────────────────┘  │   │
└─────────────────────────────────┘   │
                                      │
                    Table de liaison  │
                    ┌─────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │ relevedepense_demandes    │
        │ ─────────────────────     │
        │ • relevedepense_id        │
        │ • demandepaiement_id      │
        └───────────────────────────┘
                    │
                    │
                    ▼
┌─────────────────────────────────┐
│      DemandePaiement            │
│  ───────────────────────────    │
│  • reference (DEM-000001)       │
│  • nature_economique            │
│  • montant                      │
│  • devise (USD/CDF)             │
│  • statut                       │
│  • date_soumission              │
│                                 │
│  ┌───────────────────────────┐  │
│  │ releves_depense            │  │
│  │ (related_name)            │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

---

## Méthodes utiles du modèle ReleveDepense

### `calculer_total()`

Calcule automatiquement tous les montants du relevé à partir des demandes associées.

```python
releve.calculer_total()
# Met à jour :
# - montant_cdf, montant_usd
# - ipr_cdf, ipr_usd
# - net_a_payer_cdf, net_a_payer_usd
# - total (compatibilité)
```

### `get_total_general()`

Retourne le total général (CDF + USD).

```python
total = releve.get_total_general()
```

---

## Bonnes pratiques

1. **Toujours recalculer après modification** :
   ```python
   releve.demandes.add(demande)
   releve.calculer_total()  # Important !
   ```

2. **Utiliser `select_related()` et `prefetch_related()`** pour optimiser les requêtes :
   ```python
   releves = ReleveDepense.objects.all().prefetch_related('demandes')
   ```

3. **Vérifier l'existence avant d'accéder** :
   ```python
   try:
       releve = ReleveDepense.objects.get(numero=numero)
   except ReleveDepense.DoesNotExist:
       # Gérer l'erreur
   ```

4. **Utiliser des transactions pour les opérations critiques** :
   ```python
   from django.db import transaction
   with transaction.atomic():
       releve = ReleveDepense.objects.create(...)
       releve.demandes.set(demandes)
       releve.calculer_total()
   ```

---

## Questions fréquentes

### Q : Comment savoir si une demande est déjà dans un relevé ?
```python
releve = ReleveDepense.objects.get(numero="REL-000001")
demande = DemandePaiement.objects.get(reference="DEM-000001")

if demande in releve.demandes.all():
    print("Déjà dans le relevé")
```

### Q : Comment obtenir le nombre de demandes par devise dans un relevé ?
```python
releve = ReleveDepense.objects.get(numero="REL-000001")
nb_usd = releve.demandes.filter(devise='USD').count()
nb_cdf = releve.demandes.filter(devise='CDF').count()
```

### Q : Comment supprimer toutes les demandes d'un relevé ?
```python
releve = ReleveDepense.objects.get(numero="REL-000001")
releve.demandes.clear()
releve.calculer_total()
```

### Q : Comment copier les demandes d'un relevé vers un autre ?
```python
releve_source = ReleveDepense.objects.get(numero="REL-000001")
releve_dest = ReleveDepense.objects.get(numero="REL-000002")

releve_dest.demandes.set(releve_source.demandes.all())
releve_dest.calculer_total()
```

---

## Conclusion

La relation Many-to-Many entre `ReleveDepense` et `DemandePaiement` permet :
- ✅ De regrouper plusieurs demandes dans un relevé
- ✅ De conserver l'historique des relevés
- ✅ De réimprimer des relevés avec les mêmes données
- ✅ D'avoir une traçabilité complète avec les numéros uniques

Cette architecture garantit la **fidélité** et la **traçabilité** des relevés de dépense.

---

**Dernière mise à jour** : 2024  
**Auteur** : Documentation système e-Finance DAF

