# 🚀 Scripts de Déploiement VPS - Correction des Redirections par Rôle

## 📋 **Scripts créés pour votre VPS**

J'ai créé deux scripts que vous pouvez pusher et exécuter sur votre VPS :

---

## 🔧 **1. Script de correction local**
```bash
# fix_redirections_roles.sh
# À exécuter en local pour créer les fichiers
chmod +x fix_redirections_roles.sh
./fix_redirections_roles.sh
```

---

## 🚀 **2. Script de déploiement VPS**
```bash
# deploy_vps_redirections.sh
# À exécuter sur votre VPS après le push
chmod +x deploy_vps_redirections.sh
./deploy_vps_redirections.sh
```

---

## 🎯 **Configuration des redirections**

### **Rôles et accès configurés**

| Utilisateur | Menu | Redirection | Accès |
|------------|-------|-------------|-------|
| **AdminDaf** | Uniquement "Natures Économiques" | `/` → `/demandes/natures/` | Natures uniquement |
| **SuperAdmin** | Tableau de bord, Dépenses, Recettes, Admin Django | `/demandes/natures/` → `/tableau-bord-feuilles/` | Tout sauf natures |
| **DirDaf, DivDaf** | Tableau de bord, Clôtures, Natures, Dépenses, Recettes | `/` → `/tableau-bord-feuilles/` | Tableau de bord + Clôtures |
| **OpsDaf** | Comme avant | `/` → `/tableau-bord-feuilles/` | Accès standard |

---

## 🔄 **Processus de déploiement**

### **1. En local**
```bash
# Créer les fichiers corrigés
cd ~/e-FinTrack
chmod +x fix_redirections_roles.sh
./fix_redirections_roles.sh

# Push vers votre repository
git add .
git commit -m "Correction des redirections par rôle"
git push origin main
```

### **2. Sur votre VPS**
```bash
# Pull des modifications
cd ~/e-FinTrack
git pull origin main

# Exécuter le script de déploiement
chmod +x deploy_vps_redirections.sh
./deploy_vps_redirections.sh
```

---

## 🔍 **Ce que font les scripts**

### **Script local (`fix_redirections_roles.sh`)**
- ✅ Crée le template `base_roles.html` avec menus par rôle
- ✅ Configure les redirections JavaScript avec `sessionStorage`
- ✅ Teste les redirections en local
- ✅ Sauvegarde l'ancien template

### **Script VPS (`deploy_vps_redirections.sh`)**
- ✅ Crée le template `base_vps.html` pour production
- ✅ Remplace `base.html` par la version corrigée
- ✅ Redémarre les services Gunicorn et Nginx
- ✅ Vérifie le statut des services

---

## 🌐 **Test après déploiement**

### **URL de test sur votre VPS**
```
http://187.77.171.80/accounts/login/
```

### **Tests à effectuer**

#### **1. AdminDaf**
```
Login: AdminDaf / AdminDaf123!
Résultat attendu:
- ✅ Redirection vers /demandes/natures/
- ✅ Menu: Uniquement "Natures Économiques"
- ✅ Pas de boucle de redirection
```

#### **2. SuperAdmin**
```
Login: SuperAdmin / SuperAdmin123!
Résultat attendu:
- ✅ Redirection vers /tableau-bord-feuilles/
- ✅ Menu: Tableau de bord, Dépenses, Recettes, Admin Django
- ✅ PAS de lien vers les natures
- ✅ Si tente d'accéder aux natures → redirection tableau de bord
```

#### **3. DirDaf / DivDaf**
```
Login: [DirDaf ou DivDaf] / [mot de passe]
Résultat attendu:
- ✅ Redirection vers /tableau-bord-feuilles/
- ✅ Menu: Tableau de bord, Clôtures, Natures, Dépenses, Recettes
```

#### **4. OpsDaf**
```
Login: [OpsDaf] / [mot de passe]
Résultat attendu:
- ✅ Redirection vers /tableau-bord-feuilles/
- ✅ Menu: Comme avant (accès standard)
```

---

## 🔧 **Anti-boucles de redirection**

### **Mécanisme sessionStorage**
```javascript
// Évite les boucles infinies
var redirected = sessionStorage.getItem('redirected');
if (redirected) {
    console.log("Déjà redirigé dans cette session");
    return;
}

// Marquer la redirection
sessionStorage.setItem('redirected', 'true');

// Réinitialiser après 5 secondes
setTimeout(function() {
    sessionStorage.removeItem('redirected');
}, 5000);
```

---

## 🚨 **En cas de problème sur VPS**

### **Vérifier les logs**
```bash
# Logs Gunicorn
sudo journalctl -u gunicorn -f

# Logs Nginx
sudo journalctl -u nginx -f

# Logs Django
python manage.py runserver --settings=efinance_daf.settings
```

### **Vérifier les services**
```bash
# Statut des services
sudo systemctl status gunicorn
sudo systemctl status nginx

# Redémarrer si nécessaire
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### **Vérifier les fichiers**
```bash
# Vérifier que le template est bien déployé
ls -la templates/base.html*
cat templates/base.html | grep -A 5 "Redirection check"
```

---

## 🎊 **Résultat final**

### **Plus de boucles de redirection**
- ✅ **sessionStorage** empêche les boucles infinies
- ✅ **Redirections uniques** par rôle
- ✅ **Menus adaptés** selon les permissions

### **Accès par rôle correct**
- ✅ **AdminDaf** : Uniquement les natures
- ✅ **SuperAdmin** : Tout sauf les natures
- ✅ **DirDaf/DivDaf** : Tableau de bord + Clôtures
- ✅ **OpsDaf** : Accès standard

---

## 📞 **Instructions finales**

1. **En local** : Exécutez `./fix_redirections_roles.sh`
2. **Push** : `git add . && git commit -m "Correction redirections" && git push`
3. **Sur VPS** : `git pull && ./deploy_vps_redirections.sh`
4. **Test** : Visitez `http://187.77.171.80/accounts/login/`

**🎊 Vos redirections seront corrigées et les boucles éliminées !**
