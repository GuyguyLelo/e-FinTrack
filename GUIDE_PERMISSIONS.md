# Guide des Permissions et Rôles - e-FinTrack

## Rôles et Permissions Définis

### 1. Super Admin
- **Peut tout faire et tout voir**
- Accès complet à l'administration Django
- Peut créer/modifier/supprimer toutes les entités
- Peut valider toutes les demandes
- Peut effectuer tous les paiements

### 2. Admin
- **Peut créer les enregistrements des tables de base**
- Banques, comptes bancaires, utilisateurs, services, nature économique
- **Peut tout voir sans modification ou suppression**
- **Ne voit pas les interfaces utilisateurs** (juste l'administration Django)
- Accès consultation uniquement

### 3. DG (Directeur Général)
- **Peut voir le tableau de bord**
- **Peut voir la liste des demandes**
- **Peut voir les paiements**
- **Peut valider les demandes**
- **Sans modification** sur les autres entités

### 4. DF (Directeur Financier)
- **Peut tout voir sans modification**
- Accès consultation à tous les modules
- Pas de droits de modification ou de création

### 5. CD Finance (Chef de Division Finance)
- **Peut tout voir**
- **Peut créer des relevés**
- **Peut consulter les dépenses**
- **Peut créer des états**

### 6. Opérateur de Saisie
- **Peut saisir une demande**
- **Peut saisir une recette**
- **Ne peut pas voir le tableau de bord**

### 7. Agent Payeur
- **Peut effectuer les paiements**
- Accès limité au module paiements

## Structure des Permissions

### Méthodes de Permission Disponibles

```python
# Permissions d'accès général
user.peut_voir_tableau_bord()
user.peut_creer_entites_base()
user.peut_voir_tout_sans_modification()

# Permissions spécifiques
user.peut_valider_demandes()
user.peut_effectuer_paiements()
user.peut_creer_releves()
user.peut_consulter_depenses()
user.peut_creer_etats()
user.peut_saisir_demandes_recettes()

# Permissions de menu
user.peut_voir_menu_demandes()
user.peut_voir_menu_paiements()
user.peut_voir_menu_recettes()
user.peut_voir_menu_etats()
user.peut_acceder_admin_django()
```

### Utilisation dans les Vues

#### Avec les Mixins (Classes)
```python
from accounts.permissions import (
    TableauBordMixin, 
    CreerEntitesBaseMixin,
    SaisirDemandesRecettesMixin
)

class MaVue(TableauBordMixin, ListView):
    # Seuls les utilisateurs qui peuvent voir le tableau de bord
    # auront accès à cette vue
    pass
```

#### Avec les Décorateurs (Fonctions)
```python
from accounts.permissions import (
    tableau_bord_required,
    creer_entites_base_required,
    saisir_demandes_recettes_required
)

@tableau_bord_required
def ma_vue(request):
    # Seuls les utilisateurs qui peuvent voir le tableau de bord
    # auront accès à cette vue
    pass
```

### Utilisation dans les Templates

```html
{% if user.peut_voir_tableau_bord %}
    <a href="/tableau-bord/">Tableau de bord</a>
{% endif %}

{% if user.peut_creer_entites_base %}
    <button onclick="creerBanque()">Créer une banque</button>
{% endif %}

{% if user.peut_valider_demandes %}
    <button onclick="validerDemande()">Valider</button>
{% endif %}
```

## Menu de Navigation

Le menu dans `base.html` est automatiquement filtré selon les permissions :

- **Tableau de bord**: SUPER_ADMIN, ADMIN, DG, DF, CD_FINANCE
- **Banques/Comptes**: SUPER_ADMIN, ADMIN
- **Demandes**: SUPER_ADMIN, ADMIN, DG, DF, CD_FINANCE, AGENT_PAYEUR
- **Relevés de dépenses**: SUPER_ADMIN, CD_FINANCE
- **Paiements**: SUPER_ADMIN, ADMIN, DG, DF, CD_FINANCE, AGENT_PAYEUR
- **Consultation Dépenses**: SUPER_ADMIN, ADMIN, DG, DF, CD_FINANCE
- **Recettes**: SUPER_ADMIN, ADMIN, DG, DF, CD_FINANCE, OPERATEUR_SAISIE
- **Relevés bancaires**: SUPER_ADMIN, ADMIN, DG, DF
- **États et rapports**: SUPER_ADMIN, ADMIN, DG, DF, CD_FINANCE
- **Administration Django**: SUPER_ADMIN, ADMIN

## Tests de Permissions

Pour vérifier que les permissions fonctionnent correctement :

1. **Créer des utilisateurs de test** pour chaque rôle
2. **Se connecter avec chaque rôle** et vérifier :
   - Le menu affiché correspond aux permissions
   - L'accès aux URLs est correctement restreint
   - Les actions (créer, modifier, supprimer) sont disponibles ou non

3. **Tester les cas limites** :
   - Utilisateur non connecté
   - Utilisateur avec un rôle non reconnu
   - Tentative d'accès direct à une URL non autorisée

## Migration des Rôles Existants

Lors de la migration, les anciens rôles ont été remplacés :
- `DAF` → `ADMIN` (ou autre selon le contexte)
- `COMPTABLE` → `CD_FINANCE`
- `CHEF_SERVICE` → `OPERATEUR_SAISIE` (ou autre selon le contexte)
- `AUDITEUR` → `DF`

Les utilisateurs existants conserveront leur ancien rôle dans la base de données et devront être mis à jour manuellement via l'administration Django.
