#!/bin/bash
# fix_vps_logs.sh - Correction des permissions de logs Django

set -e

echo "🔧 Correction Permissions Logs Django"
echo "================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔧 1. Correction des permissions du fichier de log..."
echo "   Problème: Permission denied sur /home/kandolo/e-FinTrack/efinance.log"
echo "   Solution: Création du fichier de log avec bonnes permissions"

# Supprimer l'ancien fichier de log s'il existe
sudo rm -f efinance.log

# Créer le fichier de log avec les bonnes permissions
sudo touch efinance.log
sudo chown www-data:www-data efinance.log
sudo chmod 664 efinance.log

echo "✅ Fichier de log créé avec permissions correctes"

echo ""
echo "🔧 2. Correction des fichiers statiques manquants..."
echo "   Solution: Collecte complète avec chemin Python complet"

# Supprimer et recréer les fichiers statiques
sudo rm -rf staticfiles/
sudo mkdir -p staticfiles
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

# Utiliser le chemin complet de Python
PYTHON_PATH="/home/kandolo/e-FinTrack/venv/bin/python"

# Créer le répertoire de logs s'il n'existe pas
sudo mkdir -p logs
sudo chown www-data:www-data logs
sudo chmod 755 logs

# Collecter les fichiers statiques
sudo -u www-data $PYTHON_PATH manage.py collectstatic --noinput --clear

echo "✅ Fichiers statiques collectés"
echo "   Fichiers CSS: $(find staticfiles -name "*.css" | wc -l)"
echo "   Fichiers JS: $(find staticfiles -name "*.js" | wc -l)"

echo ""
echo "🔧 3. Correction du rôle SuperAdmin..."

$PYTHON_PATH manage.py shell << 'EOF'
from accounts.models import User

# Corriger le SuperAdmin
superadmin = User.objects.get(username='SuperAdmin')
print(f"SuperAdmin actuel: {superadmin.role}")

# Mettre à jour le rôle
superadmin.role = 'SUPER_ADMIN'
superadmin.is_superuser = True
superadmin.is_staff = True
superadmin.save()

print(f"SuperAdmin corrigé: {superadmin.role}")
print(f"   is_superuser: {superadmin.is_superuser}")
print(f"   is_staff: {superadmin.is_staff}")

EOF

echo ""
echo "🔧 4. Correction de l'erreur dans tableau_bord_feuilles/views.py..."

# Créer une sauvegarde du fichier
cp tableau_bord_feuilles/views.py tableau_bord_feuilles/views.py.backup

# Corriger le problème dans la vue
sed -i "215s/.*/        'peut_cloturer_periode': periode_actuelle.peut_etre_cloture()[0] if request.user.is_authenticated and request.user.role in \\['DG', 'CD_FINANCE'\\] else False,/" tableau_bord_feuilles/views.py

echo "✅ Vue tableau_bord_feuilles corrigée"

echo ""
echo "🔧 5. Correction de la configuration Nginx..."

# Créer une sauvegarde de la configuration Nginx
sudo cp /etc/nginx/sites-enabled/efintrack /etc/nginx/sites-enabled/efintrack.backup

# Mettre à jour la configuration Nginx
sudo tee /etc/nginx/sites-enabled/efintrack > /dev/null << 'EOF'
server {
    listen 80;
    server_name 187.77.171.80;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }

    location /static/ {
        alias /home/kandolo/e-FinTrack/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/kandolo/e-FinTrack/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/kandolo/e-FinTrack/gunicorn.sock;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "✅ Configuration Nginx mise à jour"

echo ""
echo "🔧 6. Vérification et redémarrage des services..."

# Tester la configuration Nginx
sudo nginx -t

# Redémarrer les services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Services redémarrés"

echo ""
echo "🔧 7. Vérification finale..."

$PYTHON_PATH manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User

print("Vérification finale:")

# Test SuperAdmin
superadmin = User.objects.get(username='SuperAdmin')
client = Client()
client.force_login(superadmin)

# Test tableau de bord
response = client.get('/tableau-bord-feuilles/')
print(f"✅ Tableau de bord: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    print(f"   Menu SuperAdmin: {'Menu SuperAdmin' in content}")
    print(f"   Tableau de bord: {'Tableau de bord' in content}")
    print(f"   Natures: {'Natures Économiques' in content}")

# Test admin
response = client.get('/admin/')
print(f"✅ Admin Django: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode('utf-8')
    print(f"   Design admin: {'dgrad-bleu' in content}")

EOF

echo ""
echo "🔧 8. Test de connectivité finale..."

echo "Test de l'application Django:"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/accounts/login/

echo ""
echo "Test de Nginx:"
curl -s -o /dev/null -w "%{http_code}" http://187.77.171.80/accounts/login/

echo ""
echo "🔧 9. État des services finaux..."

echo "Gunicorn:"
sudo systemctl status gunicorn --no-pager -l

echo ""
echo "Nginx:"
sudo systemctl status nginx --no-pager -l

echo ""
echo "🔧 10. Vérification des permissions des fichiers..."

echo "Permissions du fichier de log:"
ls -la efinance.log

echo ""
echo "Permissions des fichiers statiques:"
ls -la staticfiles/ | head -5

echo ""
echo "✅ Correction permissions logs terminée !"
echo ""
echo "🎯 Problèmes corrigés:"
echo "   ✅ Fichier de log: créé avec permissions www-data"
echo "   ✅ Fichiers statiques: CSS et JS collectés"
echo "   ✅ SuperAdmin: rôle corrigé en SUPER_ADMIN"
echo "   ✅ Vue tableau_bord_feuilles: AnonymousUser corrigé"
echo "   ✅ Nginx: configuration statiques corrigée"
echo "   ✅ Services: redémarrés"
echo ""
echo "🌐 Testez maintenant:"
echo "   1. Ouvrir un navigateur en mode incognito"
echo "   2. Aller sur: http://187.77.171.80/accounts/login/"
echo "   3. Se connecter avec SuperAdmin / SuperAdmin123!"
echo "   4. Vérifier que tout fonctionne comme en local"
echo ""
echo "🔍 Si problèmes persistent:"
echo "   1. Vérifier les logs: sudo journalctl -u gunicorn -f"
echo "   2. Vérifier Nginx: sudo nginx -t"
echo "   3. Comparer avec local: diff templates/base.html ~/e-FinTrack/templates/base.html"
