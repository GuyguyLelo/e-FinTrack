#!/bin/bash
# deploy_menu_final.sh - Déploiement final des menus corrigés

set -e

echo "🚀 Déploiement Final des Menus Corrigés"
echo "===================================="

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
        'Menu AdminDaf': 'user.role == \'ADMIN\'',
        'Menu Direction': 'user.role == \'DG\' or user.role == \'CD_FINANCE\'',
        'Menu Opérations': 'user.role == \'OPERATEUR_SAISIE\'',
        'Menu SuperAdmin': 'user.username == \'SuperAdmin\' or user.is_superuser'
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
echo "🔧 2. Création du script de déploiement VPS..."

cat > deploy_vps_menu_final.sh << 'DEPLOY_VPS_FINAL'
#!/bin/bash
# Script de déploiement VPS final pour les menus corrigés

set -e

echo "🚀 Déploiement VPS - Menus Corrigés"
echo "================================="

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
echo "🎯 Configuration finale des menus:"
echo "📋 AdminDaf (rôle ADMIN) → Menu AdminDaf (uniquement Natures Économiques)"
echo "📋 DirDaf (rôle DG) → Menu Direction (Tableau de bord + Clôtures)"
echo "📋 DivDaf (rôle CD_FINANCE) → Menu Direction (Tableau de bord + Clôtures)"
echo "📋 OpsDaf (rôle OPERATEUR_SAISIE) → Menu Opérations (accès standard)"
echo "📋 SuperAdmin → Menu SuperAdmin (tout sauf natures dans menu)"
echo ""
echo "🌐 Testez sur votre VPS:"
echo "   http://187.77.171.80/accounts/login/"
echo ""
echo "🔍 Pour vérifier les logs en cas de problème:"
echo "   sudo journalctl -u gunicorn -f"
echo "   sudo journalctl -u nginx -f"
DEPLOY_VPS_FINAL

chmod +x deploy_vps_menu_final.sh

echo "✅ Script deploy_vps_menu_final.sh créé"

echo ""
echo "📋 Instructions de déploiement:"
echo "1. git add ."
echo "2. git commit -m \"Correction finale des menus par rôle\""
echo "3. git push origin main"
echo "4. Sur VPS: git pull origin main"
echo "5. Sur VPS: ./deploy_vps_menu_final.sh"

echo ""
echo "🎊 Menus corrigés et prêts pour le déploiement !"
echo ""
echo "🌐 Testez maintenant en local:"
echo "   python manage.py runserver 127.0.0.1:8000"
echo ""
echo "📋 Tests à effectuer:"
echo "   AdminDaf → Redirection vers /demandes/natures/"
echo "   DirDaf → Menu Direction avec Tableau de bord + Clôtures"
echo "   DivDaf → Menu Direction avec Tableau de bord + Clôtures"
echo "   OpsDaf → Menu Opérations complet"
echo "   SuperAdmin → Menu SuperAdmin (tout sauf natures)"
