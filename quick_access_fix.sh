#!/bin/bash
# quick_access_fix.sh - Correction rapide des accès

set -e

echo "🚀 Correction Rapide des Accès Utilisateur"
echo "======================================"

cd ~/e-FinTrack
source venv/bin/activate

echo "🔧 1. Vérification et correction du SuperAdmin..."
python manage.py shell << 'EOF'
from accounts.models import User

# Récupérer le SuperAdmin
try:
    superuser = User.objects.get(username='SuperAdmin')
    
    # Assurer tous les privilèges
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.is_active = True
    superuser.save()
    
    print("✅ SuperAdmin mis à jour avec tous les privilèges")
    print(f"   Username: {superuser.username}")
    print(f"   Superuser: {superuser.is_superuser}")
    print(f"   Staff: {superuser.is_staff}")
    print(f"   Actif: {superuser.is_active}")
    
except User.DoesNotExist:
    print("❌ SuperAdmin non trouvé, création...")
    superuser = User.objects.create_user(
        username='SuperAdmin',
        email='superadmin@efintrack.com',
        password='SuperAdmin123!',
        role='ADMIN'
    )
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.is_active = True
    superuser.save()
    print("✅ SuperAdmin créé avec tous les privilèges")
EOF

echo ""
echo "🌐 2. Test d'accès au dashboard..."
python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User
from django.urls import reverse

# Créer un client et se connecter
client = Client()
superuser = User.objects.get(username='SuperAdmin')

# Se connecter
login_success = client.login(username='SuperAdmin', password='SuperAdmin123!')
print(f"🔐 Connexion: {'✅ Succès' if login_success else '❌ Échec'}")

if login_success:
    # Tester l'accès à la racine
    response = client.get('/')
    print(f"📊 Accès à la racine (/): Status {response.status_code}")
    
    # Tester l'accès au dashboard
    try:
        dashboard_url = reverse('dashboard:dashboard')
        response = client.get(dashboard_url)
        print(f"📊 Accès au dashboard: Status {response.status_code}")
        print(f"   URL: {dashboard_url}")
    except:
        print("❌ URL dashboard non trouvée")
    
    # Tester les autres URLs principales
    urls_test = [
        ('Recettes', '/recettes/feuille/'),
        ('Dépenses', '/demandes/depenses/feuille/'),
        ('Natures', '/demandes/natures/'),
        ('Services', '/demandes/services/'),
        ('Banques', '/recettes/banques/'),
        ('Admin', '/admin/'),
    ]
    
    print("\n📋 Test des URLs principales:")
    for name, url in urls_test:
        response = client.get(url)
        status = "✅" if response.status_code in [200, 302] else "❌"
        print(f"   {status} {name}: {url} ({response.status_code})")

EOF

echo ""
echo "🔧 3. Vérification des URLs dans le projet..."
find . -name "urls.py" -type f | head -5 | while read file; do
    echo "📁 Fichier: $file"
    if grep -q "dashboard" "$file"; then
        echo "   ✅ Contient 'dashboard'"
    else
        echo "   ❌ Ne contient pas 'dashboard'"
    fi
done

echo ""
echo "🎯 4. Instructions de test manuel:"
echo "================================"
echo "1. Ouvrez votre navigateur en mode privé"
echo "2. Allez sur: http://187.77.171.80:8000/accounts/login/"
echo "3. Connectez-vous avec:"
echo "   Username: SuperAdmin"
echo "   Password: SuperAdmin123!"
echo "4. Notez où vous êtes redirigé"
echo ""
echo "🔍 Si vous êtes redirigé vers /demandes/natures/:"
echo "   - Le problème est dans LOGIN_REDIRECT_URL"
echo "   - Vérifiez settings.py ligne LOGIN_REDIRECT_URL"
echo ""
echo "🔍 Si vous voyez une erreur 403/404:"
echo "   - Le problème est dans les permissions"
echo "   - Vérifiez que is_superuser=True"
echo ""
echo "🔍 Si vous voyez le dashboard:"
echo "   - Tout est OK !"
echo "   - Le problème est peut-être dans le cache du navigateur"

echo ""
echo "🛠️  5. Correction de LOGIN_REDIRECT_URL si nécessaire..."
python manage.py shell << 'EOF'
from django.conf import settings

current_redirect = getattr(settings, 'LOGIN_REDIRECT_URL', 'Non défini')
print(f"📍 LOGIN_REDIRECT_URL actuel: {current_redirect}")

if current_redirect != '/' and 'dashboard' not in str(current_redirect):
    print("⚠️  LOGIN_REDIRECT_URL semble incorrect")
    print("🔧 Correction recommandée:")
    print("   LOGIN_REDIRECT_URL = '/'")
    print("   ou")
    print("   LOGIN_REDIRECT_URL = 'dashboard:dashboard'")
else:
    print("✅ LOGIN_REDIRECT_URL semble correct")
EOF

echo ""
echo "✅ Diagnostic rapide terminé !"
echo "🎊 Suivez les instructions pour tester l'accès"
