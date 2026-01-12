# 📦 Guide d'Installation - e-Finance DAF

## Prérequis

- Python 3.11 ou supérieur
- PostgreSQL 15 ou supérieur
- Docker et Docker Compose (optionnel, recommandé)

## Installation avec Docker (Recommandé)

### 1. Cloner le projet
```bash
git clone <repository-url>
cd e-Finance_DAF
```

### 2. Créer le fichier .env
```bash
cp .env.example .env
# Modifier les valeurs dans .env si nécessaire
```

### 3. Lancer l'application
```bash
docker-compose up --build
```

L'application sera accessible sur `http://localhost:8000`

### Identifiants par défaut
- **Username** : `admin`
- **Password** : `admin`
- ⚠️ **Changez le mot de passe immédiatement après la première connexion !**

## Installation manuelle

### 1. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer la base de données PostgreSQL

Créer une base de données :
```sql
CREATE DATABASE efinance_daf;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE efinance_daf TO postgres;
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` :
```env
SECRET_KEY=votre-cle-secrete-ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=efinance_daf
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 5. Appliquer les migrations
```bash
python manage.py migrate
```

### 6. Charger les données initiales
```bash
python manage.py loaddata accounts/fixtures/initial_data.json
python manage.py loaddata banques/fixtures/initial_data.json
```

### 7. Créer l'utilisateur administrateur
```bash
python manage.py create_initial_user
```

Ou utiliser la commande Django standard :
```bash
python manage.py createsuperuser
```

### 8. Collecter les fichiers statiques
```bash
python manage.py collectstatic
```

### 9. Lancer le serveur de développement
```bash
python manage.py runserver
```

L'application sera accessible sur `http://localhost:8000`

## Vérification de l'installation

1. Accéder à `http://localhost:8000`
2. Se connecter avec les identifiants par défaut
3. Vérifier que le tableau de bord s'affiche correctement
4. Vérifier que les modules sont accessibles dans le menu latéral

## Problèmes courants

### Erreur de connexion à PostgreSQL
- Vérifier que PostgreSQL est démarré
- Vérifier les identifiants dans `.env`
- Vérifier que la base de données existe

### Erreur de migration
```bash
python manage.py migrate --run-syncdb
```

### Erreur de fichiers statiques
```bash
python manage.py collectstatic --noinput
```

## Production

Pour la production :
1. Définir `DEBUG=False` dans `.env`
2. Configurer un vrai `SECRET_KEY`
3. Configurer `ALLOWED_HOSTS` avec votre domaine
4. Utiliser un serveur WSGI (gunicorn, uWSGI)
5. Configurer un serveur web (Nginx, Apache)
6. Utiliser HTTPS
7. Configurer la sauvegarde de la base de données

## Support

Pour toute question, contactez l'équipe de développement.

