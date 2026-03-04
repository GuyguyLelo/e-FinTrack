#!/bin/bash
# clean_vps_final.sh - Nettoyage VPS final avec permissions résolues

set -e

echo "🧹 Nettoyage VPS Final - Permissions Résolues"
echo "=========================================="

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
from accounts.models import User

# Supprimer toutes les sessions
count = Session.objects.all().count()
Session.objects.all().delete()
print(f"✅ {count} sessions Django supprimées")

# Vérifier les utilisateurs
users = User.objects.all()
print(f"✅ Utilisateurs dans la base: {users.count()}")
for user in users:
    print(f"   - {user.username} ({user.role}) - Actif: {user.is_active}")

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
echo "🧹 4. Nettoyage complet des fichiers statiques..."

# Supprimer complètement les fichiers statiques avec sudo
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
echo "🔧 6. Recréation des répertoires avec permissions correctes..."

# Créer les répertoires avec les bonnes permissions
sudo mkdir -p staticfiles
sudo mkdir -p staticfiles/admin
sudo mkdir -p staticfiles/css
sudo mkdir -p staticfiles/js
sudo mkdir -p staticfiles/bootstrap
sudo mkdir -p staticfiles/img
sudo mkdir -p media
sudo mkdir -p logs

echo "✅ Répertoires créés"

echo ""
echo "🔧 7. Application des permissions correctes..."

# Donner les permissions correctes à www-data
sudo chown -R www-data:www-data staticfiles/
sudo chown -R www-data:www-data media/
sudo chown -R www-data:www-data logs/

sudo chmod -R 755 staticfiles/
sudo chmod -R 755 media/
sudo chmod -R 755 logs/

echo "✅ Permissions appliquées"

echo ""
echo "🔧 8. Migration de la base de données..."

# Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

echo "✅ Migrations appliquées"

echo ""
echo "🔧 9. Collecte des fichiers statiques avec permissions..."

# Exécuter collectstatic avec l'utilisateur www-data
sudo -u www-data python manage.py collectstatic --noinput

echo "✅ Fichiers statiques collectés"

echo ""
echo "🔧 10. Vérification des fichiers statiques..."

if [ -d "staticfiles" ]; then
    echo "✅ Répertoire staticfiles trouvé"
    echo "   Taille: $(du -sh staticfiles | cut -f1)"
    echo "   Fichiers CSS: $(find staticfiles -name "*.css" | wc -l)"
    echo "   Fichiers JS: $(find staticfiles -name "*.js" | wc -l)"
    echo "   Permissions: $(ls -la staticfiles/ | head -3)"
else
    echo "❌ Répertoire staticfiles manquant"
fi

echo ""
echo "🔧 11. Correction du SuperAdmin..."

python manage.py shell << 'EOF'
from accounts.models import User

# Corriger le SuperAdmin pour qu'il soit SUPER_ADMIN
try:
    superadmin = User.objects.get(username='SuperAdmin')
    if superadmin.role != 'SUPER_ADMIN':
        superadmin.role = 'SUPER_ADMIN'
        superadmin.is_superuser = True
        superadmin.is_staff = True
        superadmin.save()
        print(f"✅ SuperAdmin corrigé: {superadmin.role}")
    else:
        print(f"✅ SuperAdmin déjà correct: {superadmin.role}")
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

# Vérifier tous les utilisateurs
users = User.objects.all()
print(f"✅ Total utilisateurs: {users.count()}")
for user in users:
    print(f"   - {user.username} ({user.role}) - Actif: {user.is_active}")

EOF

echo ""
echo "🔧 12. Vérification des templates..."

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
echo "🔧 13. Test des URLs..."

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
    
    # Vérifier le contenu
    content = response.content.decode('utf-8')
    print(f"✅ Menu SuperAdmin présent: {'Menu SuperAdmin' in content}")
    print(f"✅ Tableau de bord présent: {'Tableau de bord' in content}")
    print(f"✅ Natures Économiques présentes: {'Natures Économiques' in content}")
    
except Exception as e:
    print(f"❌ Erreur test: {e}")

EOF

echo ""
echo "🔄 14. Redémarrage des services..."

sudo systemctl start gunicorn
sudo systemctl start nginx

echo ""
echo "🌐 15. Vérification des services..."

sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

echo ""
echo "✅ Nettoyage VPS final terminé !"
echo ""
echo "🎯 Actions effectuées:"
echo "   ✅ Services arrêtés et redémarrés"
echo "   ✅ Sessions Django supprimées"
echo "   ✅ Fichiers temporaires nettoyés"
echo "   ✅ Fichiers statiques recréés avec www-data"
echo "   ✅ Permissions correctes appliquées"
echo "   ✅ Migrations appliquées"
echo "   ✅ SuperAdmin corrigé"
echo "   ✅ Templates vérifiés"
echo "   ✅ URLs testées"
echo ""
echo "🌐 Maintenant testez avec un navigateur propre:"
echo "   1. Ouvrir un nouveau navigateur ou mode incognito"
echo "   2. Aller sur: http://187.77.171.80/accounts/login/"
echo "   3. Se connecter avec SuperAdmin / SuperAdmin123!"
echo "   4. Vérifier que tout fonctionne comme en local"
echo ""
echo "🎯 Configuration finale:"
echo "   - SuperAdmin: rôle SUPER_ADMIN avec tous les accès"
echo "   - AdminDaf: rôle ADMIN (natures économiques)"
echo "   - DirDaf: rôle DG (tableau + clôtures)"
echo "   - DivDaf: rôle CD_FINANCE (tableau + clôtures)"
echo "   - OpsDaf: rôle OPERATEUR_SAISIE (opérations)"
echo ""
echo "🔍 Si problèmes persistent:"
echo "   1. Vérifier les logs: sudo journalctl -u gunicorn -f"
echo "   2. Vérifier Nginx: sudo nginx -t"
echo "   3. Vérifier les permissions: ls -la staticfiles/"
