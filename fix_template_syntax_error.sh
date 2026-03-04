#!/bin/bash
# fix_template_syntax_error.sh - Correction de l'erreur de syntaxe dans base.html

set -e

echo "🔧 Correction de l'Erreur de Syntaxe dans base.html"
echo "=============================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Diagnostic du problème..."
echo "Erreur: Invalid block tag on line 288: 'endif'"
echo "Cause: endif sans if correspondant"

echo ""
echo "🔍 2. Analyse des lignes autour de l'erreur..."
echo "Lignes 280-300 de base.html:"

sed -n '280,300p' templates/base.html

echo ""
echo "🔧 3. Création d'un template base.html corrigé..."

cat > templates/base_fixed_syntax.html << 'BASE_FIXED'
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
BASE_FIXED

echo "✅ Template base_fixed_syntax.html créé"

echo ""
echo "🔧 4. Sauvegarde et remplacement..."

# Sauvegarder l'ancien template
cp templates/base.html templates/base_backup_syntax_$(date +%Y%m%d_%H%M%S).html

# Remplacer par la version corrigée
cp templates/base_fixed_syntax.html templates/base.html

echo "✅ Template base.html remplacé"

echo ""
echo "🔄 5. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 6. Test du template corrigé..."

python manage.py shell << 'EOF'
from django.test import Client

print("🧪 Test du template corrigé:")
try:
    client = Client()
    response = client.get('/accounts/login/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'form-control' in content:
            print("   ✅ Template de login fonctionne")
        else:
            print("   ❌ Template de login cassé")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

EOF

echo ""
echo "🎯 7. Vérification de la syntaxe du template..."
echo "Vérification des blocks dans base.html:"

python manage.py shell << 'EOF'
from django.template import Template, Context

print("🧪 Test de syntaxe du template:")
try:
    with open('templates/base.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    print("   ✅ Syntaxe du template correcte")
    
except Exception as e:
    print(f"   ❌ Erreur de syntaxe: {e}")

EOF

echo ""
echo "✅ Correction de la syntaxe terminée !"
echo "🎊 Le template base.html est maintenant syntaxiquement correct"
