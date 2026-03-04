#!/bin/bash
# debug_vps_complete.sh - Diagnostic complet VPS pour identifier les problèmes

set -e

echo "🔍 Diagnostic Complet VPS - Identification des Problèmes"
echo "=================================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. État des services..."
echo "Gunicorn:"
sudo systemctl status gunicorn --no-pager -l
echo ""
echo "Nginx:"
sudo systemctl status nginx --no-pager -l

echo ""
echo "🔍 2. Configuration Django..."
python manage.py shell << 'EOF'
import os
from django.conf import settings

print("Configuration Django:")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"   STATIC_URL: {settings.STATIC_URL}")
print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")
print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"   TEMPLATES DIRS: {settings.TEMPLATES[0]['DIRS']}")
print(f"   DATABASE: {settings.DATABASES['default']['ENGINE']}")
print(f"   DATABASE_NAME: {settings.DATABASES['default']['NAME']}")

# Vérifier les applications installées
print(f"\nApplications installées: {len(settings.INSTALLED_APPS)}")
for app in settings.INSTALLED_APPS:
    if 'admin' in app or 'static' in app:
        print(f"   - {app}")

EOF

echo ""
echo "🔍 3. État des fichiers statiques..."
if [ -d "staticfiles" ]; then
    echo "✅ Répertoire staticfiles existe"
    echo "   Taille: $(du -sh staticfiles | cut -f1)"
    echo "   Permissions: $(ls -la staticfiles/ | head -1)"
    echo "   Propriétaire: $(stat -c '%U:%G' staticfiles/)"
    echo "   Fichiers CSS: $(find staticfiles -name "*.css" | wc -l)"
    echo "   Fichiers JS: $(find staticfiles -name "*.js" | wc -l)"
    echo "   Fichiers Bootstrap: $(find staticfiles -name "*bootstrap*" | wc -l)"
    
    echo ""
    echo "   Contenu de staticfiles/:"
    ls -la staticfiles/ | head -10
else
    echo "❌ Répertoire staticfiles n'existe pas"
fi

echo ""
echo "🔍 4. État des templates..."
if [ -f "templates/base.html" ]; then
    echo "✅ Template base.html existe"
    echo "   Taille: $(wc -l templates/base.html | cut -d' ' -f1)"
    echo "   Dernière modification: $(stat -c '%y' templates/base.html)"
    
    # Vérifier le contenu
    echo "   Sections trouvées:"
    grep -o "Menu [A-Za-z]*" templates/base.html | sort | uniq
else
    echo "❌ Template base.html n'existe pas"
fi

if [ -f "templates/admin/base_site_custom.html" ]; then
    echo "✅ Template admin personnalisé existe"
else
    echo "❌ Template admin personnalisé n'existe pas"
fi

echo ""
echo "🔍 5. État de la base de données..."
python manage.py shell << 'EOF'
from accounts.models import User
from django.contrib.sessions.models import Session

print("Base de données:")
print(f"   Total utilisateurs: {User.objects.count()}")

for user in User.objects.all():
    print(f"   - {user.username} ({user.role}) - Actif: {user.is_active} - Staff: {user.is_staff} - Superuser: {user.is_superuser}")

print(f"\n   Sessions actives: {Session.objects.count()}")

# Vérifier les permissions des utilisateurs
superadmin = User.objects.filter(username='SuperAdmin').first()
if superadmin:
    print(f"\n   SuperAdmin permissions:")
    print(f"     peut_voir_tableau_bord: {superadmin.peut_voir_tableau_bord()}")
    print(f"     peut_ajouter_nature_economique: {superadmin.peut_ajouter_nature_economique()}")
    print(f"     peut_acceder_admin_django: {superadmin.peut_acceder_admin_django()}")
    print(f"     peut_ajouter_recette_depense: {superadmin.peut_ajouter_recette_depense()}")
    print(f"     peut_generer_etats: {superadmin.peut_generer_etats()}")
else:
    print("❌ SuperAdmin non trouvé")

EOF

echo ""
echo "🔍 6. Test des URLs avec Client Django..."
python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User
from django.urls import reverse

print("Tests des URLs:")

try:
    # Test SuperAdmin
    superadmin = User.objects.get(username='SuperAdmin')
    client = Client()
    client.force_login(superadmin)
    
    # Test tableau de bord
    try:
        url = reverse('tableau_bord_feuilles:tableau_bord_feuilles')
        response = client.get(url)
        print(f"✅ Tableau de bord: {response.status_code} - {url}")
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            print(f"     Menu SuperAdmin: {'Menu SuperAdmin' in content}")
            print(f"     Tableau de bord: {'Tableau de bord' in content}")
            print(f"     Natures: {'Natures Économiques' in content}")
    except Exception as e:
        print(f"❌ Tableau de bord: {e}")
    
    # Test admin
    response = client.get('/admin/')
    print(f"✅ Admin Django: {response.status_code}")
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        print(f"     Design admin: {'dgrad-bleu' in content}")
    
    # Test natures
    try:
        url = reverse('demandes:nature_liste')
        response = client.get(url)
        print(f"✅ Natures: {response.status_code} - {url}")
    except Exception as e:
        print(f"❌ Natures: {e}")
        
except Exception as e:
    print(f"❌ Erreur générale: {e}")

EOF

echo ""
echo "🔍 7. Configuration Nginx..."
echo "Fichier de configuration Nginx:"
sudo nginx -T | grep -A 20 -B 5 "server_name.*187.77.171.80"

echo ""
echo "🔍 8. Test de connectivité..."
echo "Test de l'application Django:"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/accounts/login/ || echo "❌ Impossible de se connecter à Django"

echo ""
echo "Test de Nginx:"
curl -s -o /dev/null -w "%{http_code}" http://187.77.171.80/accounts/login/ || echo "❌ Impossible de se connecter via Nginx"

echo ""
echo "🔍 9. Logs récents..."
echo "Logs Gunicorn (dernières 10 lignes):"
sudo journalctl -u gunicorn --no-pager -n 10

echo ""
echo "Logs Nginx (dernières 10 lignes):"
sudo journalctl -u nginx --no-pager -n 10

echo ""
echo "🔍 10. Comparaison avec local..."
echo "Fichiers modifiés récemment:"
find . -name "*.py" -o -name "*.html" -o -name "*.css" | xargs ls -lt | head -10

echo ""
echo "Différences potentielles:"
echo "   - Vérifier si les migrations sont appliquées: python manage.py showmigrations"
echo "   - Vérifier si les URLs sont correctes: python manage.py show_urls"
echo "   - Vérifier la configuration: python manage.py check --deploy"

echo ""
echo "🔧 11. Suggestions de correction..."
echo "Basé sur le diagnostic, voici les corrections suggérées:"

# Vérifier si les fichiers statiques sont servis
if [ ! -d "staticfiles" ] || [ $(find staticfiles -name "*.css" | wc -l) -eq 0 ]; then
    echo "   ❌ Fichiers statiques manquants ou incomplets"
    echo "   🔧 Solution: sudo -u www-data python manage.py collectstatic --noinput"
fi

# Vérifier si les services tournent
if ! sudo systemctl is-active --quiet gunicorn; then
    echo "   ❌ Gunicorn ne tourne pas"
    echo "   🔧 Solution: sudo systemctl start gunicorn"
fi

if ! sudo systemctl is-active --quiet nginx; then
    echo "   ❌ Nginx ne tourne pas"
    echo "   🔧 Solution: sudo systemctl start nginx"
fi

# Vérifier si le SuperAdmin a le bon rôle
python manage.py shell << 'EOF'
from accounts.models import User
superadmin = User.objects.filter(username='SuperAdmin').first()
if superadmin and superadmin.role != 'SUPER_ADMIN':
    print("   ❌ SuperAdmin n'a pas le bon rôle")
    print("   🔧 Solution: superadmin.role = 'SUPER_ADMIN'; superadmin.save()")
EOF

echo ""
echo "✅ Diagnostic complet terminé !"
echo ""
echo "📋 Résumé des problèmes identifiés:"
echo "   1. Vérifier l'état des services ci-dessus"
echo "   2. Vérifier les fichiers statiques"
echo "   3. Vérifier les permissions des utilisateurs"
echo "   4. Vérifier les logs d'erreurs"
echo "   5. Vérifier la configuration Nginx"
echo ""
echo "🔍 Prochaines étapes:"
echo "   1. Corriger les problèmes identifiés"
echo "   2. Redémarrer les services si nécessaire"
echo "   3. Tester avec un navigateur en mode incognito"
echo "   4. Comparer avec l'environnement local"
