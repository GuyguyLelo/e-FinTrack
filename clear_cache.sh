#!/bin/bash
# clear_cache.sh - Script pour vider tous les caches et recharger

set -e

echo "🧹 Nettoyage complet du cache et rechargement"
echo "============================================"

cd /var/www/e-fintrack

# Activer l'environnement virtuel
source venv/bin/activate

echo "🗑️  Vider les sessions Django..."
python manage.py clearsessions

echo "📦 Recollecter les fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "🔄 Redémarrer les services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "📊 Vérifier l'état des services..."
echo "Gunicorn:"
sudo systemctl status gunicorn | grep Active
echo "Nginx:"
sudo systemctl status nginx | grep Active

echo ""
echo "🌐 Instructions pour le navigateur:"
echo "==================================="
echo "1. Ouvrez votre site dans le navigateur"
echo "2. Appuyez sur Ctrl + Shift + R (rechargement dur)"
echo "3. Ou Ctrl + F5"
echo "4. Ou videz le cache manuellement:"
echo "   - Chrome: Ctrl + Shift + Delete"
echo "   - Firefox: Ctrl + Shift + Delete"
echo "   - Safari: Cmd + Shift + R"

echo ""
echo "✅ Nettoyage terminé !"
echo "🎯 Testez maintenant vos modifications"
