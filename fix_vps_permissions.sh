#!/bin/bash
# fix_vps_permissions.sh - Correction des permissions et problèmes VPS

set -e

echo "🔧 Correction des Permissions VPS"
echo "=============================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Correction des permissions des fichiers statiques..."

# Donner les permissions correctes aux fichiers statiques
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

echo "✅ Permissions statiques corrigées"

echo ""
echo "🔧 2. Nettoyage manuel des fichiers statiques..."

# Supprimer manuellement les fichiers problématiques
sudo rm -rf staticfiles/admin/
sudo rm -rf staticfiles/css/
sudo rm -rf staticfiles/js/
sudo rm -rf staticfiles/bootstrap/

echo "✅ Anciens fichiers statiques supprimés"

echo ""
echo "🔧 3. Recréation des fichiers statiques..."

# Créer les répertoires nécessaires
mkdir -p staticfiles/admin
mkdir -p staticfiles/css
mkdir -p staticfiles/js
mkdir -p staticfiles/bootstrap

# Donner les permissions
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

echo "✅ Répertoires statiques créés"

echo ""
echo "🔧 4. Collecte des fichiers statiques sans --clear..."

# Collecter sans --clear pour éviter les erreurs de permissions
python manage.py collectstatic --noinput

echo "✅ Fichiers statiques collectés"

echo ""
echo "🔧 5. Vérification des fichiers statiques..."

if [ -d "staticfiles" ]; then
    echo "✅ Répertoire staticfiles trouvé"
    echo "   Taille: $(du -sh staticfiles | cut -f1)"
    echo "   Fichiers CSS: $(find staticfiles -name "*.css" | wc -l)"
    echo "   Fichiers JS: $(find staticfiles -name "*.js" | wc -l)"
    
    # Vérifier les fichiers Bootstrap
    echo ""
    echo "   Fichiers Bootstrap:"
    find staticfiles -name "*bootstrap*" -type f | head -5
else
    echo "❌ Répertoire staticfiles manquant"
fi

echo ""
echo "🔧 6. Correction du template admin..."

# S'assurer que le template admin existe
if [ ! -f "templates/admin/base_site_custom.html" ]; then
    mkdir -p templates/admin
    cat > templates/admin/base_site_custom.html << 'ADMIN_TEMPLATE'
{% extends "admin/base_site.html" %}

{% block extrastyle %}{{ block.super }}
<style>
/* Styles personnalisés pour l'admin Django */
:root {
    --dgrad-bleu: #1a3a5f;
    --dgrad-dore: #d4af37;
    --dgrad-blanc: #ffffff;
    --dgrad-gris-clair: #f5f5f5;
}

/* Header */
#header {
    background: linear-gradient(135deg, var(--dgrad-bleu) 0%, #2a4a6f 100%) !important;
    border-bottom: 2px solid var(--dgrad-dore) !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

#branding h1, #branding h1 a:link, #branding h1 a:visited {
    color: var(--dgrad-dore) !important;
    font-weight: bold !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
}

/* Navigation */
#nav-sidebar {
    background-color: var(--dgrad-bleu) !important;
    border-right: 1px solid rgba(212, 175, 55, 0.3) !important;
}

#nav-sidebar .nav-item a {
    color: rgba(255,255,255,0.8) !important;
    border-radius: 5px !important;
    margin: 2px 0 !important;
    transition: all 0.3s !important;
}

#nav-sidebar .nav-item a:hover,
#nav-sidebar .nav-item a:focus {
    background-color: rgba(212, 175, 55, 0.2) !important;
    color: var(--dgrad-dore) !important;
    transform: translateX(5px) !important;
}

#nav-sidebar .nav-item.current-app a {
    background-color: rgba(212, 175, 55, 0.3) !important;
    color: var(--dgrad-dore) !important;
    font-weight: bold !important;
}

/* Main content */
.main {
    background-color: var(--dgrad-gris-clair) !important;
}

/* Tables */
#result_list thead th {
    background-color: var(--dgrad-bleu) !important;
    color: var(--dgrad-blanc) !important;
    border-bottom: 2px solid var(--dgrad-dore) !important;
    font-weight: bold !important;
}

/* Buttons */
.button, input[type=submit], input[type=button], .submit-row input {
    background: linear-gradient(135deg, var(--dgrad-bleu) 0%, #2a4a6f 100%) !important;
    color: var(--dgrad-blanc) !important;
    border: 1px solid var(--dgrad-bleu) !important;
    border-radius: 5px !important;
    padding: 8px 16px !important;
    font-weight: bold !important;
    transition: all 0.3s !important;
}

.button:hover, input[type=submit]:hover, input[type=button]:hover, .submit-row input:hover {
    background: linear-gradient(135deg, #2a4a6f 0%, var(--dgrad-bleu) 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
}

/* Footer */
#footer {
    background-color: var(--dgrad-bleu) !important;
    color: var(--dgrad-blanc) !important;
    border-top: 2px solid var(--dgrad-dore) !important;
    text-align: center !important;
    padding: 15px !important;
}
</style>
{% endblock %}
ADMIN_TEMPLATE
    echo "✅ Template admin créé"
else
    echo "✅ Template admin existe déjà"
fi

echo ""
echo "🔧 7. Vérification du template base.html..."

python manage.py shell << 'EOF'
from django.template import Template

try:
    with open('templates/base.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    print("✅ Template base.html syntaxe OK")
    
    # Vérifier les sections importantes
    sections = ['Menu SuperAdmin', 'Tableau de bord', 'Natures Économiques']
    for section in sections:
        if section in template_content:
            print(f"✅ {section} trouvé")
        else:
            print(f"❌ {section} manquant")
    
except Exception as e:
    print(f"❌ Erreur template: {e}")
EOF

echo ""
echo "🔧 8. Vérification du SuperAdmin..."

python manage.py shell << 'EOF'
from accounts.models import User

try:
    superadmin = User.objects.get(username='SuperAdmin')
    print(f"✅ SuperAdmin trouvé: {superadmin.role}")
    print(f"   is_superuser: {superadmin.is_superuser}")
    print(f"   is_staff: {superadmin.is_staff}")
    print(f"   peut_voir_tableau_bord: {superadmin.peut_voir_tableau_bord()}")
    print(f"   peut_ajouter_nature_economique: {superadmin.peut_ajouter_nature_economique()}")
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
except Exception as e:
    print(f"❌ Erreur SuperAdmin: {e}")
EOF

echo ""
echo "🔧 9. Test des URLs..."

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
echo "🔄 10. Redémarrage des services..."

# Donner les permissions finales
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 11. Vérification des services..."
sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

echo ""
echo "✅ Correction VPS terminée !"
echo ""
echo "🎯 Actions effectuées:"
echo "   ✅ Permissions des fichiers statiques corrigées"
echo "   ✅ Fichiers statiques collectés sans --clear"
echo "   ✅ Template admin personnalisé vérifié"
echo "   ✅ Template base.html vérifié"
echo "   ✅ SuperAdmin vérifié/créé"
echo "   ✅ Services redémarrés"
echo ""
echo "🌐 Testez maintenant:"
echo "   http://187.77.171.80/accounts/login/"
echo "   http://187.77.171.80/tableau-bord-feuilles/"
echo "   http://187.77.171.80/admin/"
echo ""
echo "🔍 Si problèmes persistent:"
echo "   1. Vérifier Nginx: sudo nginx -t"
echo "   2. Vérifier les logs: sudo journalctl -u gunicorn -f"
echo "   3. Vérifier les permissions: ls -la staticfiles/"
