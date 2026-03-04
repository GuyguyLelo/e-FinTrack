#!/bin/bash
# deploy_vps_final.sh - Déploiement VPS final des menus corrigés

set -e

echo "🚀 Déploiement VPS Final - Menus Corrigés"
echo "========================================"

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Vérification finale du template..."

python manage.py shell << 'EOF'
from django.template import Template

try:
    with open('templates/base.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    print("✅ Template syntaxe OK")
    
    # Vérifier les sections de menu
    sections = {
        'Menu AdminDaf': 'user.username == \'AdminDaf\'',
        'Menu Direction': 'user.role == \'DG\' or user.role == \'DF\' or user.role == \'CD_FINANCE\'',
        'Menu Opérations': 'user.role == \'OPERATEUR_SAISIE\'',
        'Menu SuperAdmin': 'user.is_super_admin or user.is_superuser'
    }
    
    for section, condition in sections.items():
        if section in template_content:
            print(f"✅ {section} trouvé (condition: {condition})")
        else:
            print(f"❌ {section} manquant")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    exit(1)

EOF

echo ""
echo "🔄 2. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 3. Vérification des services..."
sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

echo ""
echo "✅ Déploiement VPS terminé !"
echo ""
echo "🎯 Configuration finale des menus:"
echo "📋 SuperAdmin → Voit tout SAUF les natures économiques"
echo "📋 DirDaf, DivDaf → Uniquement tableau de bord et clôtures"
echo "📋 AdminDaf → Uniquement natures économiques"
echo "📋 OpsDaf → Recettes, dépenses et états"
echo ""
echo "🌐 Testez sur votre VPS:"
echo "   http://187.77.171.80/accounts/login/"
echo ""
echo "🔍 Pour vérifier les logs en cas de problème:"
echo "   sudo journalctl -u gunicorn -f"
echo "   sudo journalctl -u nginx -f"
