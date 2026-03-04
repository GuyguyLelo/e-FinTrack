#!/bin/bash
# fix_login_and_menu.sh - Correction du login et du menu

set -e

echo "🔧 Correction du Login et du Menu"
echo "==============================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Vérification du template de login..."
if [ ! -f "templates/accounts/login.html" ]; then
    echo "❌ Template de login non trouvé"
    exit 1
fi

echo "✅ Template de login trouvé"

echo ""
echo "🔧 2. Création d'un template de login corrigé..."

cat > templates/accounts/login_fixed.html << 'LOGIN_TEMPLATE'
{% extends 'base.html' %}
{% load static %}

{% block title %}Connexion - e-Finance DAF{% endblock %}

{% block content %}
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
                        <label for="{{ form.username.id_for_label }}" class="form-label"><i class="bi bi-person me-1"></i> Nom d'utilisateur</label>
                        <input type="text" class="form-control" name="{{ form.username.name }}" id="{{ form.username.id_for_label }}" required autofocus>
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.password.id_for_label }}" class="form-label"><i class="bi bi-lock me-1"></i> Mot de passe</label>
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
{% endblock %}
LOGIN_TEMPLATE

echo "✅ Template de login corrigé créé"

echo ""
echo "🔧 3. Création d'un template base corrigé..."

cat > templates/base_simple.html << 'BASE_TEMPLATE'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}e-Finance Track{% endblock %}</title>
    
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
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1030;
        }
        body { padding-top: 56px; }
        
        .navbar-brand {
            font-weight: bold;
            color: var(--dgrad-dore) !important;
            font-size: 1.3rem;
        }
        
        .sidebar {
            min-height: calc(100vh - 56px);
            position: sticky;
            top: 56px;
            background-color: var(--dgrad-bleu);
            padding: 20px 0;
            color: white;
        }
        
        .sidebar .nav-link {
            color: rgba(255,255,255,0.8);
            padding: 12px 20px;
            margin: 5px 0;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        .sidebar .nav-link:hover,
        .sidebar .nav-link.active {
            background-color: rgba(212, 175, 55, 0.2);
            color: var(--dgrad-dore);
            transform: translateX(5px);
        }
        
        .sidebar .nav-link i {
            margin-right: 10px;
            width: 20px;
        }
        
        .main-content {
            padding: 20px;
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
        
        .btn-success {
            background-color: #28a745;
        }
        
        .btn-warning {
            background-color: var(--dgrad-dore);
            border-color: var(--dgrad-dore);
            color: #000;
        }
        
        .stat-card {
            border-left: 4px solid var(--dgrad-dore);
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--dgrad-bleu);
        }
        
        .badge-dgrad {
            background-color: var(--dgrad-dore);
            color: #000;
        }
        
        .table {
            background-color: white;
        }
        
        .table th {
            background-color: var(--dgrad-bleu);
            color: white;
        }
    </style>
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="bi bi-building"></i> e-FinTrack
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="bi bi-person-circle"></i> {{ user.get_full_name|default:user.username }}
                            <span class="badge badge-dgrad ms-2">{{ user.get_role_display }}</span>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="{% url 'accounts:profile' %}">
                                <i class="bi bi-person"></i> Mon profil
                            </a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li>
                                <form method="post" action="{% url 'accounts:logout' %}" style="display: inline;">
                                    {% csrf_token %}
                                    <button type="submit" class="dropdown-item" style="border: none; background: none; width: 100%; text-align: left;">
                                        <i class="bi bi-box-arrow-right"></i> Déconnexion
                                    </button>
                                </form>
                            </li>
                        </ul>
                    </li>
                    {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'accounts:login' %}">
                            <i class="bi bi-box-arrow-in-right"></i> Connexion
                        </a>
                    </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            {% if user.is_authenticated %}
            <!-- Sidebar -->
            <div class="col-md-2 sidebar">
                <nav class="nav flex-column">
                    <!-- Menu pour AdminDaf -->
                    {% if user.username == 'AdminDaf' %}
                    <a class="nav-link" href="{% url 'demandes:nature_liste' %}">
                        <i class="bi bi-diagram-3"></i> Natures Économiques
                    </a>
                    {% endif %}
                    
                    <!-- Menu pour les autres utilisateurs -->
                    {% if user.username != 'AdminDaf' %}
                    <a class="nav-link" href="{% url 'tableau_bord_feuilles:tableau_bord_feuilles' %}">
                        <i class="bi bi-speedometer2"></i> Tableau de bord
                    </a>
                    
                    <!-- Natures pour tout le monde sauf SuperAdmin -->
                    {% if user.username != 'SuperAdmin' %}
                    <a class="nav-link" href="{% url 'demandes:nature_liste' %}">
                        <i class="bi bi-diagram-3"></i> Natures Économiques
                    </a>
                    {% endif %}
                    
                    <a class="nav-link" href="{% url 'demandes:depense_feuille_liste' %}">
                        <i class="bi bi-journal-spreadsheet"></i> Gestion dépenses
                    </a>
                    
                    <a class="nav-link" href="{% url 'recettes:feuille_liste' %}">
                        <i class="bi bi-journal-spreadsheet"></i> Gestion recettes
                    </a>
                    
                    <!-- Clôtures pour DG et CD_FINANCE -->
                    {% if user.role == 'DG' or user.role == 'CD_FINANCE' %}
                    <a class="nav-link" href="{% url 'clotures:periode_actuelle' %}">
                        <i class="bi bi-lock"></i> Clôtures
                    </a>
                    {% endif %}
                    
                    <!-- Admin Django pour SuperAdmin -->
                    {% if user.is_superuser %}
                    <hr style="border-color: rgba(255,255,255,0.2);">
                    <a class="nav-link" href="/admin/">
                        <i class="bi bi-gear"></i> Administration Django
                    </a>
                    {% endif %}
                    {% endif %}
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="col-md-10 main-content">
                <!-- Messages -->
                {% if messages %}
                <div class="messages">
                    {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% block content %}{% endblock %}
            </div>
            {% else %}
            <!-- Page de connexion (pas de sidebar) -->
            <div class="col-12">
                {% block content %}{% endblock %}
            </div>
            {% endif %}
        </div>
    </div>

    <!-- jQuery (nécessaire pour Bootstrap) -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <!-- Bootstrap 5 JS -->
    <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
    <!-- Chart.js -->
    <script src="{% static 'js/chart.umd.min.js' %}"></script>
    
    <!-- Script de redirection simple -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            {% if user.is_authenticated %}
            var username = "{{ user.username }}";
            var currentPath = "{{ request.path }}";
            
            console.log("Redirection check:", {
                path: currentPath,
                username: username,
                userRole: "{{ user.role }}"
            });
            
            // AdminDaf : redirigé vers les natures depuis la racine
            if (username === 'AdminDaf' && currentPath === '/') {
                console.log("Redirection AdminDaf vers natures");
                window.location.href = '/demandes/natures/';
            }
            
            // SuperAdmin : redirigé loin des natures
            if (username === 'SuperAdmin' && currentPath === '/demandes/natures/') {
                console.log("Redirection SuperAdmin loin des natures");
                window.location.href = '/dashboard/';
            }
            {% endif %}
        });
    </script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
BASE_TEMPLATE

echo "✅ Template base_simple.html créé"

echo ""
echo "🔧 4. Sauvegarde et remplacement..."

# Sauvegarder les anciens templates
cp templates/base.html templates/base_backup_$(date +%Y%m%d_%H%M%S).html
cp templates/accounts/login.html templates/accounts/login_backup_$(date +%Y%m%d_%H%M%S).html

# Remplacer les templates
cp templates/base_simple.html templates/base.html
cp templates/accounts/login_fixed.html templates/accounts/login.html

echo "✅ Templates remplacés"
echo "📋 Anciens templates sauvegardés avec timestamp"

echo ""
echo "🔄 5. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 6. Test des templates..."

python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User
from django.urls import reverse

print("🧪 Test des templates corrigés:")
print("=" * 50)

# Test template de login
print("\n1. Test template de login:")
client = Client()
response = client.get('/accounts/login/')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode('utf-8')
    if 'form-control' in content and 'btn-primary' in content:
        print("   ✅ Template de login correct")
    else:
        print("   ❌ Template de login incorrect")
else:
    print("   ❌ Erreur template de login")

# Test template base avec utilisateur
print("\n2. Test template base avec utilisateur:")
admin_daf = User.objects.get(username='AdminDaf')
client.force_login(admin_daf)

response = client.get('/')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode('utf-8')
    if 'sidebar' in content and 'nav-link' in content:
        print("   ✅ Template base correct")
        if 'Natures Économiques' in content:
            print("   ✅ Menu AdminDaf présent")
        else:
            print("   ❌ Menu AdminDaf absent")
    else:
        print("   ❌ Template base incorrect")
else:
    print("   ❌ Erreur template base")

# Test SuperAdmin
print("\n3. Test SuperAdmin:")
superadmin = User.objects.get(username='SuperAdmin')
client.force_login(superadmin)

response = client.get('/')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode('utf-8')
    if 'Administration Django' in content:
        print("   ✅ Menu SuperAdmin présent")
    else:
        print("   ❌ Menu SuperAdmin absent")
else:
    print("   ❌ Erreur SuperAdmin")

EOF

echo ""
echo "🎯 7. Instructions de test manuel..."
echo "======================================"
echo "1. Vider le cache du navigateur:"
echo "   Ctrl + Shift + R (rechargement dur)"
echo ""
echo "2. Tester AdminDaf:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: AdminDaf / AdminDaf123!"
echo "   Résultat attendu: Redirection vers /demandes/natures/"
echo "   Menu attendu: Uniquement 'Natures Économiques'"
echo ""
echo "3. Tester SuperAdmin:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: SuperAdmin / SuperAdmin123!"
echo "   Résultat attendu: Accès au dashboard"
echo "   Menu attendu: Tableau de bord, recettes, dépenses, admin Django"
echo ""
echo "4. Vérifier l'admin Django:"
echo "   URL: http://187.77.171.80:8000/admin/"
echo "   Login: SuperAdmin / SuperAdmin123!"
echo "   Résultat attendu: Design correct de l'admin Django"

echo ""
echo "✅ Correction terminée !"
echo "🎊 Testez maintenant les connexions"
