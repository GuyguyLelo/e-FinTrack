#!/bin/bash
# deploy_vps_clotures.sh - Déploiement VPS avec clôtures pour DirDaf et DivDaf

set -e

echo "🔧 Déploiement VPS - Ajout des Clôtures pour DirDaf et DivDaf"
echo "========================================================"

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Modification apportée:"
echo "   Ajout des clôtures dans le menu Direction"
echo "   DirDaf (DG) → Tableau de bord + Clôtures"
echo "   DivDaf (CD_FINANCE) → Tableau de bord + Clôtures"

echo ""
echo "🔧 2. Vérification du template..."

python manage.py shell << 'EOF'
from django.template import Template

try:
    with open('templates/base.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    print("✅ Template syntaxe OK")
    
    # Vérifier que les clôtures sont bien présentes
    if 'Clôtures' in template_content:
        print("✅ Clôtures trouvées dans le template")
    else:
        print("❌ Clôtures non trouvées")
        
    # Vérifier la condition pour les clôtures
    if "user.role == 'DG' or user.role == 'DF' or user.role == 'CD_FINANCE'" in template_content:
        print("✅ Condition pour clôtures correcte")
    else:
        print("❌ Condition pour clôtures incorrecte")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    exit(1)

EOF

echo ""
echo "🔄 3. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 4. Vérification des services..."
sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

echo ""
echo "✅ Déploiement VPS terminé !"
echo ""
echo "🎯 Configuration finale:"
echo "📋 SuperAdmin → Voit tout SAUF les natures économiques"
echo "📋 DirDaf, DivDaf → Tableau de bord + Clôtures"
echo "📋 AdminDaf → Uniquement natures économiques"
echo "📋 OpsDaf → Recettes, dépenses et états"
echo ""
echo "🌐 Testez sur votre VPS:"
echo "   http://187.77.171.80/accounts/login/"
echo ""
echo "🔍 Tests à effectuer:"
echo "   DirDaf → Menu Direction avec Tableau de bord + Clôtures ✅"
echo "   DivDaf → Menu Direction avec Tableau de bord + Clôtures ✅"
