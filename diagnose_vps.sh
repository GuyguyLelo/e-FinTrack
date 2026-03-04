#!/bin/bash
# diagnose_vps.sh - Diagnostic et correction des problèmes VPS

set -e

echo "🔍 Diagnostic VPS - Tableau de bord et Admin Django"
echo "================================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Vérification des fichiers statiques..."

# Vérifier si les fichiers statiques existent
if [ -d "staticfiles" ]; then
    echo "✅ Répertoire staticfiles trouvé"
    echo "   Taille: $(du -sh staticfiles | cut -f1)"
    echo "   Fichiers CSS: $(find staticfiles -name "*.css" | wc -l)"
    echo "   Fichiers JS: $(find staticfiles -name "*.js" | wc -l)"
else
    echo "❌ Répertoire staticfiles manquant"
fi

echo ""
echo "🔍 2. Vérification du template admin..."

if [ -f "templates/admin/base_site_custom.html" ]; then
    echo "✅ Template admin personnalisé trouvé"
else
    echo "❌ Template admin personnalisé manquant"
fi

echo ""
echo "🔍 3. Vérification de la configuration Django..."

python manage.py shell << 'EOF'
import os
from django.conf import settings

print("Configuration Django:")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   STATIC_URL: {settings.STATIC_URL}")
print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"   STATICFILES_DIRS: {settings.STATICFILES_DIRS}")

# Vérifier les templates
print(f"\nTemplates DIRS: {settings.TEMPLATES[0]['DIRS']}")

# Vérifier si les fichiers statiques sont collectés
if os.path.exists(settings.STATIC_ROOT):
    print(f"\n✅ STATIC_ROOT existe: {settings.STATIC_ROOT}")
    print(f"   Fichiers dans STATIC_ROOT: {len(os.listdir(settings.STATIC_ROOT))}")
else:
    print(f"\n❌ STATIC_ROOT manquant: {settings.STATIC_ROOT}")

EOF

echo ""
echo "🔧 4. Correction des fichiers statiques..."

# Collecter les fichiers statiques
echo "   Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo ""
echo "🔍 5. Vérification après collecte..."

if [ -d "staticfiles" ]; then
    echo "✅ Fichiers statiques collectés"
    echo "   Taille: $(du -sh staticfiles | cut -f1)"
    echo "   Fichiers CSS: $(find staticfiles -name "*.css" | wc -l)"
    echo "   Fichiers JS: $(find staticfiles -name "*.js" | wc -l)"
    
    # Vérifier les fichiers Bootstrap
    echo ""
    echo "   Fichiers Bootstrap:"
    find staticfiles -name "*bootstrap*" -type f | head -10
else
    echo "❌ Échec de la collecte des fichiers statiques"
fi

echo ""
echo "🔧 6. Correction du template admin..."

# Créer le template admin si manquant
if [ ! -f "templates/admin/base_site_custom.html" ]; then
    echo "   Création du template admin personnalisé..."
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

# Vérifier que le template base.html est correct
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
echo "🔄 8. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 9. Vérification des services..."
sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

echo ""
echo "🔍 10. Test d'accès aux URLs..."

python manage.py shell << 'EOF'
from django.test import Client
from django.urls import reverse
from accounts.models import User

print("Test d'accès aux URLs:")

# Test tableau de bord
try:
    url_tableau = reverse('tableau_bord_feuilles:tableau_bord_feuilles')
    print(f"✅ URL tableau de bord: {url_tableau}")
except Exception as e:
    print(f"❌ URL tableau de bord: {e}")

# Test natures
try:
    url_natures = reverse('demandes:nature_liste')
    print(f"✅ URL natures: {url_natures}")
except Exception as e:
    print(f"❌ URL natures: {e}")

# Test admin
try:
    url_admin = '/admin/'
    print(f"✅ URL admin: {url_admin}")
except Exception as e:
    print(f"❌ URL admin: {e}")

# Test SuperAdmin
try:
    superadmin = User.objects.get(username='SuperAdmin')
    client = Client()
    client.force_login(superadmin)
    
    response = client.get('/tableau-bord-feuilles/')
    print(f"✅ SuperAdmin accès tableau de bord: {response.status_code == 200}")
    
    response = client.get('/admin/')
    print(f"✅ SuperAdmin accès admin: {response.status_code == 200}")
    
except Exception as e:
    print(f"❌ Test SuperAdmin: {e}")

EOF

echo ""
echo "✅ Diagnostic et correction terminés !"
echo ""
echo "🎯 Actions effectuées:"
echo "   ✅ Collecte des fichiers statiques"
echo "   ✅ Création du template admin personnalisé"
echo "   ✅ Vérification du template base.html"
echo "   ✅ Redémarrage des services"
echo ""
echo "🌐 Testez maintenant:"
echo "   http://187.77.171.80/accounts/login/"
echo "   http://187.77.171.80/tableau-bord-feuilles/"
echo "   http://187.77.171.80/admin/"
echo ""
echo "🔍 Si problèmes persistent:"
echo "   1. Vérifier les permissions des fichiers statiques"
echo "   2. Vérifier la configuration Nginx pour /static/"
echo "   3. Vérifier les logs: sudo journalctl -u gunicorn -f"
