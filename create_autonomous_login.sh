#!/bin/bash
# create_autonomous_login.sh - Création d'un login autonome

set -e

echo "🔧 Création d'un Login Autonome"
echo "=========================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Diagnostic du problème..."
echo "Erreur: 'block' tag with name 'content' appears more than once"
echo "Solution: Template de login autonome (pas d'héritage)"

echo ""
echo "🔧 2. Création d'un template de login autonome..."

cat > templates/accounts/login_autonomous.html << 'LOGIN_AUTONOMOUS'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion - e-Finance DAF</title>
    
    <!-- Bootstrap 5 CSS -->
    {% load static %}
    <link href="{% static 'css/bootstrap.min.css' %}" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="{% static 'css/bootstrap-icons.css' %}">
    
    <style>
        :root {
            --dgrad-bleu: #1a3a5f;
            --dgrad-dore: #d4af37;
            --dgrad-blanc: #ffffff;
            --dgrad-gris-clair: #f5f5f5;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--dgrad-gris-clair);
        }
        
        .navbar {
            background: linear-gradient(135deg, var(--dgrad-bleu) 0%, #2a4a6f 100%);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .navbar-brand {
            font-weight: bold;
            color: var(--dgrad-dore) !important;
            font-size: 1.3rem;
        }
        
        .card {
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .card-header {
            background: linear-gradient(135deg, var(--dgrad-bleu) 0%, #2a4a6f 100%);
            color: white;
            font-weight: bold;
            border-radius: 8px 8px 0 0 !important;
        }
        
        .btn-primary {
            background-color: var(--dgrad-bleu);
            border-color: var(--dgrad-bleu);
        }
        
        .btn-primary:hover {
            background-color: #2a4a6f;
            border-color: #2a4a6f;
        }
        
        .alert {
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="bi bi-building"></i> e-FinTrack
            </a>
        </div>
    </nav>
    
    <!-- Formulaire de connexion -->
    <div class="container">
        <div class="row justify-content-center mt-5">
            <div class="col-md-4 col-lg-3">
                <div class="text-center mb-4">
                    <img src="{% static 'img/logo_e-FinTrack.png' %}" alt="e-FinTrack" class="img-fluid" style="max-height: 80px;">
                </div>
                <div class="card">
                    <div class="card-header text-center">
                        <h4><i class="bi bi-box-arrow-in-right"></i> Connexion</h4>
                    </div>
                    <div class="card-body">
                        <form method="post">
                            {% csrf_token %}
                            
                            {% if session_expired %}
                            <div class="alert alert-warning">
                                <i class="bi bi-exclamation-triangle"></i>
                                <strong>Session expirée.</strong> Votre session a été interrompue. Veuillez vous reconnecter.
                            </div>
                            {% endif %}
                            
                            {% if form.errors %}
                            <div class="alert alert-danger">
                                <strong>Erreur de connexion.</strong> Veuillez vérifier vos identifiants.
                            </div>
                            {% endif %}
                            
                            <div class="mb-3">
                                <label for="{{ form.username.id_for_label }}" class="form-label">
                                    <i class="bi bi-person me-1"></i> Nom d'utilisateur
                                </label>
                                <input type="text" class="form-control" name="{{ form.username.name }}" id="{{ form.username.id_for_label }}" required autofocus>
                            </div>
                            
                            <div class="mb-3">
                                <label for="{{ form.password.id_for_label }}" class="form-label">
                                    <i class="bi bi-lock me-1"></i> Mot de passe
                                </label>
                                <input type="password" class="form-control" name="{{ form.password.name }}" id="{{ form.password.id_for_label }}" required>
                            </div>
                            
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">
                                    <i class="bi bi-box-arrow-in-right"></i> Se connecter
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <div class="text-center mt-3">
                    <p class="text-muted">
                        <i class="bi bi-shield-check"></i> Système de gestion financière e-FinTrack
                    </p>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap 5 JS -->
    <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
</body>
</html>
LOGIN_AUTONOMOUS

echo "✅ Template login_autonomous.html créé"

echo ""
echo "🔧 3. Remplacement du template de login..."

# Sauvegarder l'ancien template
cp templates/accounts/login.html templates/accounts/login_backup_$(date +%Y%m%d_%H%M%S).html

# Remplacer par la version autonome
cp templates/accounts/login_autonomous.html templates/accounts/login.html

echo "✅ Template de login remplacé"

echo ""
echo "🌐 4. Test du login autonome..."

python manage.py shell << 'EOF'
from django.test import Client

print("🧪 Test du login autonome:")
try:
    client = Client()
    response = client.get('/accounts/login/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'form-control' in content and 'btn-primary' in content:
            print("   ✅ Page de login autonome fonctionne")
        else:
            print("   ❌ Page de login autonome cassée")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

EOF

echo ""
echo "🌐 5. Test de la vue de login..."

python manage.py shell << 'EOF'
from django.test import Client
from django.urls import reverse

print("🧪 Test de la vue de login:")
try:
    client = Client()
    
    # Test de la vue
    response = client.post(reverse('accounts:login'), {
        'username': 'AdminDaf',
        'password': 'AdminDaf123!'
    })
    
    print(f"   Status POST: {response.status_code}")
    
    if response.status_code == 302:
        print("   ✅ Redirection après connexion fonctionne")
        print(f"   📋 Redirection vers: {response.url}")
    elif response.status_code == 200:
        print("   ❌ Connexion échouée - reste sur la page")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

EOF

echo ""
echo "✅ Login autonome créé et testé !"
echo "🎊 Testez maintenant en local avec:"
echo "   python manage.py runserver 127.0.0.1:8000"
echo ""
echo "🌐 URL de test:"
echo "   http://127.0.0.1:8000/accounts/login/"
