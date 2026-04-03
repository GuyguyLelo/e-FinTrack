#!/usr/bin/env python
"""
Test pour vérifier la détection des utilisateurs DAF et l'assignation des formulaires
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from demandes.views import DepenseFeuilleCreateView
from demandes.forms import DepenseFeuilleDirectForm, DepenseFeuilleWorkflowForm
from accounts.models import User

def test_detection_utilisateurs():
    """Test la détection du type d'utilisateur et l'assignation des formulaires"""
    print("🧪 Test de détection des utilisateurs DAF")
    print("=" * 60)
    
    # Créer une factory de requêtes
    factory = RequestFactory()
    
    # Créer des utilisateurs de test
    users_test = {
        'admin_daf': {'username': 'admin_daf', 'expected_form': DepenseFeuilleDirectForm, 'is_superuser': False},
        'user_daf123': {'username': 'user_daf123', 'expected_form': DepenseFeuilleDirectForm, 'is_superuser': False},
        'test_DAF': {'username': 'test_DAF', 'expected_form': DepenseFeuilleDirectForm, 'is_superuser': False},
        'normal_user': {'username': 'normal_user', 'expected_form': DepenseFeuilleWorkflowForm, 'is_superuser': False},
        'finance_user': {'username': 'finance_user', 'expected_form': DepenseFeuilleWorkflowForm, 'is_superuser': False},
        'comptable': {'username': 'comptable', 'expected_form': DepenseFeuilleWorkflowForm, 'is_superuser': False},
        'superadmin': {'username': 'superadmin', 'expected_form': DepenseFeuilleWorkflowForm, 'is_superuser': True},
    }
    
    # Créer la vue
    view = DepenseFeuilleCreateView()
    
    print("📋 Test des utilisateurs :")
    print()
    
    for username, config in users_test.items():
        # Créer une requête factice
        request = factory.get('/demandes/depenses/feuille/creer/')
        
        # Créer ou récupérer l'utilisateur
        user, created = User.objects.get_or_create(username=username, defaults={'password': 'test123'})
        if created:
            user.set_password('test123')
            user.is_superuser = config['is_superuser']
            user.save()
        
        request.user = user
        view.request = request
        
        # Tester la détection
        is_daf_user = 'daf' in user.username.lower()
        is_superadmin = user.is_superuser
        form_class = view.get_form_class()
        
        # Vérifications
        expected_form = config['expected_form']
        is_correct = form_class == expected_form
        
        status = "✅" if is_correct else "❌"
        if is_superadmin:
            mode = "SuperAdmin"
        elif is_daf_user:
            mode = "Direct"
        else:
            mode = "Workflow"
        
        print(f"{status} {username:12} -> {mode:10} | {form_class.__name__:25} | {'OK' if is_correct else 'ERREUR'}")
        
        if not is_correct:
            print(f"   Attendu: {expected_form.__name__}")
            print(f"   Obtenu: {form_class.__name__}")
    
    print()
    print("🎊 Test terminé !")
    
    # Nettoyage
    for username in users_test.keys():
        User.objects.filter(username=username).delete()

def test_context_data():
    """Test que le contexte contient les bonnes variables"""
    print("\n🧪 Test du contexte de la vue")
    print("=" * 40)
    
    factory = RequestFactory()
    view = DepenseFeuilleCreateView()
    
    # Initialiser l'objet pour éviter l'erreur
    view.object = None
    
    # Test avec utilisateur DAF
    request = factory.get('/demandes/depenses/feuille/creer/')
    user_daf, created = User.objects.get_or_create(username='test_daf_user', defaults={'password': 'test123'})
    if created:
        user_daf.set_password('test123')
        user_daf.save()
    request.user = user_daf
    view.request = request
    
    # Simuler le contexte
    context = view.get_context_data()
    
    print(f"📊 Contexte pour utilisateur DAF :")
    print(f"   is_daf_user   : {context.get('is_daf_user', 'NOT_FOUND')}")
    print(f"   is_superadmin  : {context.get('is_superadmin', 'NOT_FOUND')}")
    print(f"   mode          : {context.get('mode', 'NOT_FOUND')}")
    print(f"   is_workflow   : {context.get('is_workflow', 'NOT_FOUND')}")
    
    # Test avec utilisateur normal
    user_normal, created = User.objects.get_or_create(username='test_normal_user', defaults={'password': 'test123'})
    if created:
        user_normal.set_password('test123')
        user_normal.save()
    request.user = user_normal
    view.request = request
    
    context = view.get_context_data()
    
    print(f"\n📊 Contexte pour utilisateur normal :")
    print(f"   is_daf_user   : {context.get('is_daf_user', 'NOT_FOUND')}")
    print(f"   is_superadmin  : {context.get('is_superadmin', 'NOT_FOUND')}")
    print(f"   mode          : {context.get('mode', 'NOT_FOUND')}")
    print(f"   is_workflow   : {context.get('is_workflow', 'NOT_FOUND')}")
    
    # Test avec SuperAdmin
    user_superadmin, created = User.objects.get_or_create(username='test_superadmin', defaults={'password': 'test123'})
    if created:
        user_superadmin.set_password('test123')
        user_superadmin.is_superuser = True
        user_superadmin.save()
    request.user = user_superadmin
    view.request = request
    
    context = view.get_context_data()
    
    print(f"\n📊 Contexte pour SuperAdmin :")
    print(f"   is_daf_user   : {context.get('is_daf_user', 'NOT_FOUND')}")
    print(f"   is_superadmin  : {context.get('is_superadmin', 'NOT_FOUND')}")
    print(f"   mode          : {context.get('mode', 'NOT_FOUND')}")
    print(f"   is_workflow   : {context.get('is_workflow', 'NOT_FOUND')}")
    
    # Nettoyage
    user_daf.delete()
    user_normal.delete()
    user_superadmin.delete()
    
    print("\n✅ Test du contexte terminé !")

if __name__ == "__main__":
    test_detection_utilisateurs()
    test_context_data()
