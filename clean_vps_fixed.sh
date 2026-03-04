#!/bin/bash
# clean_vps_fixed.sh - Nettoyage VPS corrigé pour modèle User personnalisé

set -e

echo "🧹 Nettoyage VPS Corrigé - Modèle User Personnalisé"
echo "=============================================="

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

# Vérifier les utilisateurs avec le bon modèle
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
echo "🔧 6. Recréation des répertoires nécessaires..."

mkdir -p staticfiles
mkdir -p media
mkdir -p logs

echo "✅ Répertoires créés"

echo ""
echo "🔧 7. Correction des permissions..."

# Donner les permissions correctes
sudo chown -R www-data:www-data staticfiles/
sudo chown -R www-data:www-data media/
sudo chmod -R 755 staticfiles/
sudo chmod -R 755 media/

echo "✅ Permissions corrigées"

echo ""
echo "🔧 8. Migration de la base de données..."

# Appliquer les migrations pour s'assurer que tout est à jour
python manage.py makemigrations
python manage.py migrate

echo "✅ Migrations appliquées"

echo ""
echo "🔧 9. Collecte des fichiers statiques..."

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

echo "✅ Fichiers statiques collectés"

echo ""
echo "🔧 10. Création du SuperAdmin si nécessaire..."

python manage.py shell << 'EOF'
from accounts.models import User

try:
    superadmin = User.objects.get(username='SuperAdmin')
    print(f"✅ SuperAdmin existe: {superadmin.role}")
    print(f"   is_superuser: {superadmin.is_superuser}")
    print(f"   is_staff: {superadmin.is_staff}")
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

# Créer AdminDaf si nécessaire
try:
    admin_daf = User.objects.get(username='AdminDaf')
    print(f"✅ AdminDaf existe: {admin_daf.role}")
except User.DoesNotExist:
    print("❌ AdminDaf non trouvé, création...")
    admin_daf = User.objects.create_user(
        username='AdminDaf',
        email='admindaf@efinance.dg',
        password='AdminDaf123!',
        role='ADMIN',
        first_name='Admin',
        last_name='Daf'
    )
    print("✅ AdminDaf créé")

# Créer DirDaf si nécessaire
try:
    dir_daf = User.objects.get(username='DirDaf')
    print(f"✅ DirDaf existe: {dir_daf.role}")
except User.DoesNotExist:
    print("❌ DirDaf non trouvé, création...")
    dir_daf = User.objects.create_user(
        username='DirDaf',
        email='dirdaf@efinance.dg',
        password='DirDaf123!',
        role='DG',
        first_name='Directeur',
        last_name='Daf'
    )
    print("✅ DirDaf créé")

# Créer DivDaf si nécessaire
try:
    div_daf = User.objects.get(username='DivDaf')
    print(f"✅ DivDaf existe: {div_daf.role}")
except User.DoesNotExist:
    print("❌ DivDaf non trouvé, création...")
    div_daf = User.objects.create_user(
        username='DivDaf',
        email='divdaf@efinance.dg',
        password='DivDaf123!',
        role='CD_FINANCE',
        first_name='Chef',
        last_name='Division'
    )
    print("✅ DivDaf créé")

# Créer OpsDaf si nécessaire
try:
    ops_daf = User.objects.get(username='OpsDaf')
    print(f"✅ OpsDaf existe: {ops_daf.role}")
except User.DoesNotExist:
    print("❌ OpsDaf non trouvé, création...")
    ops_daf = User.objects.create_user(
        username='OpsDaf',
        email='opsdaf@efinance.dg',
        password='OpsDaf123!',
        role='OPERATEUR_SAISIE',
        first_name='Opérateur',
        last_name='Saisie'
    )
    print("✅ OpsDaf créé")

# Résumé final
users = User.objects.all()
print(f"✅ Total utilisateurs: {users.count()}")
for user in users:
    print(f"   - {user.username} ({user.role}) - Actif: {user.is_active}")

EOF

echo ""
echo "🔧 11. Vérification des templates..."

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
echo "🔧 12. Test des URLs..."

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
    
    # Test AdminDaf
    try:
        admin_daf = User.objects.get(username='AdminDaf')
        client.force_login(admin_daf)
        response = client.get('/demandes/natures/')
        print(f"✅ AdminDaf natures accessibles: {response.status_code == 200}")
    except Exception as e:
        print(f"❌ AdminDaf test: {e}")
    
    # Test DirDaf
    try:
        dir_daf = User.objects.get(username='DirDaf')
        client.force_login(dir_daf)
        response = client.get('/tableau-bord-feuilles/')
        print(f"✅ DirDaf tableau de bord accessible: {response.status_code == 200}")
    except Exception as e:
        print(f"❌ DirDaf test: {e}")
    
except Exception as e:
    print(f"❌ Erreur test général: {e}")

EOF

echo ""
echo "🔄 13. Redémarrage des services..."

sudo systemctl start gunicorn
sudo systemctl start nginx

echo ""
echo "🌐 14. Vérification des services..."

sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

echo ""
echo "✅ Nettoyage VPS corrigé terminé !"
echo ""
echo "🎯 Actions effectuées:"
echo "   ✅ Services arrêtés et redémarrés"
echo "   ✅ Sessions Django supprimées"
echo "   ✅ Fichiers temporaires nettoyés"
echo "   ✅ Fichiers statiques recréés"
echo "   ✅ Permissions corrigées"
echo "   ✅ Migrations appliquées"
echo "   ✅ Utilisateurs créés/vérifiés"
echo "   ✅ Templates vérifiés"
echo "   ✅ URLs testées"
echo ""
echo "🌐 Maintenant testez avec un navigateur propre:"
echo "   1. Ouvrir un nouveau navigateur ou mode incognito"
echo "   2. Aller sur: http://187.77.171.80/accounts/login/"
echo "   3. Se connecter avec les utilisateurs:"
echo "      - SuperAdmin / SuperAdmin123!"
echo "      - AdminDaf / AdminDaf123!"
echo "      - DirDaf / DirDaf123!"
echo "      - DivDaf / DivDaf123!"
echo "      - OpsDaf / OpsDaf123!"
echo "   4. Vérifier que tout fonctionne comme en local"
echo ""
echo "🔍 Si problèmes persistent:"
echo "   1. Vérifier les logs: sudo journalctl -u gunicorn -f"
echo "   2. Vérifier Nginx: sudo nginx -t"
echo "   3. Comparer les fichiers: diff templates/base.html ~/e-FinTrack/templates/base.html"
