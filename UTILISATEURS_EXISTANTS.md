# Liste des Utilisateurs Existants - e-FinTrack

## Informations d'Authentification

**Important**: Les mots de passe par défaut ne sont pas stockés en clair pour des raisons de sécurité. 
Vous devrez les réinitialiser via l'administration Django ou créer de nouveaux utilisateurs.

## Utilisateurs Actuels

| Username | Email | Rôle Actuel | Actif | Nouveau Rôle Recommandé |
|----------|-------|-------------|-------|------------------------|
| admin | admin@dgrad.cd | DG | True | SUPER_ADMIN |
| auditeur | auditeur@dgrad.cd | AUDITEUR | True | DF |
| chef.service | chef.service@dgrad.cd | CHEF_SERVICE | True | CD_FINANCE |
| comptable1 | comptable1@dgrad.cd | COMPTABLE | True | CD_FINANCE |
| comptable2 | comptable2@dgrad.cd | COMPTABLE | True | CD_FINANCE |
| daf | daf@dgrad.cd | DAF | True | ADMIN |
| df | df@dgrad.cd | DF | True | DF |
| dg | dg@dgrad.cd | DG | True | DG |
| operateur1 | operateur1@dgrad.cd | OPERATEUR_SAISIE | True | OPERATEUR_SAISIE |
| operateur2 | operateur2@dgrad.cd | OPERATEUR_SAISIE | True | AGENT_PAYEUR |

## Mapping Anciens → Nouveaux Rôles

| Ancien Rôle | Nouveau Rôle | Utilisaires Concernés |
|-------------|---------------|----------------------|
| DG | DG | admin, dg |
| DAF | ADMIN | daf |
| DF | DF | df, auditeur |
| COMPTABLE | CD_FINANCE | comptable1, comptable2 |
| CHEF_SERVICE | CD_FINANCE | chef.service |
| OPERATEUR_SAISIE | OPERATEUR_SAISIE | operateur1 |
| OPERATEUR_SAISIE | AGENT_PAYEUR | operateur2 |
| AUDITEUR | DF | auditeur |

## Commandes pour Réinitialiser les Mots de Passe

```bash
# Accéder au shell Django
cd /home/mohamed-kandolo/e-FinTrack
source venv/bin/activate
python manage.py shell
```

```python
# Dans le shell Django
from accounts.models import User
from django.contrib.auth.hashers import make_password

# Réinitialiser le mot de passe de l'admin
admin = User.objects.get(username='admin')
admin.password = make_password('admin123')
admin.save()

# Réinitialiser le mot de passe du DG
dg = User.objects.get(username='dg')
dg.password = make_password('dg123')
dg.save()

# Réinitialiser le mot de passe de l'Agent Payeur
agent = User.objects.get(username='operateur2')
agent.password = make_password('payeur123')
agent.save()
```

## Mise à Jour des Rôles

```python
# Mettre à jour les rôles vers le nouveau système
from accounts.models import User

# Super Admin
User.objects.filter(username='admin').update(role='SUPER_ADMIN')

# Admin
User.objects.filter(username='daf').update(role='ADMIN')

# DG
User.objects.filter(username='dg').update(role='DG')

# DF
User.objects.filter(username__in=['df', 'auditeur']).update(role='DF')

# CD Finance
User.objects.filter(username__in=['comptable1', 'comptable2', 'chef.service']).update(role='CD_FINANCE')

# Opérateur de Saisie
User.objects.filter(username='operateur1').update(role='OPERATEUR_SAISIE')

# Agent Payeur
User.objects.filter(username='operateur2').update(role='AGENT_PAYEUR')
```

## Comptes de Test Suggérés

Après mise à jour, voici les comptes de test recommandés :

### Super Admin
- **Username**: admin
- **Password**: admin123
- **Rôle**: SUPER_ADMIN
- **Accès**: Tout

### DG (Directeur Général)
- **Username**: dg
- **Password**: dg123
- **Rôle**: DG
- **Accès**: Tableau bord, voir demandes, valider demandes, voir paiements

### CD Finance
- **Username**: comptable1
- **Password**: finance123
- **Rôle**: CD_FINANCE
- **Accès**: Tout voir, créer relevés, consulter dépenses, créer états

### Opérateur de Saisie
- **Username**: operateur1
- **Password**: saisie123
- **Rôle**: OPERATEUR_SAISIE
- **Accès**: Saisir demandes et recettes

### Agent Payeur
- **Username**: operateur2
- **Password**: payeur123
- **Rôle**: AGENT_PAYEUR
- **Accès**: Effectuer les paiements

## Étapes de Configuration

1. **Réinitialiser les mots de passe** avec les commandes ci-dessus
2. **Mettre à jour les rôles** selon le mapping
3. **Tester chaque compte** pour vérifier les permissions
4. **Documenter les accès** pour les utilisateurs finaux

## Notes de Sécurité

- Changez les mots de passe par défaut après la première connexion
- Utilisez des mots de passe forts pour la production
- Désactivez les comptes non utilisés
- Configurez des permissions supplémentaires si nécessaire
