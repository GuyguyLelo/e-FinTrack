#!/bin/bash
# clean_vps_complete.sh - Nettoyage complet VPS pour synchronisation

set -e

echo "🧹 Nettoyage Complet VPS - Synchronisation avec Local"
echo "================================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Arrêt des services..."
sudo systemctl stop gunicorn
sudo systemctl stop nginx

echo "✅ Services arrêtés"

echo ""
echo "🧹 2. Nettoyage des sessions et cookies..."

# Supprimer les sessions Django
python manage.py shell << 'EOF'
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

# Supprimer toutes les sessions
count = Session.objects.all().count()
Session.objects.all().delete()
print(f"✅ {count} sessions Django supprimées")

# Vérifier les utilisateurs
users = User.objects.all()
print(f"✅ Utilisateurs dans la base: {users.count()}")
for user in users:
    print(f"   - {user.username} ({user.role})")
EOF

echo ""
echo "🧹 3. Nettoyage des fichiers temporaires..."

# Supprimer les fichiers temporaires
rm -rf __pycache__/
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Fichiers Python temporaires supprimés"

echo ""
echo "🧹 4. Nettoyage des fichiers statiques..."

# Supprimer complètement les fichiers statiques
sudo rm -rf staticfiles/
sudo rm -rf media/

echo "✅ Fichiers statiques et médias supprimés"

echo ""
echo "🧹 5. Nettoyage des logs Django..."

# Supprimer les logs Django
rm -f efinance.log
rm -f *.log

echo "✅ Logs Django supprimés"

echo ""
echo "🧹 6. Nettoyage des cookies du navigateur (instructions)..."

echo "📋 Instructions pour nettoyer les cookies du navigateur:"
echo "   1. Ouvrir les outils de développement (F12)"
echo "   2. Aller dans l'onglet 'Application' ou 'Stockage'"
echo "   3. Cliquer sur 'Cookies' → 'http://187.77.171.80'"
echo "   4. Supprimer tous les cookies"
echo "   5. Ou utiliser: document.cookie.split(';').forEach(c => document.cookie = c.replace(/^ +/, '').replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/'));"

echo ""
echo "🧹 7. Nettoyage du cache du navigateur..."

echo "📋 Instructions pour vider le cache:"
echo "   1. Ctrl+Shift+Delete (ou Cmd+Shift+Delete sur Mac)"
echo "   2. Sélectionner 'Images et fichiers en cache'"
echo "   3. Choisir 'Dernière heure' ou 'Toutes les périodes'"
echo "   4. Cliquer sur 'Effacer les données'"
echo "   5. Ou utiliser: Ctrl+F5 pour recharger sans cache"

echo ""
echo "🔧 8. Recréation des répertoires nécessaires..."

mkdir -p staticfiles
mkdir -p media
mkdir -p logs

echo "✅ Répertoires créés"

echo ""
echo "🔧 9. Correction des permissions..."

# Donner les permissions correctes
sudo chown -R www-data:www-data staticfiles/
sudo chown -R www-data:www-data media/
sudo chmod -R 755 staticfiles/
sudo chmod -R 755 media/

echo "✅ Permissions corrigées"

echo ""
echo "🔧 10. Migration de la base de données..."

# Appliquer les migrations pour s'assurer que tout est à jour
python manage.py makemigrations
python manage.py migrate

echo "✅ Migrations appliquées"

echo ""
echo "🔧 11. Collecte des fichiers statiques..."

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

echo "✅ Fichiers statiques collectés"

echo ""
echo "🔧 12. Création du SuperAdmin si nécessaire..."

python manage.py shell << 'EOF'
from accounts.models import User
from django.contrib.auth.models import User as DjangoUser

try:
    superadmin = User.objects.get(username='SuperAdmin')
    print(f"✅ SuperAdmin existe: {superadmin.role}")
except User.DoesNotExist:
    print("❌ SuperAdmin non trouvé, création...")
    superadmin = User.objects.create_superuser(
        username='SuperAdmin',
        email='superadmin@efinance.dg',
        password='SuperAdmin123!',
        role='SUPER_ADMIN',
        first_name='Super',
        last_name='Admin'
    )
    print("✅ SuperAdmin créé")

# Vérifier les autres utilisateurs
users = User.objects.all()
print(f"✅ Total utilisateurs: {users.count()}")
for user in users:
    print(f"   - {user.username} ({user.role}) - Actif: {user.is_active}")

EOF

echo ""
echo "🔧 13. Vérification des templates..."

python manage.py shell << 'EOF'
from django.template import Template

try:
    with open('templates/base.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    print("✅ Template base.html syntaxe OK")
    
    # Vérifier les sections importantes
    sections = ['Menu SuperAdmin', 'Menu Direction', 'Menu AdminDaf', 'Menu Opérations']
    for section in sections:
        if section in template_content:
            print(f"✅ {section} trouvé")
        else:
            print(f"❌ {section} manquant")
    
except Exception as e:
    print(f"❌ Erreur template: {e}")

EOF

echo ""
echo "🔧 14. Test des URLs..."

python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User

print("Test d'accès aux URLs:")

try:
    # Test SuperAdmin
    superadmin = User.objects.get(username='SuperAdmin')
    client = Client()
    client.force_login(superadmin)
    
    response = client.get('/tableau-bord-feuilles/')
    print(f"✅ Tableau de bord accessible: {response.status_code == 200}")
    
    response = client.get('/admin/')
    print(f"✅ Admin Django accessible: {response.status_code == 200}")
    
    # Test AdminDaf
    try:
        admin_daf = User.objects.get(username='AdminDaf')
        client.force_login(admin_daf)
        response = client.get('/demandes/natures/')
        print(f"✅ AdminDaf natures accessibles: {response.status_code == 200}")
    except:
        print("❌ AdminDaf non trouvé")
    
except Exception as e:
    print(f"❌ Erreur test: {e}")

EOF

echo ""
echo "🔄 15. Redémarrage des services..."

sudo systemctl start gunicorn
sudo systemctl start nginx

echo ""
echo "🌐 16. Vérification des services..."

sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

echo ""
echo "✅ Nettoyage complet VPS terminé !"
echo ""
echo "🎯 Actions effectuées:"
echo "   ✅ Services arrêtés et redémarrés"
echo "   ✅ Sessions Django supprimées"
echo "   ✅ Fichiers temporaires nettoyés"
echo "   ✅ Fichiers statiques recréés"
echo "   ✅ Permissions corrigées"
echo "   ✅ Migrations appliquées"
echo "   ✅ Templates vérifiés"
echo "   ✅ URLs testées"
echo ""
echo "🌐 Maintenant testez avec un navigateur propre:"
echo "   1. Ouvrir un nouveau navigateur ou mode incognito"
echo "   2. Aller sur: http://187.77.171.80/accounts/login/"
echo "   3. Se connecter avec SuperAdmin / SuperAdmin123!"
echo "   4. Vérifier que tout fonctionne comme en local"
echo ""
echo "🔍 Si problèmes persistent:"
echo "   1. Vérifier les logs: sudo journalctl -u gunicorn -f"
echo "   2. Vérifier Nginx: sudo nginx -t"
echo "   3. Comparer les fichiers: diff templates/base.html ~/e-FinTrack/templates/base.html"
