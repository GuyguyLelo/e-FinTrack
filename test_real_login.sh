#!/bin/bash
# test_real_login.sh - Test de connexion réel

set -e

echo "🧪 Test de Connexion Réel"
echo "========================"

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Simulation de connexion complète..."
python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User
from django.urls import reverse

# Créer un client
client = Client()

# 1. Accéder à la page de login
print("📝 1. Accès à la page de login...")
response = client.get('/accounts/login/')
print(f"   Status: {response.status_code}")

# 2. Se connecter
print("🔐 2. Tentative de connexion...")
login_data = {
    'username': 'SuperAdmin',
    'password': 'SuperAdmin123!'
}
response = client.post('/accounts/login/', login_data, follow=True)
print(f"   Status final: {response.status_code}")
print(f"   URL finale: {response.request['PATH_INFO']}")
print(f"   Redirections: {len(response.redirect_chain)}")

# 3. Vérifier la session
print("📊 3. État de la session:")
print(f"   Utilisateur connecté: {response.context['user'].is_authenticated}")
print(f"   Username: {response.context['user'].username}")
print(f"   Superuser: {response.context['user'].is_superuser}")

# 4. Vérifier le contenu de la page
if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Chercher des indices sur la page
    if 'dashboard' in content.lower():
        print("   ✅ Page dashboard détectée")
    elif 'nature' in content.lower():
        print("   ⚠️  Page natures détectée")
    elif 'recette' in content.lower():
        print("   ✅ Page recettes détectée")
    else:
        print("   ❓ Page non identifiée")
        
    # Afficher les premiers liens
    import re
    links = re.findall(r'href="([^"]+)"', content)[:5]
    print("   Liens trouvés:")
    for link in links:
        print(f"      - {link}")

EOF

echo ""
echo "🌐 2. Test avec un vrai navigateur (instructions):"
echo "================================================="
echo "1. Ouvrez un onglet PRIVÉ dans votre navigateur"
echo "2. Allez sur: http://187.77.171.80:8000/accounts/login/"
echo "3. Connectez-vous avec:"
echo "   Username: SuperAdmin"
echo "   Password: SuperAdmin123!"
echo "4. Regardez attentivement où vous êtes redirigé"
echo "5. Notez l'URL exacte dans la barre d'adresse"
echo ""
echo "🔍 Si vous êtes redirigé vers /demandes/natures/:"
echo "   - Le problème est dans les views.py"
echo "   - Vérifiez la vue de redirection après login"
echo ""
echo "🔍 Si vous voyez une erreur 403:"
echo "   - Le problème est dans les permissions"
echo "   - Vérifiez les décorateurs @login_required"
echo ""
echo "🔍 Si vous voyez le dashboard:"
echo "   - Tout est OK !"
echo "   - Le problème était peut-être le cache"

echo ""
echo "🔧 3. Vérification des views de redirection..."
python manage.py shell << 'EOF'
from django.urls import reverse
from django.conf import settings

# Vérifier les URLs de login
try:
    login_url = reverse('accounts:login')
    print(f"📍 URL login: {login_url}")
except:
    print("❌ URL login non trouvée")

# Vérifier les settings
print(f"📍 LOGIN_URL: {getattr(settings, 'LOGIN_URL', 'Non défini')}")
print(f"📍 LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', 'Non défini')}")

EOF

echo ""
echo "🎯 4. Solution si problème persiste..."
echo "===================================="
echo "Si vous êtes toujours redirigé vers /demandes/natures/:"
echo ""
echo "1. Vérifiez la vue de login dans accounts/views.py:"
echo "   grep -A 10 -B 5 'redirect' accounts/views.py"
echo ""
echo "2. Vérifiez les middlewares:"
echo "   grep -A 5 -B 5 'auth' efinance_daf/settings.py"
echo ""
echo "3. Videz le cache du navigateur:"
echo "   Ctrl + Shift + R (rechargement dur)"
echo ""
echo "4. Testez avec un autre navigateur"

echo ""
echo "✅ Test terminé !"
echo "🎊 Suivez les instructions pour tester la connexion réelle"
