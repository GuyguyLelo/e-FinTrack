#!/bin/bash
# fix_user_access.sh - Diagnostic et correction des accès utilisateur

set -e

echo "🔍 Diagnostic des Accès Utilisateur"
echo "=================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "👤 1. Vérification du SuperAdmin..."
python manage.py shell << EOF
from accounts.models import User
from django.contrib.auth import authenticate

# Vérifier le SuperAdmin
try:
    superuser = User.objects.get(username='SuperAdmin')
    print(f"✅ SuperAdmin trouvé: {superuser.username}")
    print(f"   Email: {superuser.email}")
    print(f"   Role: {superuser.role}")
    print(f"   Superuser: {superuser.is_superuser}")
    print(f"   Staff: {superuser.is_staff}")
    print(f"   Actif: {superuser.is_active}")
    
    # Tester l'authentification
    auth_test = authenticate(username='SuperAdmin', password='SuperAdmin123!')
    print(f"   Authentification: {'✅ Succès' if auth_test else '❌ Échec'}")
    
except User.DoesNotExist:
    print("❌ SuperAdmin non trouvé")
EOF

echo ""
echo "🌐 2. Vérification des URLs et permissions..."
python manage.py shell << EOF
from django.urls import reverse
from django.contrib.auth.models import Permission
from accounts.models import User

# Vérifier les URLs principales
try:
    superuser = User.objects.get(username='SuperAdmin')
    
    # Tester les URLs principales
    urls_to_test = [
        ('Dashboard', 'dashboard:dashboard'),
        ('Recettes', 'recettes:recette_feuille_liste'),
        ('Dépenses', 'demandes:depense_feuille_liste'),
        ('Natures', 'demandes:nature_liste'),
        ('Services', 'demandes:service_liste'),
        ('Banques', 'recettes:banque_liste'),
        ('Clotures', 'clotures:cloture_liste'),
        ('Admin Django', 'admin:index'),
    ]
    
    print("📋 URLs disponibles:")
    for name, url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"   ✅ {name}: {url}")
        except:
            print(f"   ❌ {name}: Non trouvée")
            
except Exception as e:
    print(f"❌ Erreur: {e}")
EOF

echo ""
echo "🔧 3. Vérification des permissions..."
python manage.py shell << EOF
from accounts.models import User
from django.contrib.auth.models import Permission

try:
    superuser = User.objects.get(username='SuperAdmin')
    
    # Vérifier les permissions
    print("📊 Permissions du SuperAdmin:")
    
    # Permissions Django standards
    all_permissions = Permission.objects.all()
    user_permissions = superuser.user_permissions.all()
    
    print(f"   Permissions utilisateur: {user_permissions.count()}")
    print(f"   Permissions totales: {all_permissions.count()}")
    
    # Comme c'est un superuser, il devrait avoir toutes les permissions
    if superuser.is_superuser:
        print("   ✅ Superuser: Toutes les permissions automatiques")
    else:
        print("   ❌ Pas superuser: Permissions limitées")
        
except Exception as e:
    print(f"❌ Erreur permissions: {e}")
EOF

echo ""
echo "🏠 4. Vérification de la page d'accueil..."
python manage.py shell << EOF
from django.urls import reverse
from django.test import Client

# Simuler l'accès au dashboard
client = Client()
superuser = User.objects.get(username='SuperAdmin')
client.force_login(superuser)

# Tester l'accès au dashboard
try:
    response = client.get('/')
    print(f"📊 Accès à la page d'accueil (/):")
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirection vers: {response.get('Location', 'Inconnue')}")
    elif response.status_code == 200:
        print("   ✅ Page accessible")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        
    # Tester l'accès au dashboard nommé
    try:
        dashboard_url = reverse('dashboard:dashboard')
        response = client.get(dashboard_url)
        print(f"📊 Accès au dashboard nommé: {dashboard_url}")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur dashboard: {e}")
        
except Exception as e:
    print(f"❌ Erreur test: {e}")
EOF

echo ""
echo "🔍 5. Vérification des middlewares et settings..."
python manage.py shell << EOF
from django.conf import settings

print("⚙️  Configuration importante:")
print(f"   LOGIN_URL: {getattr(settings, 'LOGIN_URL', 'Non défini')}")
print(f"   LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', 'Non défini')}")
print(f"   DEBUG: {getattr(settings, 'DEBUG', 'Non défini')}")
print(f"   ALLOWED_HOSTS: {getattr(settings, 'ALLOWED_HOSTS', 'Non défini')}")

# Vérifier les middlewares
middlewares = getattr(settings, 'MIDDLEWARE', [])
print("📋 Middlewares:")
for i, middleware in enumerate(middlewares):
    status = "✅" if 'auth' in middleware or 'session' in middleware else "📝"
    print(f"   {i+1}. {status} {middleware}")
EOF

echo ""
echo "🛠️  6. Correction des problèmes courants..."

# Vérifier si l'utilisateur est bien connecté
echo "🔧 Test de connexion et de redirection..."
python manage.py shell << EOF
from django.test import Client
from accounts.models import User
from django.urls import reverse

# Créer un client de test
client = Client()

# 1. Tester la connexion
login_data = {
    'username': 'SuperAdmin',
    'password': 'SuperAdmin123!'
}

response = client.post('/accounts/login/', login_data, follow=True)
print(f"📊 Test de connexion:")
print(f"   Status final: {response.status_code}")
print(f"   URL finale: {response.request['PATH_INFO']}")

# 2. Tester l'accès après connexion
if response.status_code == 200:
    print("   ✅ Connexion réussie")
    
    # Tester l'accès au dashboard
    try:
        dashboard_response = client.get('/')
        print(f"📊 Accès dashboard après connexion:")
        print(f"   Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("   ✅ Dashboard accessible")
        elif dashboard_response.status_code == 302:
            print(f"   ⚠️  Redirection: {dashboard_response.get('Location', 'Inconnue')}")
        else:
            print(f"   ❌ Erreur: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur dashboard: {e}")
else:
    print("   ❌ Connexion échouée")

# 3. Vérifier les sessions
print(f"📊 Session après connexion: {client.session.items()}")

EOF

echo ""
echo "🎯 7. Solutions recommandées:"
echo "=========================="
echo "1. Si redirection vers /demandes/natures/:"
echo "   - Vérifiez LOGIN_REDIRECT_URL dans settings.py"
echo "   - Devrait être '/' ou 'dashboard:dashboard'"
echo ""
echo "2. Si problème de permissions:"
echo "   - Vérifiez que SuperAdmin est bien is_superuser=True"
echo "   - Vérifiez que SuperAdmin est bien is_staff=True"
echo ""
echo "3. Si problème d'URL:"
echo "   - Vérifiez les patterns d'URL dans urls.py"
echo "   - Assurez-vous que le dashboard est bien défini"
echo ""
echo "4. Test manuel recommandé:"
echo "   - Ouvrez: http://187.77.171.80:8000/accounts/login/"
echo "   - Connectez-vous avec SuperAdmin / SuperAdmin123!"
echo "   - Regardez où vous êtes redirigé"

echo ""
echo "✅ Diagnostic terminé !"
echo "🎊 Suivez les recommandations pour corriger le problème"
