# 🚀 Guide rapide : Publier sur GitHub

## Option 1 : Script automatique (Recommandé)

1. **Créez d'abord le dépôt sur GitHub** :
   - Allez sur : https://github.com/new
   - Nom : `e-Finance_DAF`
   - Ne cochez **aucune option**
   - Cliquez sur "Create repository"

2. **Exécutez le script** :
   ```powershell
   cd D:\Developpement\python\projets\e-Finance_DAF
   .\push_to_github.ps1
   ```

3. **Suivez les instructions** :
   - Le script vous guidera pas à pas
   - Quand GitHub demande vos identifiants :
     - **Username** : `guyguylelo`
     - **Password** : Votre **Personal Access Token** (pas votre mot de passe)

## Option 2 : Commandes manuelles

Si vous préférez faire manuellement :

```powershell
cd D:\Developpement\python\projets\e-Finance_DAF

# 1. Ajouter le remote GitHub
git remote add origin https://github.com/guyguylelo/e-Finance_DAF.git

# 2. Renommer la branche en 'main'
git branch -M main

# 3. Pousser le code
git push -u origin main
```

## 🔑 Personal Access Token

Si vous n'avez pas de token :

1. Allez sur : https://github.com/settings/tokens
2. Cliquez sur "Generate new token" → "Generate new token (classic)"
3. Donnez un nom : "e-Finance DAF"
4. Sélectionnez la scope : **`repo`** (toutes les permissions)
5. Cliquez sur "Generate token"
6. **Copiez le token** (vous ne le reverrez plus !)
7. Utilisez ce token comme mot de passe lors du push

## ✅ Vérification

Après le push, vérifiez que tout est bien en ligne :
- https://github.com/guyguylelo/e-Finance_DAF

## 📝 Prochains commits

Pour les prochaines modifications :

```powershell
git add .
git commit -m "Description des modifications"
git push
```

---

**Note** : Le script `push_to_github.ps1` gère automatiquement :
- ✅ Vérification du dépôt Git
- ✅ Ajout du remote (avec remplacement si nécessaire)
- ✅ Renommage de la branche en 'main'
- ✅ Instructions pour l'authentification
- ✅ Push avec gestion d'erreurs

