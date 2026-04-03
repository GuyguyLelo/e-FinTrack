#!/usr/bin/env python
"""
Test pour valider la nouvelle logique finale
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.test import RequestFactory
from demandes.views import DepenseFeuilleCreateView
from demandes.forms import DepenseFeuilleDirectForm
from accounts.models import User

def test_logique_finale():
    """Test la logique finale de redirection"""
    print("🧪 TEST DE LA LOGIQUE FINALE")
    print("=" * 50)
    
    factory = RequestFactory()
    view = DepenseFeuilleCreateView()
    view.object = None
    
    # Test des différents types d'utilisateurs
    test_cases = [
        ('SuperAdmin', 'superadmin', 'direct', True),
        ('AdminDaf', 'daf', 'direct', True),
        ('DirDaf', 'daf', 'direct', True),
        ('DivDaf', 'daf', 'direct', True),
        ('OpsDaf', 'daf', 'direct', True),
        ('Operateur', 'normal', 'redirect', False),
    ]
    
    print("📋 Test de redirection selon le type d'utilisateur:")
    print("-" * 60)
    print(f"{'Utilisateur':15} | {'Type':8} | {'Action':10} | {'Accès page'}")
    print("-" * 60)
    
    for username, user_type, expected_action, should_access in test_cases:
        try:
            user = User.objects.get(username=username)
            request = factory.get('/demandes/depenses/feuille/creer/')
            request.user = user
            view.request = request
            
            # Test de la méthode dispatch
            response = view.dispatch(request)
            
            if hasattr(response, 'url'):
                # C'est une redirection
                action = 'redirect'
                access_page = False
                redirect_url = response.url
            else:
                # C'est la vue normale
                action = 'view'
                access_page = True
                redirect_url = None
            
            is_correct = (action == expected_action)
            status = "✅" if is_correct else "❌"
            
            print(f"{username:15} | {user_type:8} | {action:10} | {access_page}")
            
            if not is_correct:
                print(f"   Erreur: attendu {expected_action}, obtenu {action}")
                if redirect_url:
                    print(f"   Redirection vers: {redirect_url}")
            
        except User.DoesNotExist:
            print(f"{username:15} | {'N/A':8} | {'ERROR':10} | False")
        except Exception as e:
            print(f"{username:15} | {user_type:8} | {'ERROR':10} | False - {e}")

def test_formulaire():
    """Test que seul le formulaire direct est utilisé"""
    print("\n🧪 TEST DU FORMULAIRE")
    print("=" * 30)
    
    factory = RequestFactory()
    view = DepenseFeuilleCreateView()
    view.object = None
    
    # Test avec un utilisateur DAF
    user_daf = User.objects.get(username='AdminDaf')
    request = factory.get('/demandes/depenses/feuille/creer/')
    request.user = user_daf
    view.request = request
    
    # La méthode dispatch retourne la vue, donc on peut tester get_form_class
    form_class = view.get_form_class()
    expected_form = DepenseFeuilleDirectForm
    
    print(f"📋 Formulaire pour AdminDaf:")
    print(f"   Attendu: {expected_form.__name__}")
    print(f"   Obtenu: {form_class.__name__}")
    print(f"   ✅ Correct: {form_class == expected_form}")
    
    # Test avec SuperAdmin
    user_superadmin = User.objects.get(username='SuperAdmin')
    request.user = user_superadmin
    view.request = request
    
    form_class = view.get_form_class()
    print(f"\n📋 Formulaire pour SuperAdmin:")
    print(f"   Attendu: {expected_form.__name__}")
    print(f"   Obtenu: {form_class.__name__}")
    print(f"   ✅ Correct: {form_class == expected_form}")

def test_contexte():
    """Test le contexte pour les utilisateurs qui accèdent à la page"""
    print("\n🧪 TEST DU CONTEXTE")
    print("=" * 30)
    
    factory = RequestFactory()
    view = DepenseFeuilleCreateView()
    view.object = None
    
    # Test avec AdminDaf
    user_daf = User.objects.get(username='AdminDaf')
    request = factory.get('/demandes/depenses/feuille/creer/')
    request.user = user_daf
    view.request = request
    
    context = view.get_context_data()
    
    print("📊 Contexte pour AdminDaf:")
    print(f"   mode: {context.get('mode')}")
    print(f"   is_daf_user: {context.get('is_daf_user')}")
    print(f"   is_superadmin: {context.get('is_superadmin')}")
    
    # Test avec SuperAdmin
    user_superadmin = User.objects.get(username='SuperAdmin')
    request.user = user_superadmin
    view.request = request
    
    context = view.get_context_data()
    
    print("\n📊 Contexte pour SuperAdmin:")
    print(f"   mode: {context.get('mode')}")
    print(f"   is_daf_user: {context.get('is_daf_user')}")
    print(f"   is_superadmin: {context.get('is_superadmin')}")

if __name__ == "__main__":
    test_logique_finale()
    test_formulaire()
    test_contexte()
    
    print("\n🎯 RÉSUMÉ DE LA LOGIQUE FINALE:")
    print("=" * 50)
    print("📊 URL /demandes/depenses/feuille/creer/ :")
    print("🔹 SuperAdmin -> Accès direct (formulaire direct)")
    print("🔹 Users DAF -> Accès direct (formulaire direct)")
    print("🔹 Users Normaux -> REDIRECTION vers /demandes/paiement/creer/")
    print("🎯 Les utilisateurs normaux utilisent l'interface de paiement classique")
    print("🎯 Les données de paiement seront stockées dans DepenseFeuille")
    print("🎯 Les DAF utilisent l'interface directe sans champs paiement")
