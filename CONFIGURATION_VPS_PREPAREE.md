# 🚀 Configuration VPS Hostinger - Fichiers Préparés

## 📋 **Ce que vous pouvez faire maintenant**

### **1. Fichier .env pour la production**
```bash
# À créer sur votre VPS dans /votre/chemin/e-FinTrack/.env
DEBUG=False
SECRET_KEY=django-insecure-change-me-avec-votre-propre-secret-key-tres-long-et-aleatoire-123456789
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com,votre-ip-vps
DB_NAME=fintrack
DB_USER=fintrack_user
DB_PASSWORD=votre-mot-de-passe-securise
DB_HOST=localhost
DB_PORT=5432
USE_POSTGRESQL=True

STATIC_URL=/static/
MEDIA_URL=/media/
```

### **2. Configuration Nginx**
```nginx
# /etc/nginx/sites-available/e-fintrack
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com votre-ip-vps;
    
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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **3. Service Gunicorn**
```ini
# /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon for e-FinTrack
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/votre/chemin/e-FinTrack
Environment="PATH=/votre/chemin/e-FinTrack/venv/bin"
ExecStart=/votre/chemin/e-FinTrack/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock efinance_daf.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## 🔧 **Scripts de déploiement**

### **1. Script d'installation rapide**
```bash
#!/bin/bash
# install.sh - À exécuter sur votre VPS

set -e

echo "🚀 Installation de e-FinTrack sur VPS Hostinger..."

# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib git

# Créer la base de données
echo "🗄️ Configuration PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE fintrack;"
sudo -u postgres psql -c "CREATE USER fintrack_user WITH PASSWORD 'votre_mot_de_passe_securise';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fintrack TO fintrack_user;"
sudo -u postgres psql -c "ALTER USER fintrack_user CREATEDB;"

# Créer le répertoire du projet
sudo mkdir -p /var/www/e-fintrack
sudo chown $USER:$USER /var/www/e-fintrack

# Aller dans le répertoire
cd /var/www/e-fintrack

# Cloner le projet (remplacez par votre méthode)
# git clone votre-repo.git .
# Ou copiez vos fichiers manuellement

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances Django
pip install django python-decoups psycopg2-binary gunicorn

echo "✅ Installation terminée !"
echo "📝 Prochaines étapes :"
echo "1. Copiez vos fichiers du projet dans /var/www/e-fintrack"
echo "2. Créez le fichier .env avec vos configurations"
echo "3. Exécutez le script deploy.sh"
```

### **2. Script de déploiement**
```bash
#!/bin/bash
# deploy.sh - À exécuter après avoir copié vos fichiers

set -e

echo "🚀 Déploiement de e-FinTrack..."

cd /var/www/e-fintrack

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

# Appliquer les migrations
echo "🗄️ Application des migrations..."
python manage.py migrate

# Créer le superuser
echo "👤 Création du superuser..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@votre-domaine.com', 'admin123')
    print('Superuser créé: admin / admin123')
else:
    print('Superuser existe déjà')
EOF

# Permissions
echo "🔐 Configuration des permissions..."
sudo chown -R www-data:www-data staticfiles/
sudo chown -R www-data:www-data media/
sudo chmod -R 755 staticfiles/
sudo chmod -R 755 media/

# Configurer Nginx
echo "🌐 Configuration Nginx..."
sudo ln -sf /etc/nginx/sites-available/e-fintrack /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Configurer Gunicorn
echo "⚙️ Configuration Gunicorn..."
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Redémarrer les services
echo "🔄 Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Déploiement terminé !"
echo "🌐 Votre site est disponible sur : http://votre-domaine.com"
echo "👤 Admin : admin / admin123"
```

---

## 🎯 **Étapes à suivre sur votre VPS**

### **1. Préparation du VPS**
```bash
# Connectez-vous à votre VPS Hostinger
ssh root@votre-ip-vps

# Téléchargez et exécutez le script d'installation
wget https://votre-domaine.com/install.sh  # ou copiez-collez le contenu
chmod +x install.sh
./install.sh
```

### **2. Transfert de vos fichiers**
```bash
# Méthode 1: SCP (depuis votre machine locale)
scp -r /chemin/local/e-FinTrack/* root@votre-ip-vps:/var/www/e-fintrack/

# Méthode 2: Git (si vous avez un repo)
cd /var/www/e-fintrack
git clone votre-repo.git .

# Méthode 3: SFTP avec FileZilla ou autre
```

### **3. Configuration finale**
```bash
# Sur le VPS
cd /var/www/e-fintrack

# Créer le fichier .env
nano .env
# Collez le contenu du fichier .env ci-dessus

# Rendez le script exécutable
chmod +x deploy.sh

# Exécutez le déploiement
./deploy.sh
```

---

## 🔍 **Vérification**

### **1. Vérifier les services**
```bash
# Sur votre VPS
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status postgresql
```

### **2. Vérifier les fichiers statiques**
```bash
ls -la /var/www/e-fintrack/staticfiles/
# Devrait contenir css/, js/, images/, etc.
```

### **3. Vérifier les logs**
```bash
# Logs Nginx
sudo tail -f /var/log/nginx/error.log

# Logs Gunicorn
sudo journalctl -u gunicorn -f
```

---

## 🚨 **Dépannage rapide**

### **Si le design est cassé**
```bash
# Sur le VPS
cd /var/www/e-fintrack
source venv/bin/activate
python manage.py collectstatic --noinput --clear
sudo systemctl restart nginx
```

### **Si vous avez une erreur 502**
```bash
# Vérifier Gunicorn
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50
```

### **Si vous avez une erreur 503**
```bash
# Vérifier si Django fonctionne
cd /var/www/e-fintrack
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
# Testez avec curl http://localhost:8000
```

---

## 🎉 **Configuration terminée**

Votre projet est maintenant configuré pour la production sur VPS Hostinger !

### **Points importants**
- ✅ Settings.py modifié pour la production
- ✅ Fichiers de configuration prêts
- ✅ Scripts d'installation et déploiement prêts
- ✅ Guide de dépannage complet

### **Prochaines étapes**
1. **Connectez-vous à votre VPS**
2. **Exécutez le script d'installation**
3. **Transférez vos fichiers**
4. **Configurez le fichier .env**
5. **Exécutez le script de déploiement**

**🎊 Votre site sera fonctionnel en quelques minutes !**

---

*Configuration préparée le : 2 mars 2026*
*VPS : Hostinger*
*Projet : e-FinTrack Django*
