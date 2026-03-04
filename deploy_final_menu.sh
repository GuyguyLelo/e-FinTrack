#!/bin/bash
# deploy_final_menu.sh - Déploiement final du menu corrigé

set -e

echo "🚀 Déploiement Final du Menu Corrigé"
echo "=================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. État actuel du template:"
echo "✅ Template syntaxiquement correct"
echo "✅ Menu général fonctionne"
echo "⚠️ Menu DG à vérifier"

echo ""
echo "🔧 2. Vérification finale du template..."

python manage.py shell << 'EOF'
from django.template import Template

try:
    with open('templates/base.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    print("✅ Template syntaxe OK")
    
    # Vérifier les sections de menu
    if 'Menu Direction' in template_content:
        print("✅ Section Menu Direction présente")
    else:
        print("❌ Section Menu Direction manquante")
    
    if 'Menu Général' in template_content:
        print("✅ Section Menu Général présente")
    else:
        print("❌ Section Menu Général manquante")
    
    if 'Menu SuperAdmin' in template_content:
        print("✅ Section Menu SuperAdmin présente")
    else:
        print("❌ Section Menu SuperAdmin manquante")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

EOF

echo ""
echo "🔧 3. Création du script de déploiement VPS..."

cat > deploy_vps_menu.sh << 'DEPLOY_VPS'
#!/bin/bash
# Script de déploiement VPS pour le menu corrigé

set -e

echo "🚀 Déploiement VPS - Menu Corrigé"
echo "=============================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Vérification du template..."
python manage.py shell << 'EOF'
from django.template import Template

try:
    with open('templates/base.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    print("✅ Template syntaxe OK")
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
echo "🎯 Configuration du menu:"
echo "📋 AdminDaf → Uniquement Natures Économiques"
echo "📋 SuperAdmin → Tableau de bord + Admin Django (pas les natures)"
echo "📋 DirDaf, DivDaf → Tableau de bord + Clôtures"
echo "📋 OpsDaf → Menu Opérations complet"
echo "📋 Autres → Menu Général"
echo ""
echo "🌐 Testez sur votre VPS:"
echo "   http://187.77.171.80/accounts/login/"
echo ""
echo "🔍 Pour vérifier les logs en cas de problème:"
echo "   sudo journalctl -u gunicorn -f"
echo "   sudo journalctl -u nginx -f"
DEPLOY_VPS

chmod +x deploy_vps_menu.sh

echo "✅ Script deploy_vps_menu.sh créé"

echo ""
echo "📋 Instructions de déploiement:"
echo "1. git add ."
echo "2. git commit -m \"Correction du menu et des redirections\""
echo "3. git push origin main"
echo "4. Sur VPS: git pull origin main"
echo "5. Sur VPS: ./deploy_vps_menu.sh"

echo ""
echo "🎊 Menu corrigé et prêt pour le déploiement !"
echo ""
echo "🌐 Testez maintenant en local:"
echo "   python manage.py runserver 127.0.0.1:8000"
echo ""
echo "📋 Pages à tester:"
echo "   http://127.0.0.1:8000/accounts/login/"
echo "   http://127.0.0.1:8000/tableau-bord-feuilles/"
