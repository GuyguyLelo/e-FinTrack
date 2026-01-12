# 👥 Utilisateurs par Rôle - e-Finance DAF

## 🔑 Identifiants de connexion

### Rôles de Direction

| Username | Rôle | Mot de passe | Service | Permissions |
|----------|------|--------------|---------|-------------|
| **admin** | Administrateur | `admin` | Direction Générale | Toutes les permissions |
| **dg** | Directeur Général | `dg123456` | Direction Générale | Valide dépenses importantes, consulte tous les rapports |
| **daf** | Directeur Administratif et Financier | `daf123456` | Direction Générale | Supervise validations, approuve relevés |
| **df** | Directeur Financier | `df123456` | Service Financier | Vérifie disponibilité budgétaire, valide paiements |

### Rôles Opérationnels

| Username | Rôle | Mot de passe | Service | Permissions |
|----------|------|--------------|---------|-------------|
| **comptable1** | Comptable | `comptable123` | Service Comptable | Exécute paiements, enregistre recettes, valide relevés |
| **comptable2** | Comptable | `comptable123` | Service Comptable | Exécute paiements, enregistre recettes, valide relevés |
| **chef_service** | Chef de Service | `chef123456` | Service Financier | Crée et suit les demandes de paiement |
| **auditeur** | Auditeur | `audit123456` | Service Audit | Consulte tous les modules, valide rapprochements |
| **operateur1** | Opérateur de Saisie | `operateur123` | Service Comptable | Saisit relevés, encode recettes/dépenses |
| **operateur2** | Opérateur de Saisie | `operateur123` | Service Comptable | Saisit relevés, encode recettes/dépenses |

## 📋 Récapitulatif des permissions

### Directeur Général (DG)
- ✅ Valide les dépenses importantes
- ✅ Consulte tous les rapports consolidés
- ✅ Accès complet à toutes les fonctionnalités

### Directeur Administratif et Financier (DAF)
- ✅ Supervise les validations
- ✅ Approuve les relevés consolidés
- ✅ Consulte tous les modules

### Directeur Financier (DF)
- ✅ Vérifie la disponibilité budgétaire
- ✅ Valide les paiements
- ✅ Valide les rapprochements bancaires
- ✅ Valide les relevés bancaires

### Comptable
- ✅ Exécute les paiements
- ✅ Enregistre les recettes
- ✅ Valide les recettes
- ✅ Valide les relevés bancaires

### Chef de Service
- ✅ Crée les demandes de paiement
- ✅ Suit les demandes de son service
- ❌ Ne peut pas valider les demandes

### Auditeur
- ✅ Consulte tous les modules
- ✅ Génère les rapports d'audit
- ✅ Valide les rapprochements bancaires

### Opérateur de Saisie
- ✅ Saisit les relevés bancaires
- ✅ Encode les recettes
- ✅ Encode les dépenses
- ❌ Ne peut pas valider

## 🔐 Sécurité

⚠️ **IMPORTANT**: 
- Changez tous les mots de passe après la première connexion
- Utilisez des mots de passe forts en production
- Ne partagez pas les identifiants

## 🧪 Test des fonctionnalités

### Tester avec un Chef de Service
1. Connectez-vous avec `chef_service` / `chef123456`
2. Créez une demande de paiement
3. Vérifiez que vous ne pouvez pas valider les demandes

### Tester avec un DF
1. Connectez-vous avec `df` / `df123456`
2. Accédez aux demandes de paiement
3. Validez une demande en attente

### Tester avec un Comptable
1. Connectez-vous avec `comptable1` / `comptable123`
2. Enregistrez une recette
3. Validez la recette

### Tester avec un Opérateur de Saisie
1. Connectez-vous avec `operateur1` / `operateur123`
2. Saisissez un relevé bancaire
3. Ajoutez des mouvements bancaires

### Tester avec un Auditeur
1. Connectez-vous avec `auditeur` / `audit123456`
2. Consultez tous les modules
3. Créez un rapprochement bancaire
4. Validez le rapprochement

## 📝 Commandes utiles

### Créer les utilisateurs
```bash
python manage.py create_users_by_role
```

### Créer un utilisateur admin
```bash
python manage.py create_initial_user
```

### Créer un superutilisateur personnalisé
```bash
python manage.py createsuperuser
```

### Changer un mot de passe
```bash
python manage.py changepassword <username>
```

## 🔄 Réinitialiser les utilisateurs

Pour recréer tous les utilisateurs avec leurs mots de passe par défaut :
```bash
python manage.py create_users_by_role
```

Cette commande mettra à jour les mots de passe si les utilisateurs existent déjà.


