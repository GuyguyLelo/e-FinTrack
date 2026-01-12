# 🚀 Guide de Configuration - e-Finance DAF

## ✅ Étape 1 : Environnement virtuel créé

L'environnement virtuel Python a été créé dans `venv/`

## ✅ Étape 2 : Dépendances installées

Toutes les dépendances ont été installées avec succès :
- Django 5.0.4
- PostgreSQL (psycopg2-binary)
- Bootstrap 5 (crispy-forms)
- Et toutes les autres dépendances

## ✅ Étape 3 : Migrations créées

Les migrations ont été créées pour toutes les applications :
- ✅ accounts
- ✅ banques
- ✅ demandes
- ✅ recettes
- ✅ releves
- ✅ rapprochements

## 📋 Prochaines étapes

### 1. Configurer PostgreSQL

Assurez-vous que PostgreSQL est installé et en cours d'exécution.

**Option A : Utiliser PostgreSQL local**
1. Créer une base de données :
```sql
CREATE DATABASE efinance_daf;
```

2. Vérifier/modifier le fichier `.env` :
```env
DB_NAME=efinance_daf
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
```

**Option B : Utiliser Docker (Recommandé)**
```bash
docker-compose up -d db
```

### 2. Appliquer les migrations

```bash
.\venv\Scripts\Activate.ps1
python manage.py migrate
```

### 3. Charger les données initiales

```bash
python manage.py loaddata accounts/fixtures/initial_data.json
python manage.py loaddata banques/fixtures/initial_data.json
```

### 4. Créer l'utilisateur administrateur

```bash
python manage.py create_initial_user
```

Ou utiliser la commande Django standard :
```bash
python manage.py createsuperuser
```

### 5. Collecter les fichiers statiques

```bash
python manage.py collectstatic
```

### 6. Lancer le serveur de développement

```bash
python manage.py runserver
```

L'application sera accessible sur : **http://localhost:8000**

## 🔑 Identifiants par défaut

Après avoir exécuté `create_initial_user` :
- **Username** : `admin`
- **Password** : `admin`
- ⚠️ **Changez le mot de passe immédiatement !**

## 📝 Commandes utiles

### Activer l'environnement virtuel
```bash
.\venv\Scripts\Activate.ps1
```

### Créer de nouvelles migrations
```bash
python manage.py makemigrations
```

### Appliquer les migrations
```bash
python manage.py migrate
```

### Accéder au shell Django
```bash
python manage.py shell
```

### Accéder à l'admin Django
```bash
# Naviguer vers http://localhost:8000/admin
```

## 🐛 Dépannage

### Erreur de connexion à PostgreSQL
- Vérifier que PostgreSQL est démarré
- Vérifier les identifiants dans `.env`
- Vérifier que la base de données existe

### Erreur "No module named 'decouple'"
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Erreur de migration
```bash
python manage.py migrate --run-syncdb
```

## 🎉 Prêt !

Une fois toutes ces étapes terminées, votre application e-Finance DAF sera prête à être utilisée !

