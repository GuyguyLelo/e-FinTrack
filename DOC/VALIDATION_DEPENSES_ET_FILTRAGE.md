# Documentation : Validation des Dépenses et Filtrage des Demandes

## Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Workflow de validation des dépenses](#workflow-de-validation-des-dépenses)
3. [Filtrage des demandes dans les relevés](#filtrage-des-demandes-dans-les-relevés)
4. [Mode historique des demandes](#mode-historique-des-demandes)
5. [Modifications des modèles](#modifications-des-modèles)
6. [Vues et URLs](#vues-et-urls)
7. [Exemples d'utilisation](#exemples-dutilisation)

---

## Vue d'ensemble

Le système permet maintenant :
- ✅ **Créer des relevés de dépense** avec des demandes validées
- ✅ **Valider les dépenses** d'un relevé (créer des objets `Depense` à partir des demandes)
- ✅ **Filtrer automatiquement** les demandes déjà dans un relevé
- ✅ **Consulter l'historique complet** de toutes les demandes (y compris celles dans un relevé)

---

## Workflow de validation des dépenses

### Étape 1 : Création d'un relevé de dépense

Un relevé de dépense (`ReleveDepense`) est créé avec :
- Un numéro unique généré automatiquement (ex: `REL-000001`)
- Une période (mois)
- Des demandes de paiement validées associées

**Vues concernées** :
- `ReleveDepenseCreateView` : Création manuelle
- `ReleveDepenseAutoCreateView` : Création automatique à partir des demandes validées

### Étape 2 : Validation des dépenses

Une fois le relevé créé, l'étape suivante est de **valider les dépenses réalisées** sur base des demandes.

**Processus de validation** :

1. **Accès** : Depuis la page de détail du relevé (`/demandes/releves/<pk>/`)
2. **Bouton** : "Valider les dépenses" (visible uniquement si non validé et si l'utilisateur a les permissions)
3. **Action** : 
   - Pour chaque demande du relevé, crée un objet `Depense`
   - Génère un code de dépense unique (format : `DEP-YYYY-MM-NNNN`)
   - Copie les données de la demande vers la dépense
   - Marque le relevé comme validé

**Permissions requises** :
- DAF (Directeur Administratif et Financier)
- DG (Directeur Général)
- COMPTABLE

**Vue** : `ReleveDepenseValiderDepensesView`
**URL** : `/demandes/releves/<pk>/valider-depenses/` (POST uniquement)

### Étape 3 : Résultat

Après validation :
- ✅ Le relevé est marqué comme `depenses_validees = True`
- ✅ Les objets `Depense` sont créés dans la base de données
- ✅ Le bouton de validation disparaît
- ✅ Un badge "Dépenses validées" s'affiche
- ✅ Les informations de validation sont enregistrées (qui, quand)

---

## Filtrage des demandes dans les relevés

### Comportement par défaut

**Dans la liste des demandes validées pour créer un relevé** (`ReleveDepenseListView`) :
- ❌ Les demandes **déjà dans un relevé** sont **exclues automatiquement**
- ✅ Seules les demandes **disponibles** (non incluses dans un relevé) sont affichées

**Code** :
```python
queryset = queryset.exclude(releves_depense__isnull=False)
```

### Dans la liste générale des demandes

**Par défaut** (`DemandePaiementListView`) :
- ❌ Les demandes **déjà dans un relevé** sont **exclues**
- ✅ Seules les demandes **disponibles** sont affichées

**Avec le mode historique** (`?historique=true`) :
- ✅ **Toutes les demandes** sont affichées
- ✅ Les demandes dans un relevé sont **visuellement distinctes** :
  - Ligne en gris clair (opacité réduite)
  - Badge avec le(s) numéro(s) de relevé(s)

---

## Mode historique des demandes

### Activation

Le mode historique permet de voir **toutes les demandes**, y compris celles déjà dans un relevé.

**Activation** :
1. Aller dans la liste des demandes (`/demandes/`)
2. Cocher la case "Voir l'historique complet (toutes les demandes)"
3. Cliquer sur "Filtrer"

**URL** : `/demandes/?historique=true`

### Indicateurs visuels

**Badge dans l'en-tête des filtres** :
- 🟢 **Vert** : "Demandes disponibles (hors relevés)" - Mode normal
- 🔵 **Bleu** : "Mode historique (toutes les demandes)" - Mode historique

**Dans le tableau** :
- Les demandes dans un relevé ont :
  - Une ligne en gris clair (`table-secondary opacity-75`)
  - Un badge avec le numéro du relevé : `Dans relevé: REL-000001`

### Exemple

```
Référence: DEM-000001
Dans relevé: [REL-000001] [REL-000002]  ← Si dans plusieurs relevés
```

---

## Modifications des modèles

### Modèle `ReleveDepense`

**Nouveaux champs ajoutés** :

```python
# Validation des dépenses
depenses_validees = models.BooleanField(
    default=False, 
    verbose_name="Dépenses validées"
)

depenses_validees_par = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='releves_depenses_validees',
    limit_choices_to={'role__in': ['DAF', 'DG', 'COMPTABLE']},
    verbose_name="Dépenses validées par"
)

date_validation_depenses = models.DateTimeField(
    null=True, 
    blank=True, 
    verbose_name="Date de validation des dépenses"
)
```

**Migration** : `0018_add_validation_depenses_to_relevedepense.py`

---

## Vues et URLs

### Vues de validation

#### `ReleveDepenseValiderDepensesView`

**Fichier** : `demandes/views.py` (ligne 1157)

**Méthode** : POST uniquement

**Fonctionnalités** :
- Vérifie que les dépenses ne sont pas déjà validées
- Vérifie les permissions de l'utilisateur
- Pour chaque demande du relevé :
  - Génère un code de dépense unique
  - Crée un objet `Depense`
  - Évite les doublons
- Marque le relevé comme validé

**URL** : `/demandes/releves/<int:pk>/valider-depenses/`
**Nom** : `releve_valider_depenses`

### Vues de filtrage

#### `DemandePaiementListView`

**Modifications** :
- Exclusion par défaut des demandes dans un relevé
- Support du paramètre `?historique=true` pour voir toutes les demandes
- Optimisation avec `prefetch_related('releves_depense')`

#### `ReleveDepenseListView`

**Modifications** :
- Exclusion automatique des demandes déjà dans un relevé
- Seules les demandes disponibles sont affichées

---

## Exemples d'utilisation

### Exemple 1 : Valider les dépenses d'un relevé

```python
# Via l'interface web
# 1. Aller sur /demandes/releves/1/
# 2. Cliquer sur "Valider les dépenses"
# 3. Confirmer l'action

# Résultat :
# - Des objets Depense sont créés
# - Le relevé est marqué comme validé
```

### Exemple 2 : Voir les demandes disponibles

```python
# URL : /demandes/
# Par défaut, seules les demandes non dans un relevé sont affichées

# Dans le code :
demandes_disponibles = DemandePaiement.objects.filter(
    statut__in=['VALIDEE_DG', 'VALIDEE_DF', 'PAYEE']
).exclude(
    releves_depense__isnull=False
)
```

### Exemple 3 : Voir l'historique complet

```python
# URL : /demandes/?historique=true
# Toutes les demandes sont affichées, y compris celles dans un relevé

# Dans le code :
toutes_demandes = DemandePaiement.objects.all()
# Les demandes dans un relevé sont visuellement distinctes
```

### Exemple 4 : Vérifier si une demande est dans un relevé

```python
demande = DemandePaiement.objects.get(reference="DEM-000001")

# Vérifier si dans un relevé
if demande.releves_depense.exists():
    print("Cette demande est dans un relevé")
    for releve in demande.releves_depense.all():
        print(f"  - Relevé {releve.numero}")
else:
    print("Cette demande est disponible")
```

### Exemple 5 : Lister les demandes d'un relevé et leurs dépenses validées

```python
releve = ReleveDepense.objects.get(numero="REL-000001")

# Vérifier si les dépenses sont validées
if releve.depenses_validees:
    print(f"Dépenses validées le {releve.date_validation_depenses}")
    print(f"Validé par : {releve.depenses_validees_par}")
    
    # Les dépenses créées ont dans leur observation le numéro du relevé
    depenses = Depense.objects.filter(
        observation__contains=f"relevé {releve.numero}"
    )
    print(f"Nombre de dépenses créées : {depenses.count()}")
else:
    print("Les dépenses ne sont pas encore validées")
```

---

## Schéma du workflow

```
┌─────────────────────────────────┐
│  DemandePaiement (VALIDEE)      │
│  ───────────────────────────    │
│  • reference: DEM-000001        │
│  • statut: VALIDEE_DG          │
│  • montant: 1000 USD           │
└─────────────────────────────────┘
            │
            │ Création du relevé
            ▼
┌─────────────────────────────────┐
│  ReleveDepense                  │
│  ───────────────────────────    │
│  • numero: REL-000001           │
│  • periode: 2024-01-01          │
│  • demandes: [DEM-000001, ...]  │
│  • depenses_validees: False      │
└─────────────────────────────────┘
            │
            │ Validation des dépenses
            ▼
┌─────────────────────────────────┐
│  Depense (créée)                 │
│  ───────────────────────────     │
│  • code_depense: DEP-2024-01-0001│
│  • libelle_depenses: ...         │
│  • montant_usd: 1000             │
│  • observation: "Dépense validée │
│    depuis le relevé REL-000001"  │
└─────────────────────────────────┘
            │
            │ Mise à jour du relevé
            ▼
┌─────────────────────────────────┐
│  ReleveDepense (mis à jour)     │
│  ───────────────────────────    │
│  • depenses_validees: True       │
│  • depenses_validees_par: User   │
│  • date_validation_depenses: ...│
└─────────────────────────────────┘
```

---

## Filtrage dans les listes

### Liste des demandes validées (pour créer un relevé)

**URL** : `/demandes/releves/`

**Comportement** :
- ✅ Affiche uniquement les demandes validées **non dans un relevé**
- ❌ Les demandes déjà dans un relevé sont **toujours exclues**

**Code** :
```python
queryset = DemandePaiement.objects.filter(
    statut__in=['VALIDEE_DG', 'VALIDEE_DF', 'PAYEE']
).exclude(
    releves_depense__isnull=False
)
```

### Liste générale des demandes

**URL** : `/demandes/`

**Comportement par défaut** :
- ✅ Affiche uniquement les demandes **non dans un relevé**
- ❌ Les demandes déjà dans un relevé sont **exclues**

**Mode historique** (`?historique=true`) :
- ✅ Affiche **toutes les demandes**
- ✅ Les demandes dans un relevé sont **visuellement distinctes**

**Code** :
```python
voir_historique = request.GET.get('historique', 'false').lower() == 'true'
if not voir_historique:
    queryset = queryset.exclude(releves_depense__isnull=False)
```

---

## Interface utilisateur

### Page de détail du relevé

**Bouton "Valider les dépenses"** :
- Visible si : `not releve.depenses_validees and user.peut_valider_depense()`
- Action : POST vers `/demandes/releves/<pk>/valider-depenses/`
- Confirmation : Dialog JavaScript avant validation

**Badge "Dépenses validées"** :
- Visible si : `releve.depenses_validees == True`
- Affiche : Qui a validé et quand

**Lien "Voir les dépenses validées"** :
- Visible si : `releve.depenses_validees == True`
- Redirige vers : `/demandes/depenses/?releve=REL-000001`

### Liste des demandes

**Checkbox "Voir l'historique complet"** :
- Position : Dans les filtres
- Fonction : Active/désactive le mode historique
- Badge d'indication : Affiche le mode actif

**Indication visuelle dans le tableau** :
- Ligne grise pour les demandes dans un relevé
- Badge avec numéro(s) de relevé(s)

---

## Sécurité et permissions

### Validation des dépenses

**Permissions requises** :
- `user.peut_valider_depense()` doit retourner `True`
- Rôles autorisés : `DAF`, `DG`, `COMPTABLE`

**Vérifications** :
1. ✅ Les dépenses ne sont pas déjà validées
2. ✅ L'utilisateur a les permissions
3. ✅ Le relevé contient des demandes
4. ✅ Confirmation avant validation

### Filtrage

**Aucune restriction** : Tous les utilisateurs peuvent :
- Voir les demandes disponibles
- Activer le mode historique
- Voir toutes les demandes

---

## Bonnes pratiques

1. **Toujours vérifier avant validation** :
   ```python
   if releve.depenses_validees:
       # Ne pas valider à nouveau
   ```

2. **Utiliser prefetch_related** pour optimiser :
   ```python
   queryset = queryset.prefetch_related('releves_depense')
   ```

3. **Vérifier l'existence avant d'accéder** :
   ```python
   if demande.releves_depense.exists():
       # La demande est dans un relevé
   ```

4. **Utiliser des transactions** pour les opérations critiques :
   ```python
   from django.db import transaction
   with transaction.atomic():
       # Créer les dépenses
       # Marquer le relevé comme validé
   ```

---

## Questions fréquentes

### Q : Peut-on valider les dépenses plusieurs fois ?
**R** : Non, une fois validées, le bouton disparaît et une nouvelle validation n'est pas possible.

### Q : Que se passe-t-il si une demande est dans plusieurs relevés ?
**R** : C'est possible en théorie (relation Many-to-Many), mais en pratique, une demande ne devrait être que dans un seul relevé par période.

### Q : Comment voir les dépenses créées à partir d'un relevé ?
**R** : Les dépenses ont dans leur champ `observation` le numéro du relevé. Vous pouvez filtrer :
```python
depenses = Depense.objects.filter(
    observation__contains=f"relevé {releve.numero}"
)
```

### Q : Les demandes dans un relevé peuvent-elles être modifiées ?
**R** : Oui, mais cela peut affecter les totaux du relevé. Il faut recalculer avec `releve.calculer_total()`.

### Q : Comment annuler la validation des dépenses ?
**R** : Actuellement, il n'y a pas de fonctionnalité d'annulation. Il faudrait :
- Supprimer manuellement les objets `Depense` créés
- Remettre `depenses_validees = False` sur le relevé

---

## Conclusion

Le système de validation des dépenses permet :
- ✅ De créer des relevés avec des demandes validées
- ✅ De valider les dépenses réalisées à partir d'un relevé
- ✅ De filtrer automatiquement les demandes déjà dans un relevé
- ✅ De consulter l'historique complet quand nécessaire
- ✅ D'avoir une traçabilité complète (qui, quand, quoi)

Cette architecture garantit la **cohérence** et la **traçabilité** des données financières.

---

**Dernière mise à jour** : 2024  
**Auteur** : Documentation système e-Finance DAF

