#!/bin/bash
# diagnose_500_error.sh - Diagnostic rapide de l'erreur 500

set -e

echo "🚨 Diagnostic de l'Erreur 500"
echo "============================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Vérification des fichiers templates..."
echo "Vérification des fichiers créés:"

if [ -f "templates/base.html" ]; then
    echo "✅ templates/base.html existe"
    echo "   Taille: $(wc -l < templates/base.html) lignes"
else
    echo "❌ templates/base.html manquant"
fi

if [ -f "templates/accounts/login.html" ]; then
    echo "✅ templates/accounts/login.html existe"
    echo "   Taille: $(wc -l < templates/accounts/login.html) lignes"
else
    echo "❌ templates/accounts/login.html manquant"
fi

echo ""
echo "🔍 2. Vérification des permissions..."
ls -la templates/base.html
ls -la templates/accounts/login.html

echo ""
echo "🔍 3. Test de syntaxe Django..."
python manage.py check --deploy

echo ""
echo "🔍 4. Test de la vue de login..."
python manage.py shell << 'EOF'
from django.urls import reverse
from django.test import Client

print("🧪 Test de la vue de login:")
try:
    url = reverse('accounts:login')
    print(f"   ✅ URL login trouvée: {url}")
    
    client = Client()
    response = client.get(url)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        print("   ✅ Template de login accessible")
    elif response.status_code == 500:
        print("   ❌ Erreur 500 - problème de template ou vue")
    else:
        print(f"   ⚠️  Status inattendu: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

EOF

echo ""
echo "🔍 5. Vérification des logs Django..."
echo "Recherche des erreurs récentes..."

if [ -f "django.log" ]; then
    echo "📋 Dernières lignes de django.log:"
    tail -20 django.log
else
    echo "📋 Logs Django non trouvés"
fi

echo ""
echo "🔍 6. Vérification des logs Gunicorn..."
echo "Recherche des erreurs récentes..."

sudo journalctl -u gunicorn --no-pager -n 20 | grep -i error || echo "Pas d'erreurs récentes dans Gunicorn"

echo ""
echo "🔍 7. Vérification des logs Nginx..."
echo "Recherche des erreurs récentes..."

sudo journalctl -u nginx --no-pager -n 20 | grep -i error || echo "Pas d'erreurs récentes dans Nginx"

echo ""
echo "🔧 8. Correction rapide si problème de template..."
echo "Création d'un template de login ultra-simple..."

cat > templates/accounts/login_emergency.html << 'EMERGENCY_LOGIN'
{% load static %}
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion - e-Finance DAF</title>
    <link href="{% static 'css/bootstrap.min.css' %}" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/bootstrap-icons.css' %}">
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .navbar { background: #1a3a5f; padding: 1rem; }
        .navbar-brand { color: #d4af37; font-weight: bold; }
        .container { margin-top: 2rem; }
        .card { border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card-header { background: #1a3a5f; color: white; padding: 1rem; }
        .card-body { padding: 2rem; }
        .form-control { margin-bottom: 1rem; }
        .btn { background: #1a3a5f; color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">e-FinTrack</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h4>Connexion</h4>
                    </div>
                    <div class="card-body">
                        <form method="post">
                            {% csrf_token %}
                            <div class="form-group">
                                <label>Nom d'utilisateur</label>
                                <input type="text" name="username" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label>Mot de passe</label>
                                <input type="password" name="password" class="form-control" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Se connecter</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
EMERGENCY_LOGIN

echo "✅ Template d'urgence créé"

echo ""
echo "🔧 9. Création d'une vue de login d'urgence..."

cat > accounts/views_emergency.py << 'EMERGENCY_VIEWS'
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

def emergency_login(request):
    """Vue de login d'urgence"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Redirection selon le rôle
            if user.username == 'AdminDaf':
                return HttpResponseRedirect('/demandes/natures/')
            elif user.username == 'SuperAdmin':
                return HttpResponseRedirect('/dashboard/')
            else:
                return HttpResponseRedirect('/dashboard/')
        else:
            messages.error(request, 'Identifiants invalides')
    
    return render(request, 'accounts/login_emergency.html')

print("✅ Vue d'urgence créée")
EMERGENCY_VIEWS

echo ""
echo "🔧 10. Mise à jour des URLs d'urgence..."
echo "Ajout d'une URL d'urgence dans accounts/urls.py..."

# Vérifier si le fichier URLs existe
if [ -f "accounts/urls.py" ]; then
    echo "📋 Ajout de l'URL d'urgence..."
    
    # Créer une sauvegarde
    cp accounts/urls.py accounts/urls_backup_$(date +%Y%m%d_%H%M%S).py
    
    # Ajouter l'URL d'urgence
    cat >> accounts/urls.py << 'URL_ADD'

# URL d'urgence pour le login
from django.urls import path
from . import views_emergency

urlpatterns += [
    path('login-emergency/', views_emergency.emergency_login, name='login_emergency'),
]

URL_ADD

    echo "✅ URL d'urgence ajoutée"
else
    echo "❌ accounts/urls.py non trouvé"
fi

echo ""
echo "🔄 11. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 12. Test d'urgence..."
echo "Test du template d'urgence:"

python manage.py shell << 'EOF'
from django.test import Client

print("🧪 Test d'urgence:")
try:
    client = Client()
    response = client.get('/accounts/login-emergency/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'form-control' in content:
            print("   ✅ Template d'urgence fonctionnel")
        else:
            print("   ❌ Template d'urgence cassé")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

EOF

echo ""
echo "🎯 13. Instructions finales..."
echo "========================="
echo "✅ Diagnostic terminé"
echo ""
echo "🌐 URL de test d'urgence:"
echo "   http://187.77.171.80:8000/accounts/login-emergency/"
echo ""
echo "🔧 Si l'erreur 500 persiste:"
echo "1. Utilisez l'URL d'urgence ci-dessus"
echo "2. Vérifiez les logs:"
echo "   - Django: python manage.py runserver --settings=efinance_daf.settings"
echo "   - Gunicorn: sudo journalctl -u gunicorn -f"
echo "   - Nginx: sudo journalctl -u nginx -f"
echo ""
echo "3. Vérifiez les permissions:"
echo "   - Templates: chmod 644 templates/*.html"
echo "   - Vues: chmod 644 accounts/*.py"
echo ""
echo "4. Vérifiez la configuration:"
echo "   - python manage.py check --deploy"
echo "   - python manage.py collectstatic --noinput"

echo ""
echo "✅ Diagnostic d'urgence terminé !"
echo "🎊 Utilisez l'URL d'urgence si nécessaire"
