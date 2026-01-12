# 🏦 e-Finance DAF - Système de Gestion Financière DGRAD

Application web complète de gestion financière intégrée pour la **Direction Générale des Recettes Administratives, Judiciaires, Domaniales et de Participations (DGRAD)**.

## 📋 Fonctionnalités

### ✅ Modules principaux

- **🏦 Gestion Multi-Banques** : Gestion de plusieurs banques et comptes bancaires (USD et CDF)
- **💸 Demandes de Paiement** : Création, validation hiérarchique et suivi des dépenses
- **💰 Gestion des Recettes** : Enregistrement et validation des recettes encaissées
- **📊 Relevés Bancaires** : Saisie et validation des relevés bancaires multi-banques
- **🔄 Rapprochement Bancaire** : Rapprochement automatique par compte et période
- **📈 Reporting Consolidé** : Tableaux de bord et rapports consolidés multi-banques
- **🔐 Gestion des Rôles** : 7 rôles avec permissions personnalisées

### 👥 Rôles et Permissions

| Rôle | Description | Permissions |
|------|-------------|-------------|
| **DG** | Directeur Général | Validation des dépenses importantes, consultation complète |
| **DAF** | Directeur Administratif et Financier | Supervise validations, approuve relevés |
| **DF** | Directeur Financier | Vérifie disponibilité budgétaire, valide paiements |
| **Comptable** | Comptable | Exécute paiements, enregistre recettes, valide relevés |
| **Chef de Service** | Responsable d'unité | Crée et suit les demandes de paiement |
| **Auditeur** | Audit interne | Consulte tous les modules, valide rapprochements |
| **Opérateur de Saisie** | Agent bancaire | Saisit relevés, encode recettes/dépenses |

## 🛠️ Stack Technologique

- **Backend** : Django 5.0
- **Base de données** : PostgreSQL 15
- **Frontend** : Bootstrap 5 + Chart.js
- **Authentification** : Django Auth avec rôles personnalisés
- **Déploiement** : Docker + Docker Compose

## 🚀 Installation

### Prérequis

- Python 3.11+
- PostgreSQL 15
- Docker et Docker Compose (optionnel)

### Installation avec Docker (Recommandé)

1. **Cloner le projet**
```bash
git clone <repository-url>
cd e-Finance_DAF
```

2. **Créer le fichier .env**
```bash
cp .env.example .env
# Modifier les valeurs dans .env si nécessaire
```

3. **Lancer avec Docker Compose**
```bash
docker-compose up --build
```

L'application sera accessible sur `http://localhost:8000`

### Installation manuelle

1. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer la base de données**
- Créer une base PostgreSQL nommée `efinance_daf`
- Modifier les paramètres dans `efinance_daf/settings.py` ou `.env`

4. **Appliquer les migrations**
```bash
python manage.py migrate
```

5. **Charger les données initiales**
```bash
python manage.py loaddata accounts/fixtures/initial_data.json
python manage.py loaddata banques/fixtures/initial_data.json
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Collecter les fichiers statiques**
```bash
python manage.py collectstatic
```

8. **Lancer le serveur**
```bash
python manage.py runserver
```

## 📁 Structure du Projet

```
e-Finance_DAF/
├── accounts/          # Gestion utilisateurs et rôles
├── banques/           # Gestion banques et comptes
├── demandes/          # Demandes de paiement
├── recettes/          # Gestion des recettes
├── releves/           # Relevés bancaires
├── rapprochements/    # Rapprochement bancaire
├── rapports/          # Rapports et tableaux de bord
├── efinance_daf/      # Configuration Django
├── templates/         # Templates HTML
├── static/            # Fichiers statiques
├── media/             # Fichiers uploadés
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🔑 Accès par défaut

Après chargement des fixtures :
- **Username** : `admin`
- **Password** : `admin` (à changer immédiatement)

## 📊 Utilisation

### 1. Gestion des Banques

- Accéder à **Banques** > **Ajouter une banque**
- Créer les comptes bancaires (USD et CDF) pour chaque banque

### 2. Demandes de Paiement

- Les **Chefs de Service** créent des demandes
- Validation hiérarchique : DF → DAF → DG
- Les demandes validées passent au statut "Payée"

### 3. Recettes

- **Opérateurs de Saisie** ou **Comptables** enregistrent les recettes
- Validation par le **Comptable**
- Mise à jour automatique des soldes bancaires

### 4. Relevés Bancaires

- Les **Opérateurs de Saisie** saisissent les relevés reçus
- Ajout des mouvements bancaires individuels
- Validation par **Comptable** ou **DF**

### 5. Rapprochement Bancaire

- Création d'un rapprochement pour un compte et une période
- Calcul automatique du solde interne
- Comparaison avec le solde bancaire
- Validation finale par **Auditeur**

### 6. Rapports

- **Tableau de bord** : Vue d'ensemble consolidée
- **Rapports consolidés** : Détails par période et banque
- Graphiques interactifs (Chart.js)

## 🔒 Sécurité

- Authentification sécurisée avec Django Auth
- Permissions basées sur les rôles
- Validation des fichiers uploadés
- Protection CSRF activée
- Sessions sécurisées

## 🧪 Tests

```bash
python manage.py test
```

## 📝 Migrations

Créer une migration :
```bash
python manage.py makemigrations
```

Appliquer les migrations :
```bash
python manage.py migrate
```

## 🐳 Docker

### Commandes utiles

```bash
# Démarrer les services
docker-compose up

# Démarrer en arrière-plan
docker-compose up -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f web

# Accéder au shell Django
docker-compose exec web python manage.py shell
```

## 📈 Évolutions prévues

- [ ] Connexion bancaire automatisée (API)
- [ ] Export Excel/PDF des rapports
- [ ] Intégration Power BI
- [ ] API REST complète
- [ ] Notifications en temps réel
- [ ] Multi-tenant (multi-organisations)

## 📄 Licence

Projet développé pour la DGRAD.

## 👨‍💻 Support

Pour toute question ou problème, contacter l'équipe de développement.

---

**Développé avec ❤️ pour la DGRAD**

