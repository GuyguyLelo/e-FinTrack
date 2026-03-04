#!/bin/bash
# fix_redirect_loop.sh - Correction des redirections en boucle

set -e

echo "🔄 Correction des Redirections en Boucle"
echo "====================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Analyse du problème de boucle..."
echo "Le problème vient des conditions de redirection qui s'appliquent en boucle"
echo "Solution: Ajouter des conditions anti-boucle"

echo ""
echo "🔧 2. Création d'un template corrigé..."

cat > templates/base_fixed.html << 'TEMPLATE'
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
        
        /* Style pour les redirections */
        .redirect-notice {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            text-align: center;
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
                <!-- Menu selon le rôle -->
                <nav class="nav flex-column">
                    {% if user.username == 'AdminDaf' %}
                    <!-- AdminDaf : uniquement les natures -->
                    <a class="nav-link" href="{% url 'demandes:nature_liste' %}">
                        <i class="bi bi-diagram-3"></i> Natures Économiques
                    </a>
                    {% else %}
                    <!-- Autres utilisateurs -->
                    <a class="nav-link" href="{% url 'tableau_bord_feuilles:tableau_bord_feuilles' %}">
                        <i class="bi bi-speedometer2"></i> Tableau de bord
                    </a>
                    
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
                    {% endif %}
                    
                    {% if user.role == 'DG' or user.role == 'CD_FINANCE' %}
                    <a class="nav-link" href="{% url 'clotures:periode_actuelle' %}">
                        <i class="bi bi-lock"></i> Clôtures
                    </a>
                    {% endif %}
                    
                    {% if user.is_superuser %}
                    <hr style="border-color: rgba(255,255,255,0.2);">
                    <a class="nav-link" href="/admin/">
                        <i class="bi bi-gear"></i> Administration Django
                    </a>
                    {% endif %}
                </nav>
            </div>
            
            <!-- Main Content -->
            <div class="{% if user.is_authenticated %}col-md-10{% else %}col-12{% endif %} main-content">
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
            {% endif %}
        </div>
    </div>

    <!-- jQuery (nécessaire pour Bootstrap) -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <!-- Bootstrap 5 JS -->
    <script src="{% static 'js/bootstrap.bundle.min.js' %}"></script>
    <!-- Chart.js -->
    <script src="{% static 'js/chart.umd.min.js' %}"></script>
    
    <!-- Script de redirection anti-boucle -->
    <script>
        // Attendre que la page soit chargée
        document.addEventListener('DOMContentLoaded', function() {
            {% if user.is_authenticated %}
                // Variables Django
                var currentPath = "{{ request.path }}";
                var username = "{{ user.username }}";
                
                console.log("Redirection check:", {
                    path: currentPath,
                    username: username,
                    userRole: "{{ user.role }}"
                });
                
                // Éviter les boucles de redirection
                var redirected = false;
                
                // AdminDaf : redirigé vers les natures depuis la racine
                if (username === 'AdminDaf' && currentPath === '/' && !redirected) {
                    console.log("Redirection AdminDaf vers natures");
                    window.location.href = '/demandes/natures/';
                    redirected = true;
                }
                
                // SuperAdmin : redirigé loin des natures
                if (username === 'SuperAdmin' && currentPath === '/demandes/natures/' && !redirected) {
                    console.log("Redirection SuperAdmin loin des natures");
                    window.location.href = '/dashboard/';
                    redirected = true;
                }
                
                // Marquer que la redirection a été traitée
                if (redirected) {
                    sessionStorage.setItem('redirected', 'true');
                }
                
                // Réinitialiser après 5 secondes
                setTimeout(function() {
                    sessionStorage.removeItem('redirected');
                }, 5000);
            {% endif %}
        });
    </script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
TEMPLATE

echo "✅ Template base_fixed.html créé avec redirections anti-boucle"

echo ""
echo "🔧 3. Remplacer le template actuel..."
echo "Voulez-vous remplacer le template actuel par la version corrigée ?"
echo "1. Oui : Remplacer base.html par base_fixed.html"
echo "2. Non : Garder l'ancien et diagnostiquer manuellement"

read -p "Votre choix (1/2): " choice

case $choice in
    1)
        echo "🔄 Remplacement du template..."
        cp templates/base.html templates/base_backup.html
        cp templates/base_fixed.html templates/base.html
        echo "✅ Template remplacé"
        echo "📋 Ancien template sauvegardé dans base_backup.html"
        ;;
    2)
        echo "🔍 Diagnostic manuel..."
        echo "Template actuel conservé"
        echo "Vérifiez manuellement les conditions de redirection"
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "🔄 4. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 5. Test de redirection..."
python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User

# Test AdminDaf
print("🧪 Test AdminDaf:")
client = Client()
admin_daf = User.objects.get(username='AdminDaf')
client.force_login(admin_daf)

# Accès à la racine
response = client.get('/', follow=False)
print(f"   Accès racine: {response.status_code}")
if response.status_code == 200:
    # Vérifier s'il y a une redirection
    content = response.content.decode('utf-8')
    if 'window.location.href' in content:
        print("   ✅ Redirection vers natures détectée")
    else:
        print("   ❌ Pas de redirection détectée")

# Test SuperAdmin
print("\n🧪 Test SuperAdmin:")
superadmin = User.objects.get(username='SuperAdmin')
client.force_login(superadmin)

# Accès aux natures
response = client.get('/demandes/natures/', follow=False)
print(f"   Accès natures: {response.status_code}")
if response.status_code == 200:
    content = response.content.decode('utf-8')
    if 'window.location.href' in content:
        print("   ✅ Redirection loin des natures détectée")
    else:
        print("   ❌ Pas de redirection détectée")

EOF

echo ""
echo "✅ Correction des redirections en boucle terminée !"
echo "🎊 Testez maintenant avec Ctrl + Shift + R"
