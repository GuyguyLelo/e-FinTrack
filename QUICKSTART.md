# 🚀 Guide de Démarrage Rapide

## Démarrage en 5 minutes avec Docker

```bash
# 1. Cloner le projet
git clone <repository-url>
cd e-Finance_DAF

# 2. Créer le fichier .env
cp .env.example .env

# 3. Lancer l'application
docker-compose up --build
```

Attendre quelques instants que l'application démarre, puis accéder à :
**http://localhost:8000**

### Identifiants par défaut
- Username: `admin`
- Password: `admin`

⚠️ **Changez le mot de passe immédiatement !**

## Premiers pas dans l'application

### 1. Se connecter
- Accéder à `http://localhost:8000`
- Utiliser les identifiants admin

### 2. Configurer les banques
- Menu latéral : **Banques** > **Ajouter une banque**
- Ajouter au moins une banque (ex: "Bank of Kinshasa")
- Créer des comptes bancaires (USD et CDF) pour chaque banque

### 3. Créer une demande de paiement (Chef de Service)
- Menu : **Demandes de paiement** > **Créer une demande**
- Remplir les informations et soumettre

### 4. Valider une demande (DF/DAF/DG)
- Accéder à la liste des demandes
- Cliquer sur **Valider** pour une demande en attente

### 5. Enregistrer une recette (Comptable/Opérateur)
- Menu : **Recettes** > **Enregistrer une recette**
- Sélectionner la banque et le compte
- Remplir les informations et valider

### 6. Saisir un relevé bancaire (Opérateur de Saisie)
- Menu : **Relevés bancaires** > **Saisir un relevé**
- Ajouter les mouvements bancaires
- Valider le relevé (Comptable/DF)

### 7. Rapprochement bancaire (Auditeur)
- Menu : **Rapprochements** > **Créer un rapprochement**
- Calculer le solde interne
- Valider le rapprochement

### 8. Consulter les rapports
- Menu : **Rapports consolidés**
- Filtrer par période pour voir les statistiques détaillées

## Structure des rôles

### DG (Directeur Général)
- Valide les dépenses importantes
- Consulte tous les rapports

### DAF (Directeur Administratif et Financier)
- Supervise les validations
- Approuve les relevés

### DF (Directeur Financier)
- Valide les paiements
- Valide les relevés bancaires

### Comptable
- Enregistre les recettes
- Valide les recettes et relevés

### Chef de Service
- Crée les demandes de paiement

### Auditeur
- Consulte tous les modules
- Valide les rapprochements

### Opérateur de Saisie
- Saisit les relevés bancaires
- Enregistre les recettes

## Commandes utiles

### Docker
```bash
# Démarrer
docker-compose up

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f web

# Accéder au shell Django
docker-compose exec web python manage.py shell
```

### Django (sans Docker)
```bash
# Créer un superutilisateur
python manage.py createsuperuser

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Charger les données de test
python manage.py loaddata accounts/fixtures/initial_data.json
python manage.py loaddata banques/fixtures/initial_data.json
```

## Support

Pour plus d'informations, consultez le fichier `README.md` et `INSTALLATION.md`.

