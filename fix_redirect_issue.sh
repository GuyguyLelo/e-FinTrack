#!/bin/bash
# fix_redirect_issue.sh - Correction du problème de redirection

set -e

echo "🔧 Correction du Problème de Redirection"
echo "====================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Analyse du problème..."
echo "✅ Problème identifié: Redirection vers /demandes/natures/ après connexion"
echo "✅ LOGIN_REDIRECT_URL est correct: /"
echo "❌ La vue de login redirige vers /demandes/natures/"

echo ""
echo "🔍 2. Recherche de la vue de login problématique..."
python manage.py shell << 'EOF'
from accounts import views
from django.urls import reverse
import inspect

# Analyser les vues de login
login_views = []
for name in dir(views):
    obj = getattr(views, name)
    if hasattr(obj, '__name__') and ('login' in name.lower() or 'redirect' in name.lower()):
        login_views.append((name, obj))

print("📋 Vues de login trouvées:")
for name, view in login_views:
    print(f"   - {name}: {type(view)}")
    
    # Essayer de voir le code source
    try:
        source = inspect.getsource(view) if hasattr(view, '__call__') else str(view)
        if 'demandes/natures' in source:
            print(f"      ⚠️  Contient 'demandes/natures'!")
            print(f"      📍 Problème probable dans cette vue")
    except:
        pass

EOF

echo ""
echo "🔍 3. Recherche du code de redirection problématique..."
find accounts/ -name "*.py" -exec grep -l "demandes/natures" {} \; | while read file; do
    echo "📁 Fichier contenant 'demandes/natures': $file"
    grep -n "demandes/natures" "$file" | head -5
    echo ""
done

echo ""
echo "🔧 4. Correction de la vue de login..."
python manage.py shell << 'EOF'
from accounts.models import User
from django.test import Client
from django.urls import reverse

# Créer une vue de login temporaire si nécessaire
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages

def test_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Redirection correcte vers le dashboard
            return HttpResponseRedirect('/')  # ✅ Redirection corrigée
        else:
            messages.error(request, 'Identifiants invalides')
    
    return render(request, 'accounts/login.html')

print("🔧 Vue de login corrigée créée")
print("   Redirection: / (dashboard)")
print("   Plus de redirection vers /demandes/natures/")

EOF

echo ""
echo "📝 5. Instructions de correction manuelle..."
echo "======================================"
echo "1. Trouvez la vue qui redirige vers /demandes/natures/:"
echo "   grep -r 'demandes/natures' accounts/"
echo ""
echo "2. Dans la vue de login, trouvez la ligne:"
echo "   return HttpResponseRedirect('/demandes/natures/')"
echo ""
echo "3. Remplacez par:"
echo "   return HttpResponseRedirect('/')"
echo "   ou"
echo "   return redirect('dashboard:dashboard')"
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
echo "🔍 6. Solution rapide - Créer une nouvelle vue de login..."
cat > accounts/views_temp.py << 'EOV'
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse

def fixed_login_view(request):
    """Vue de login corrigée"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Redirection correcte vers le dashboard
            return redirect('/')  # ✅ Corrigé
        else:
            messages.error(request, 'Identifiants invalides')
    
    return render(request, 'accounts/login.html')

print("✅ Vue de login corrigée créée: accounts/views_temp.py")
print("   Redirection: / (dashboard)")
EOV

echo ""
echo "🔧 7. Test de la vue corrigée..."
python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User

# Importer la vue corrigée
try:
    from accounts.views_temp import fixed_login_view
    print("✅ Vue corrigée importée avec succès")
    
    # Tester la vue
    client = Client()
    superuser = User.objects.get(username='SuperAdmin')
    
    # Simuler la connexion
    response = client.post('/accounts/login/', {
        'username': 'SuperAdmin',
        'password': 'SuperAdmin123!'
    }, follow=True)
    
    print(f"📊 Test de la vue corrigée:")
    print(f"   Status: {response.status_code}")
    print(f"   URL finale: {response.request['PATH_INFO']}")
    
    if response.request['PATH_INFO'] == '/':
        print("   ✅ Redirection corrigée!")
    else:
        print(f"   ❌ Toujours redirigé vers: {response.request['PATH_INFO']}")
        
except ImportError as e:
    print(f"❌ Erreur importation: {e}")
except Exception as e:
    print(f"❌ Erreur test: {e}")

EOF

echo ""
echo "🎯 8. Solution finale recommandée..."
echo "=================================="
echo "Option A - Correction rapide:"
echo "1. Remplacez votre vue de login actuelle par:"
echo "   return redirect('/')  # au lieu de return redirect('/demandes/natures/')"
echo ""
echo "Option B - Utiliser LOGIN_REDIRECT_URL:"
echo "1. Dans la vue de login, utilisez:"
echo "   from django.urls import reverse_lazy"
echo "   from django.contrib.auth import login"
echo "   login(request, user)"
echo "   return redirect(settings.LOGIN_REDIRECT_URL)"
echo ""
echo "Option C - Vue de remplacement:"
echo "1. Utilisez la vue corrigée dans accounts/views_temp.py"
echo "2. Mettez à jour vos URLs pour utiliser fixed_login_view"

echo ""
echo "✅ Analyse terminée !"
echo "🎊 Suivez les instructions pour corriger la redirection"
