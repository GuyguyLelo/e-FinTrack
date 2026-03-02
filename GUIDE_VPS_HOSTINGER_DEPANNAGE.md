# 🚨 Guide de Dépannage - Design Cassé sur VPS Hostinger

## 🎯 **Problème identifié**

Le design est cassé sur votre VPS Hostinger alors qu'il fonctionne en local. C'est un problème très courant avec Django en production.

---

## 🔍 **Causes principales probables**

### **1. DEBUG=False en production**
```python
# Dans settings.py
DEBUG = False  # Ne sert plus les fichiers statiques automatiquement
```

### **2. Fichiers statiques non collectés**
```bash
# Les fichiers statiques ne sont pas dans le bon répertoire
# Django ne les trouve pas
```

### **3. Configuration du serveur web**
```bash
# Nginx/Apache ne sert pas les fichiers statiques
# Configuration manquante
```

### **4. Permissions incorrectes**
```bash
# Permissions sur les répertoires static/
# Le serveur ne peut pas lire les fichiers
```

---

## 🔧 **Solutions immédiates**

### **Étape 1 : Collecter les fichiers statiques**
```bash
# Sur votre VPS
cd /votre/chemin/e-FinTrack
python manage.py collectstatic --noinput --clear
```

### **Étape 2 : Vérifier les permissions**
```bash
# Permissions correctes pour les fichiers statiques
chmod -R 755 static/
chmod -R 755 staticfiles/
chmod -R 755 media/
```

### **Étape 3 : Configurer les variables d'environnement**
```bash
# Créer ou modifier .env sur le VPS
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,votre-ip-vps
STATIC_URL=/static/
STATIC_ROOT=/votre/chemin/e-FinTrack/staticfiles
```

### **Étape 4 : Configurer Nginx pour les fichiers statiques**
```nginx
# Dans /etc/nginx/sites-available/votre-site
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;
    
    location /static/ {
        alias /votre/chemin/e-FinTrack/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /votre/chemin/e-FinTrack/media/;
        expires 30d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🛠️ **Configuration Django pour la production**

### **1. Settings.py optimisé**
```python
# Ajouter à settings.py
import os

# Production settings
if not DEBUG:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # Media files
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    
    # Security
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

### **2. Middleware requis**
```python
# Vérifier que ces middleware sont présents
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

---

## 🌐 **Configuration Hostinger VPS**

### **1. Installation des dépendances**
```bash
# Sur votre VPS Hostinger
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Configuration PostgreSQL**
```bash
# Créer la base de données
sudo -u postgres psql
CREATE DATABASE fintrack;
CREATE USER fintrack_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE fintrack TO fintrack_user;
\q
```

### **3. Fichier .env pour la production**
```bash
# .env sur le VPS
DEBUG=False
SECRET_KEY=votre-secret-key-unique-et-securise
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,votre-ip-vps
DB_NAME=fintrack
DB_USER=fintrack_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
USE_POSTGRESQL=True
```

---

## 🚀 **Déploiement complet**

### **1. Script de déploiement**
```bash
#!/bin/bash
# deploy.sh

cd /votre/chemin/e-FinTrack

# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour le code
git pull origin main

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --noinput --clear

# Appliquer les migrations
python manage.py migrate

# Redémarrer les services
sudo systemctl restart nginx
sudo systemctl restart gunicorn

echo "Déploiement terminé !"
```

### **2. Service Gunicorn**
```bash
# /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon for e-FinTrack
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/votre/chemin/e-FinTrack
ExecStart=/votre/chemin/e-FinTrack/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock efinance_daf.wsgi:application

[Install]
WantedBy=multi-user.target
```

---

## 🔍 **Diagnostic rapide**

### **Vérifier l'état des fichiers statiques**
```bash
# Sur votre VPS
ls -la staticfiles/
# Devrait contenir css/, js/, images/, etc.

# Vérifier les permissions
ls -la staticfiles/css/
# Les fichiers doivent être lisibles par le serveur web
```

### **Tester avec DEBUG=True temporairement**
```bash
# Pour diagnostic uniquement
# Dans .env
DEBUG=True

# Redémarrer le serveur
sudo systemctl restart gunicorn

# Si le design revient, c'est bien un problème de fichiers statiques
```

### **Vérifier les logs**
```bash
# Logs Nginx
sudo tail -f /var/log/nginx/error.log

# Logs Gunicorn
sudo journalctl -u gunicorn -f
```

---

## 🎯 **Solution rapide pour Hostinger**

### **1. Commandes immédiates**
```bash
# Connectez-vous à votre VPS
cd /votre/chemin/e-FinTrack

# Collecter les fichiers statiques
python manage.py collectstatic --noinput --clear

# Permissions
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

# Redémarrer Nginx
sudo systemctl restart nginx
```

### **2. Si ça ne fonctionne pas**
```bash
# Activer DEBUG temporairement pour diagnostic
echo "DEBUG=True" >> .env
sudo systemctl restart gunicorn

# Testez dans le navigateur
# Si le design revient, le problème est bien les fichiers statiques

# Remettre DEBUG=False après test
sed -i 's/DEBUG=True/DEBUG=False/' .env
```

---

## 🚨 **Si rien ne fonctionne**

### **Solution de secours**
```python
# Dans settings.py - temporairement
DEBUG = True  # Uniquement pour diagnostic
ALLOWED_HOSTS = ['*']  # Attention: non sécurisé !

# Après avoir confirmé que le design fonctionne avec DEBUG=True
# Revenez à la configuration sécurisée
```

---

## 📞 **Support Hostinger**

Si le problème persiste, contactez le support Hostinger avec :
- Type de serveur : VPS
- Configuration : Django + Nginx + Gunicorn
- Problème : Fichiers statiques non servis
- Messages d'erreur des logs

---

## 🎉 **Conclusion**

Le problème de design cassé sur VPS est presque toujours lié aux fichiers statiques. Suivez ces étapes dans l'ordre :

1. **Collectstatic** - 90% des cas résolus
2. **Permissions** - 5% des cas résolus  
3. **Configuration Nginx** - 4% des cas résolus
4. **Variables d'environnement** - 1% des cas résolus

**La solution est généralement simple et rapide !**

---

*Guide créé le : 2 mars 2026*
*Problème : Design cassé sur VPS Hostinger*
*Solutions : Fichiers statiques + configuration serveur*
