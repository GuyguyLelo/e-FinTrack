# 🗄️ Migration SQLite vers PostgreSQL

## 📋 Configuration PostgreSQL

### 🔧 Informations de connexion
- **Base de données** : e_FinTrack_db
- **Utilisateur** : postgres
- **Mot de passe** : mohkandolo

---

## 🚀 Processus de Migration

### 1. **Installation des dépendances**
```bash
pip install psycopg2-binary
```

### 2. **Configuration Django settings**
Modification du fichier `settings.py` pour utiliser PostgreSQL

### 3. **Sauvegarde des données**
Export des données depuis SQLite

### 4. **Création de la base PostgreSQL**
Configuration et création de la base

### 5. **Migration des données**
Import des données vers PostgreSQL

---

## 🔧 Étapes détaillées

### Étape 1: Installation de psycopg2
```bash
source venv/bin/activate
pip install psycopg2-binary
```

### Étape 2: Configuration settings.py
Remplacer la configuration DATABASE par PostgreSQL

### Étape 3: Dump des données SQLite
```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json
```

### Étape 4: Création base PostgreSQL
```sql
CREATE DATABASE e_FinTrack_db;
```

### Étape 5: Migration et import
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata data.json
```

---

## ✅ Vérification post-migration

### Tests à effectuer
- Connexion des utilisateurs
- Accès aux données
- Fonctionnalités CRUD
- Permissions et rôles

---

## 🔄 Rollback (si nécessaire)

### Commande pour revenir à SQLite
```bash
# Modifier settings.py vers SQLite
python manage.py migrate
# Les données sont toujours dans data.json
```
