#!/bin/bash

# Script de déploiement pour corriger l'admin Django sur VPS
echo "🔧 CORRECTION ADMIN DJANGO - VPS"
echo "=================================="

# 1. Activer l'environnement virtuel
echo ""
echo "🔧 Activation environnement virtuel..."
source venv/bin/activate

# 2. Vérifier la configuration actuelle
echo ""
echo "⚙️  Vérification configuration..."
python manage.py check --deploy | head -10

# 3. Nettoyer et recollecter les fichiers statiques
echo ""
echo "📁 Nettoyage et recollecte des fichiers statiques..."
rm -rf staticfiles/admin/
python manage.py collectstatic --noinput --clear

# 4. Vérifier les fichiers statiques
echo ""
echo "📂 Vérification des fichiers statiques..."
if [ -d "staticfiles/admin" ]; then
    echo "✅ Dossier admin/ trouvé dans staticfiles"
    echo "   Fichiers dans staticfiles/admin/css/:"
    ls staticfiles/admin/css/ | head -5
    echo "   Fichiers dans staticfiles/admin/js/:"
    ls staticfiles/admin/js/ | head -5
else
    echo "❌ Dossier admin/ manquant dans staticfiles"
fi

# 5. Ajuster les permissions
echo ""
echo "🔒 Ajustement des permissions..."
chmod -R 755 staticfiles/
chmod -R 755 media/

# 6. Vérifier la configuration des URLs
echo ""
echo "🌐 Vérification configuration URLs..."
python manage.py shell -c "
from django.urls import get_resolver
from django.conf import settings
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'DEBUG: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
"

# 7. Vérifier l'accès SuperAdmin
echo ""
echo "👤 Vérification accès SuperAdmin..."
python manage.py shell -c "
from accounts.models import User
superusers = User.objects.filter(role='SUPER_ADMIN')
print(f'SuperAdmin users: {superusers.count()}')
for u in superusers:
    print(f'  - {u.username} (admin_access: {u.peut_acceder_admin_django()})')
"

# 8. Instructions pour le test
echo ""
echo "🚀 INSTRUCTIONS DE TEST:"
echo "1. Démarrez le serveur:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "2. Testez l'accès admin:"
echo "   http://187.77.171.80:8000/admin/"
echo ""
echo "3. Connectez-vous avec:"
echo "   Username: SuperAdmin"
echo "   Password: [votre mot de passe]"
echo ""
echo "4. Si le design est cassé, vérifiez:"
echo "   - Les fichiers CSS/JS se chargent (F12 > Network)"
echo "   - Les erreurs 404 pour les fichiers statiques"
echo "   - La configuration du serveur web (nginx/apache)"

# 9. Diagnostic avancé
echo ""
echo "🔍 DIAGNOSTIC AVANCÉ:"
python fix_admin_django.py

echo ""
echo "✅ CORRECTION ADMIN DJANGO TERMINÉE"
echo "=================================="
