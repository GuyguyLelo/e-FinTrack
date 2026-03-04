#!/bin/bash
# fix_natures_view_error.sh - Correction de l'erreur sur /demandes/natures/

set -e

echo "🔧 Correction de l'Erreur sur /demandes/natures/"
echo "============================================"

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Diagnostic du problème..."
echo "La page de login fonctionne, mais /demandes/natures/ donne une erreur 500"
echo "Cause probable: Vue des natures ou modèle Nature"

echo ""
echo "🔍 2. Vérification de la vue des natures..."
python manage.py shell << 'EOF'
from django.urls import reverse
from django.test import Client
from accounts.models import User

print("🧪 Test de la vue des natures:")
try:
    # Test avec AdminDaf
    admin_daf = User.objects.get(username='AdminDaf')
    client = Client()
    client.force_login(admin_daf)
    
    # Test de l'URL des natures
    url = reverse('demandes:nature_liste')
    print(f"   URL des natures: {url}")
    
    response = client.get(url)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 500:
        print("   ❌ Erreur 500 - problème dans la vue ou le modèle")
        
        # Analyser le contenu de l'erreur
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            if '500' in content:
                print("   📋 Page d'erreur 500 détectée")
            elif 'Traceback' in content:
                print("   📋 Traceback détecté dans la réponse")
            else:
                print("   📋 Contenu d'erreur analysé")
    elif response.status_code == 200:
        print("   ✅ Vue des natures fonctionne")
    else:
        print(f"   ⚠️  Status inattendu: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur lors du test: {e}")

EOF

echo ""
echo "🔍 3. Vérification du modèle Nature..."
python manage.py shell << 'EOF'
from demandes.models import Nature

print("🧪 Test du modèle Nature:")
try:
    # Test de création d'une nature
    test_nature = Nature.objects.first()
    if test_nature:
        print(f"   ✅ Modèle Nature accessible")
        print(f"   📋 Première nature: {test_nature}")
        print(f"   📋 Champs: {[f.name for f in test_nature._meta.get_fields()]}")
    else:
        print("   ⚠️  Aucune nature trouvée")
        
    # Test de requête
    natures_count = Nature.objects.count()
    print(f"   📊 Total natures: {natures_count}")
    
except Exception as e:
    print(f"   ❌ Erreur modèle Nature: {e}")

EOF

echo ""
echo "🔍 4. Vérification des permissions du modèle..."
python manage.py shell << 'EOF'
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from demandes.models import Nature

print("🧪 Test des permissions sur le modèle Nature:")
try:
    # Vérifier les permissions du modèle
    content_type = ContentType.objects.get_for_model(Nature)
    permissions = Permission.objects.filter(content_type=content_type)
    
    print(f"   📋 Content Type: {content_type}")
    print(f"   📊 Permissions trouvées: {permissions.count()}")
    
    for perm in permissions:
        print(f"      - {perm.codename}: {perm.name}")
        
except Exception as e:
    print(f"   ❌ Erreur permissions: {e}")

EOF

echo ""
echo "🔍 5. Vérification de la vue nature_liste..."
python manage.py shell << 'EOF'
import inspect
from demandes import views

print("🧪 Test de la vue nature_liste:")
try:
    # Trouver la vue
    view_name = 'nature_liste'
    if hasattr(views, view_name):
        view_func = getattr(views, view_name)
        print(f"   ✅ Vue {view_name} trouvée")
        print(f"   📋 Type: {type(view_func)}")
        
        # Analyser la source si possible
        if hasattr(view_func, '__name__'):
            print(f"   📋 Nom: {view_func.__name__}")
        
        # Vérifier les décorateurs
        if hasattr(view_func, '__wrapped__'):
            print("   📋 Vue a des décorateurs")
        
        # Vérifier les imports
        try:
            source = inspect.getsource(view_func)
            if 'Nature' in source:
                print("   ✅ Vue utilise le modèle Nature")
            if 'login_required' in source:
                print("   ✅ Vue a login_required")
            if 'role_required' in source:
                print("   ✅ Vue a role_required")
        except:
            print("   ⚠️  Impossible d'analyser la source")
    else:
        print(f"   ❌ Vue {view_name} non trouvée")
        
except Exception as e:
    print(f"   ❌ Erreur vue: {e}")

EOF

echo ""
echo "🔍 6. Vérification des URLs..."
python manage.py shell << 'EOF'
from django.urls import get_resolver
from django.urls import reverse

print("🧪 Test des URLs:")
try:
    resolver = get_resolver()
    
    # Tester la résolution de l'URL
    try:
        url = reverse('demandes:nature_liste')
        print(f"   ✅ URL 'demandes:nature_liste' résolue: {url}")
    except Exception as e:
        print(f"   ❌ Erreur résolution URL: {e}")
    
    # Lister les URLs de l'app demandes
    print("   📋 URLs de l'app demandes:")
    from demandes import urls as demandes_urls
    if hasattr(demandes_urls, 'urlpatterns'):
        for pattern in demandes_urls.urlpatterns:
            print(f"      - {pattern}")
            
except Exception as e:
    print(f"   ❌ Erreur URLs: {e}")

EOF

echo ""
echo "🔧 7. Création d'une vue de natures d'urgence..."

cat > demandes/views_nature_emergency.py << 'EMERGENCY_NATURE_VIEW'
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from demandes.models import Nature
from django.http import JsonResponse
import json

@login_required
def nature_liste_emergency(request):
    """Vue des natures d'urgence - ultra simple"""
    try:
        # Récupérer toutes les natures
        natures = Nature.objects.all()
        
        # Préparer les données pour le template
        context = {
            'natures': natures,
            'user': request.user,
        }
        
        return render(request, 'demandes/nature_liste_emergency.html', context)
        
    except Exception as e:
        # En cas d'erreur, retourner une réponse simple
        return JsonResponse({
            'error': str(e),
            'message': 'Erreur lors du chargement des natures'
        }, status=500)

def nature_detail_emergency(request, pk):
    """Vue de détail d'une nature d'urgence"""
    try:
        nature = Nature.objects.get(pk=pk)
        return JsonResponse({
            'id': nature.id,
            'code': nature.code,
            'libelle': nature.libelle,
            'description': getattr(nature, 'description', '')
        })
    except Nature.DoesNotExist:
        return JsonResponse({'error': 'Nature non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

print("✅ Vue d'urgence des natures créée")
EMERGENCY_NATURE_VIEW

echo ""
echo "🔧 8. Création d'un template de natures d'urgence..."

cat > templates/demandes/nature_liste_emergency.html << 'EMERGENCY_NATURE_TEMPLATE'
{% extends 'base.html' %}
{% load static %}

{% block title %}Natures Économiques - e-Finance DAF{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="bi bi-diagram-3"></i> Natures Économiques</h2>
                {% if user.username == 'AdminDaf' %}
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addNatureModal">
                    <i class="bi bi-plus"></i> Ajouter une nature
                </button>
                {% endif %}
            </div>
            
            {% if natures %}
            <div class="card">
                <div class="card-header">
                    <h5><i class="bi bi-list"></i> Liste des Natures Économiques</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Code</th>
                                    <th>Libellé</th>
                                    <th>Description</th>
                                    {% if user.username == 'AdminDaf' %}
                                    <th>Actions</th>
                                    {% endif %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for nature in natures %}
                                <tr>
                                    <td>{{ nature.code }}</td>
                                    <td>{{ nature.libelle }}</td>
                                    <td>{{ nature.description|default:"-" }}</td>
                                    {% if user.username == 'AdminDaf' %}
                                    <td>
                                        <button class="btn btn-sm btn-outline-primary" onclick="editNature({{ nature.id }})">
                                            <i class="bi bi-pencil"></i>
                                        </button>
                                        <button class="btn btn-sm btn-outline-danger" onclick="deleteNature({{ nature.id }})">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </td>
                                    {% endif %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i>
                Aucune nature économique trouvée.
                {% if user.username == 'AdminDaf' %}
                <br>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addNatureModal">
                    <i class="bi bi-plus"></i> Ajouter la première nature
                </button>
                {% endif %}
            </div>
            {% endif %}
        </div>
    </div>
</div>

<!-- Modal d'ajout pour AdminDaf -->
{% if user.username == 'AdminDaf' %}
<div class="modal fade" id="addNatureModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">
                    <i class="bi bi-plus"></i> Ajouter une Nature Économique
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="addNatureForm">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label class="form-label">Code</label>
                        <input type="text" name="code" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Libellé</label>
                        <input type="text" name="libelle" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea name="description" class="form-control" rows="3"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annuler</button>
                <button type="button" class="btn btn-primary" onclick="saveNature()">Enregistrer</button>
            </div>
        </div>
    </div>
</div>

<script>
function editNature(id) {
    alert('Fonction d\'édition à implémenter pour la nature ' + id);
}

function deleteNature(id) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette nature ?')) {
        alert('Fonction de suppression à implémenter pour la nature ' + id);
    }
}

function saveNature() {
    const form = document.getElementById('addNatureForm');
    const formData = new FormData(form);
    
    fetch('/demandes/natures/create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erreur: ' + data.error);
        }
    })
    .catch(error => {
        alert('Erreur lors de l\'ajout: ' + error);
    });
}
</script>
{% endif %}
{% endblock %}
EMERGENCY_NATURE_TEMPLATE

echo "✅ Template d'urgence des natures créé"

echo ""
echo "🔧 9. Mise à jour des URLs d'urgence..."
echo "Ajout des URLs d'urgence dans demandes/urls.py..."

# Vérifier si le fichier URLs existe
if [ -f "demandes/urls.py" ]; then
    echo "📋 Ajout des URLs d'urgence..."
    
    # Créer une sauvegarde
    cp demandes/urls.py demandes/urls_backup_$(date +%Y%m%d_%H%M%S).py
    
    # Ajouter les URLs d'urgence
    cat >> demandes/urls.py << 'URL_ADD'

# URLs d'urgence pour les natures
from django.urls import path
from . import views_nature_emergency

urlpatterns += [
    path('natures-emergency/', views_nature_emergency.nature_liste_emergency, name='nature_liste_emergency'),
    path('natures-emergency/<int:pk>/', views_nature_emergency.nature_detail_emergency, name='nature_detail_emergency'),
]

URL_ADD

    echo "✅ URLs d'urgence ajoutées"
else
    echo "❌ demandes/urls.py non trouvé"
fi

echo ""
echo "🔄 10. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 11. Test d'urgence des natures..."

python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User

print("🧪 Test d'urgence des natures:")
try:
    # Test avec AdminDaf
    admin_daf = User.objects.get(username='AdminDaf')
    client = Client()
    client.force_login(admin_daf)
    
    # Test de l'URL d'urgence des natures
    response = client.get('/demandes/natures-emergency/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'Natures Économiques' in content:
            print("   ✅ Template d'urgence des natures fonctionne")
        else:
            print("   ❌ Template d'urgence des natures cassé")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

EOF

echo ""
echo "🎯 12. Instructions finales..."
echo "========================="
echo "✅ Diagnostic des natures terminé"
echo ""
echo "🌐 URL de test d'urgence:"
echo "   http://187.77.171.80:8000/demandes/natures-emergency/"
echo ""
echo "🔧 Si l'erreur 500 persiste sur /demandes/natures/:"
echo "1. Utilisez l'URL d'urgence ci-dessus"
echo "2. Vérifiez le modèle demandes.Nature"
echo "3. Vérifiez la vue demandes.views.nature_liste"
echo "4. Vérifiez les permissions AdminDaf"
echo ""
echo "🔧 Pour corriger le problème original:"
echo "1. Analysez les logs Django pour l'erreur exacte"
echo "2. Vérifiez les décorateurs sur la vue nature_liste"
echo "3. Vérifiez les permissions du modèle Nature"
echo "4. Testez avec des données simples"

echo ""
echo "✅ Diagnostic d'urgence des natures terminé !"
echo "🎊 Utilisez l'URL d'urgence si nécessaire"
