#!/bin/bash
# fix_vps_no_logs.sh - Correction VPS Sans Logs pour éviter les erreurs de permissions

set -e

echo "🔧 Correction VPS Sans Logs - Éviter les Erreurs de Permissions"
echo "================================================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔧 1. Désactivation temporaire des logs Django..."
echo "   Solution: Modification des settings pour désactiver les logs de fichiers"

# Créer une sauvegarde des settings
cp efinance_daf/settings.py efinance_daf/settings.py.backup

# Modifier les settings pour désactiver les logs de fichiers
sed -i 's/"file": "efinance.log"/"file": null/' efinance_daf/settings.py
sed -i 's/"filename": "efinance.log"/"filename": null/' efinance_daf/settings.py

echo "✅ Logs de fichiers désactivés dans les settings"

echo ""
echo "🔧 2. Correction des fichiers statiques manquants..."
echo "   Solution: Collecte complète avec chemin Python complet"

# Supprimer et recréer les fichiers statiques
sudo rm -rf staticfiles/
sudo mkdir -p staticfiles
sudo chown -R www-data:www-data staticfiles/
sudo chmod -R 755 staticfiles/

# Utiliser le chemin complet de Python
PYTHON_PATH="/home/kandolo/e-FinTrack/venv/bin/python"
sudo -u www-data $PYTHON_PATH manage.py collectstatic --noinput --clear

echo "✅ Fichiers statiques collectés"
echo "   Fichiers CSS: $(find staticfiles -name "*.css" | wc -l)"
echo "   Fichiers JS: $(find staticfiles -name "*.js" | wc -l)"

echo ""
echo "🔧 3. Correction du rôle SuperAdmin..."
echo "   Solution: Mise à jour du rôle"

$PYTHON_PATH manage.py shell << 'EOF'
from accounts.models import User

# Corriger le SuperAdmin
superadmin = User.objects.get(username='SuperAdmin')
print(f"SuperAdmin actuel: {superadmin.role}")

# Mettre à jour le rôle
superadmin.role = 'SUPER_ADMIN'
superadmin.is_superuser = True
superadmin.is_staff = True
superadmin.save()

print(f"SuperAdmin corrigé: {superadmin.role}")
print(f"   is_superuser: {superadmin.is_superuser}")
print(f"   is_staff: {superadmin.is_staff}")

# Vérifier les permissions après correction
print(f"   peut_voir_tableau_bord: {superadmin.peut_voir_tableau_bord()}")
print(f"   peut_ajouter_nature_economique: {superadmin.peut_ajouter_nature_economique()}")
print(f"   peut_acceder_admin_django: {superadmin.peut_acceder_admin_django()}")

