#!/bin/bash
# deploy_vps_final_complete.sh - Déploiement VPS final complet

set -e

echo "🚀 Déploiement VPS Final Complet"
echo "================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Modifications apportées:"
echo "   ✅ Création du SuperAdmin en local"
echo "   ✅ SuperAdmin voit tableau de bord ET natures économiques"
echo "   ✅ Correction du design de l'admin Django"
echo "   ✅ Template admin personnalisé avec style e-FinTrack"

echo ""
echo "🔧 2. Vérification du SuperAdmin..."

python manage.py shell << 'EOF'
from accounts.models import User

try:
    superadmin = User.objects.get(username='SuperAdmin')
    print(f"✅ SuperAdmin trouvé: {superadmin.role}")
    print(f"   is_superuser: {superadmin.is_superuser}")
    print(f"   is_staff: {superadmin.is_staff}")
    print(f"   peut_voir_tableau_bord: {superadmin.peut_voir_tableau_bord()}")
    print(f"   peut_ajouter_nature_economique: {superadmin.peut_ajouter_nature_economique()}")
    print(f"   peut_acceder_admin_django: {superadmin.peut_acceder_admin_django()}")
except Exception as e:
    print(f"❌ Erreur: {e}")
EOF

echo ""
echo "🔧 3. Vérification du template..."

python manage.py shell << 'EOF'
from django.template import Template

try:
    with open('templates/base.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    print("✅ Template syntaxe OK")
    
    # Vérifier que SuperAdmin a les natures
    if 'Natures Économiques' in template_content and 'Menu SuperAdmin' in template_content:
        print("✅ SuperAdmin a accès aux natures économiques")
    else:
        print("❌ SuperAdmin n'a pas accès aux natures")
    
    # Vérifier le template admin
    import os
    if os.path.exists('templates/admin/base_site_custom.html'):
        print("✅ Template admin personnalisé trouvé")
    else:
        print("❌ Template admin personnalisé manquant")
    
except Exception as e:
    print(f"❌ Erreur template: {e}")
EOF

echo ""
echo "🔄 4. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 5. Vérification des services..."
sudo systemctl status gunicorn --no-pager -l
sudo systemctl status nginx --no-pager -l

echo ""
echo "✅ Déploiement VPS terminé !"
echo ""
echo "🎯 Configuration finale complète:"
echo "📋 SuperAdmin → Tableau de bord + Natures Économiques + Admin Django avec design corrigé"
echo "📋 DirDaf, DivDaf → Tableau de bord + Clôtures"
echo "📋 AdminDaf → Uniquement natures économiques"
echo "📋 OpsDaf → Recettes, dépenses et états"
echo ""
echo "🌐 Testez sur votre VPS:"
echo "   http://187.77.171.80/accounts/login/"
echo ""
echo "🔍 Tests à effectuer:"
echo "   SuperAdmin → Menu SuperAdmin complet avec natures ✅"
echo "   SuperAdmin → Admin Django avec design e-FinTrack ✅"
echo "   DirDaf/DivDaf → Menu Direction avec clôtures ✅"
echo "   AdminDaf → Menu AdminDaf (natures uniquement) ✅"
echo "   OpsDaf → Menu Opérations complet ✅"
echo ""
echo "🔍 Pour vérifier les logs en cas de problème:"
echo "   sudo journalctl -u gunicorn -f"
echo "   sudo journalctl -u nginx -f"
