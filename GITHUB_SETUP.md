# Instructions pour publier sur GitHub

## ✅ Étape 1 : Dépôt Git initialisé
Le dépôt Git local a été initialisé et le commit initial a été créé.

## 📋 Étape 2 : Créer le dépôt sur GitHub

1. **Allez sur GitHub** : https://github.com/new
2. **Connectez-vous** avec votre compte : `guyguylelo`
3. **Créez un nouveau dépôt** :
   - **Repository name** : `e-Finance_DAF` (ou un autre nom si vous préférez)
   - **Description** : "Système de gestion financière pour la DGRAD"
   - **Visibilité** : Public ou Private (selon votre choix)
   - **NE COCHEZ PAS** "Initialize this repository with a README" (le dépôt existe déjà)
   - **NE COCHEZ PAS** "Add .gitignore" (nous en avons déjà un)
   - **NE COCHEZ PAS** "Choose a license"
4. **Cliquez sur "Create repository"**

## 🔗 Étape 3 : Connecter le dépôt local à GitHub

Une fois le dépôt créé sur GitHub, exécutez ces commandes dans PowerShell :

```powershell
cd D:\Developpement\python\projets\e-Finance_DAF

# Ajouter le remote GitHub (remplacez USERNAME par votre nom d'utilisateur GitHub si différent)
git remote add origin https://github.com/guyguylelo/e-Finance_DAF.git

# Ou si vous utilisez SSH :
# git remote add origin git@github.com:guyguylelo/e-Finance_DAF.git

# Vérifier que le remote est bien ajouté
git remote -v
```

## 📤 Étape 4 : Pousser le code sur GitHub

```powershell
# Renommer la branche principale en 'main' (si nécessaire)
git branch -M main

# Pousser le code sur GitHub
git push -u origin main
```

Si GitHub vous demande vos identifiants :
- **Username** : `guyguylelo`
- **Password** : Utilisez un **Personal Access Token** (pas votre mot de passe)
  - Créez-en un ici : https://github.com/settings/tokens
  - Sélectionnez les scopes : `repo` (toutes les permissions du dépôt)

## ✅ Étape 5 : Vérification

Allez sur : https://github.com/guyguylelo/e-Finance_DAF

Vous devriez voir tous vos fichiers !

## 🔄 Pour les prochains commits

Après avoir fait des modifications :

```powershell
git add .
git commit -m "Description de vos modifications"
git push
```

## 📝 Notes importantes

- ✅ Le fichier `.gitignore` est configuré pour exclure :
  - La base de données SQLite (`db.sqlite3`)
  - Les fichiers de média (`/media`)
  - L'environnement virtuel (`venv/`)
  - Les fichiers statiques compilés (`/staticfiles`)
  - Les fichiers sensibles (`.env`, `local_settings.py`)

- ⚠️ **Sécurité** : Assurez-vous que `SECRET_KEY` n'est pas hardcodé dans `settings.py`
  - Le projet utilise `python-decouple` avec une valeur par défaut
  - En production, utilisez une variable d'environnement

- 📦 Les fichiers volumineux (`.accdb`, `.docx`) sont inclus mais vous pouvez les ajouter au `.gitignore` si nécessaire

## 🆘 En cas de problème

### Erreur : "remote origin already exists"
```powershell
git remote remove origin
git remote add origin https://github.com/guyguylelo/e-Finance_DAF.git
```

### Erreur : "authentication failed"
- Vérifiez que vous utilisez un Personal Access Token
- Créez-en un nouveau : https://github.com/settings/tokens

### Erreur : "repository not found"
- Vérifiez que le dépôt existe sur GitHub
- Vérifiez le nom d'utilisateur et le nom du dépôt dans l'URL

