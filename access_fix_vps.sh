#!/bin/bash
# access_fix_vps.sh - Script corrigé pour le chemin VPS

set -e

echo "🚀 Correction Accès Utilisateur (Chemin VPS corrigé)"
echo "================================================="

# Utiliser le bon chemin pour votre VPS
cd ~/e-FinTrack
source venv/bin/activate

echo "🔧 1. Vérification du SuperAdmin..."
python manage.py shell << 'EOF'
from accounts.models import User

try:
    superuser = User.objects.get(username='SuperAdmin')
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.is_active = True
    superuser.save()
    print("✅ SuperAdmin mis à jour avec tous les privilèges")
    print(f"   Username: {superuser.username}")
    print(f"   Superuser: {superuser.is_superuser}")
    print(f"   Staff: {superuser.is_staff}")
except User.DoesNotExist:
    print("❌ SuperAdmin non trouvé")
EOF

echo ""
echo "🌐 2. Test d'accès au dashboard..."
python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User

client = Client()
superuser = User.objects.get(username='SuperAdmin')
login_success = client.login(username='SuperAdmin', password='SuperAdmin123!')
print(f"🔐 Connexion: {'✅ Succès' if login_success else '❌ Échec'}")

if login_success:
    # Test des URLs principales
    urls_test = [
        ('Accueil', '/'),
        ('Dashboard', '/dashboard/'),
        ('Recettes', '/recettes/feuille/'),
        ('Dépenses', '/demandes/depenses/feuille/'),
        ('Natures', '/demandes/natures/'),
        ('Admin', '/admin/'),
    ]
    
    print("📋 Test des URLs:")
    for name, url in urls_test:
        response = client.get(url)
        status = "✅" if response.status_code in [200, 302] else "❌"
        print(f"   {status} {name}: {url} ({response.status_code})")
EOF

echo ""
echo "🔍 3. Vérification de LOGIN_REDIRECT_URL..."
python manage.py shell << 'EOF'
from django.conf import settings

redirect_url = getattr(settings, 'LOGIN_REDIRECT_URL', 'Non défini')
print(f"📍 LOGIN_REDIRECT_URL actuel: {redirect_url}")

if redirect_url == '/demandes/natures/' or redirect_url == 'demandes:nature_liste':
    print("⚠️  PROBLÈME TROUVÉ: Redirection vers les natures!")
    print("🔧 Solution: Changez LOGIN_REDIRECT_URL dans settings.py")
    print("   LOGIN_REDIRECT_URL = '/'")
    print("   ou")
    print("   LOGIN_REDIRECT_URL = 'dashboard:dashboard'")
elif redirect_url == '/' or 'dashboard' in str(redirect_url):
    print("✅ LOGIN_REDIRECT_URL semble correct")
else:
    print(f"ℹ️  LOGIN_REDIRECT_URL: {redirect_url}")
EOF

echo ""
echo "📝 4. Instructions de correction manuelle..."
echo "========================================"
echo "Si LOGIN_REDIRECT_URL est incorrect:"
echo "1. Éditez settings.py:"
echo "   nano efinance_daf/settings.py"
echo ""
echo "2. Cherchez la ligne LOGIN_REDIRECT_URL"
echo "3. Remplacez par:"
echo "   LOGIN_REDIRECT_URL = '/'"
echo ""
echo "4. Redémarrez les services:"
echo "   sudo systemctl restart gunicorn"
echo "   sudo systemctl restart nginx"
echo ""
echo "5. Testez la connexion:"
echo "   http://187.77.171.80:8000/accounts/login/"
echo "   Username: SuperAdmin"
echo "   Password: SuperAdmin123!"

echo ""
echo "✅ Diagnostic terminé !"
echo "🎊 Suivez les instructions pour corriger l'accès"
