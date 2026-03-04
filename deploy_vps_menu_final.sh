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
