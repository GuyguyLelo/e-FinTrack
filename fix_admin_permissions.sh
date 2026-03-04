#!/bin/bash

# Script pour corriger les permissions et configuration admin sur VPS
echo "🔧 CORRECTION PERMISSIONS ADMIN DJANGO - VPS"
echo "============================================="

# 1. Corriger les permissions avec sudo
echo ""
echo "🔒 Correction des permissions fichiers statiques..."
sudo chown -R kandolo:kandolo staticfiles/
sudo chmod -R 755 staticfiles/
echo "✅ Permissions staticfiles corrigées"

# 2. Recollecter les fichiers statiques proprement
echo ""
echo "📁 Recollecte des fichiers statiques..."
source venv/bin/activate
python manage.py collectstatic --noinput --clear
echo "✅ Fichiers statiques recollectés"

# 3. Vérifier la configuration nginx
echo ""
echo "🌐 Vérification configuration nginx..."
if [ -f "/etc/nginx/sites-available/e-fintrack" ]; then
    echo "✅ Configuration nginx trouvée"
    echo "   Vérification que les fichiers statiques sont servis..."
    grep -A 5 "location /static/" /etc/nginx/sites-available/e-fintrack || echo "⚠️  Configuration static manquante"
else
    echo "⚠️  Configuration nginx non trouvée dans /etc/nginx/sites-available/e-fintrack"
    echo "   Fichiers de configuration possibles:"
    find /etc/nginx -name "*.conf" | grep -E "(e-fin|default)" | head -5
fi

# 4. Tester la configuration nginx
echo ""
echo "🧪 Test configuration nginx..."
sudo nginx -t && echo "✅ Configuration nginx valide" || echo "❌ Configuration nginx invalide"

# 5. Redémarrer les services
echo ""
echo "🔄 Redémarrage des services..."
sudo systemctl reload nginx
sudo systemctl restart gunicorn
echo "✅ Services redémarrés"

# 6. Vérifier que les fichiers sont accessibles via nginx
echo ""
echo "🌍 Test accès fichiers statiques..."
curl -I http://localhost/static/admin/css/base.css | head -1 || echo "❌ Fichiers statiques non accessibles"

# 7. Diagnostic rapide
echo ""
echo "🔍 Diagnostic rapide:"
echo "   User: $(whoami)"
echo "   Django DEBUG: $(source venv/bin/activate && python -c \"import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings'); import django; django.setup(); from django.conf import settings; print(settings.DEBUG)\")"
echo "   STATIC_ROOT: $(source venv/bin/activate && python -c \"import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings'); import django; django.setup(); from django.conf import settings; print(settings.STATIC_ROOT)\")"

echo ""
echo "🚀 INSTRUCTIONS FINALES:"
echo "1. Vérifiez l'admin: http://187.77.171.80:8000/admin/"
echo "2. Si le design est toujours cassé:"
echo "   - Vérifiez les erreurs 404 dans la console du navigateur (F12)"
echo "   - Vérifiez que nginx sert bien /static/"
echo "   - Redémarrez nginx: sudo systemctl restart nginx"

echo ""
echo "✅ CORRECTION TERMINÉE"
