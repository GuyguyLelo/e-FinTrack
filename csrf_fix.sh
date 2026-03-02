#!/bin/bash
# csrf_fix.sh - Solution définitive pour CSRF multi-machines

set -e

echo "🚨 Solution Définitive CSRF Multi-Machines"
echo "======================================"

cd /var/www/e-fintrack
source venv/bin/activate

echo "🗑️  1. Vider toutes les sessions existantes..."
python manage.py shell << EOF
from django.contrib.sessions.models import Session
count = Session.objects.all().delete()[0]
print(f"✅ {count} sessions supprimées")
EOF

echo ""
echo "📦 2. Recollecter les fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo ""
echo "🔄 3. Redémarrer tous les services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl restart postgresql

echo ""
echo "🔍 4. Vérifier la configuration CSRF..."
python manage.py shell << EOF
from django.conf import settings
print("📊 Configuration CSRF:")
print(f"DEBUG: {settings.DEBUG}")
print(f"CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'Non défini')}")
print(f"SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', 'Non défini')}")
print(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'Non défini')}")
print(f"SESSION_COOKIE_DOMAIN: {getattr(settings, 'SESSION_COOKIE_DOMAIN', 'Non défini')}")
print(f"SESSION_COOKIE_AGE: {getattr(settings, 'SESSION_COOKIE_AGE', 'Non défini')}")
EOF

echo ""
echo "🌐 5. Test de connexion depuis différentes machines..."
echo "==================================================="
echo "📝 Instructions de test:"
echo "1. Machine A: Ouvrir http://187.77.171.80:8000/accounts/login/"
echo "2. Se connecter avec AdminDaf / AdminDaf123!"
echo "3. Fermer le navigateur"
echo "4. Machine B: Ouvrir http://187.77.171.80:8000/accounts/login/"
echo "5. Se connecter avec DirDaf / DirDaf123!"
echo "6. Les deux machines doivent pouvoir se connecter"

echo ""
echo "🔧 6. Si problème persiste, solution de dernier recours..."
echo "====================================================="
echo "Ajouter dans settings.py (temporairement pour test):"
echo "MIDDLEWARE = ["
echo "    # 'django.middleware.csrf.CsrfViewMiddleware',  # Commenter"
echo "    'django.middleware.security.SecurityMiddleware',"
echo "    # ... autres middlewares"
echo "]"

echo ""
echo "🎯 7. Configuration Nginx pour headers CSRF..."
echo "=============================================="
echo "Ajouter dans /etc/nginx/sites-available/e-fintrack:"
echo "location / {"
echo "    proxy_pass http://127.0.0.1:8000;"
echo "    proxy_set_header Host \$host;"
echo "    proxy_set_header X-Real-IP \$remote_addr;"
echo "    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
echo "    proxy_set_header X-Forwarded-Proto \$scheme;"
echo "    proxy_set_header X-CSRFToken \$csrf_token;"
echo "    proxy_pass_request_headers on;"
echo "}"

echo ""
echo "✅ Configuration CSRF terminée !"
echo "🎊 Testez maintenant depuis différentes machines"
