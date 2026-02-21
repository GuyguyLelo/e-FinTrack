#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Ajouter le chemin du projet au Python path
sys.path.insert(0, '/home/mohamed-kandolo/e-FinTrack')

# Configuration Django minimale
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')

# Test simple
try:
    django.setup()
    from django.contrib.auth import authenticate
    from accounts.models import User
    
    # Test d'authentification
    user = authenticate(username='DirDaf', password='DirDaf123!')
    if user:
        print(f"✅ Authentification réussie: {user.username}")
        print(f"✅ Rôle: {user.role}")
        print(f"✅ Actif: {user.is_active}")
    else:
        print("❌ Authentification échouée")
        
    # Test des applications
    from django.apps import apps
    try:
        apps.check_apps_ready()
        print("✅ Applications chargées avec succès")
    except Exception as e:
        print(f"❌ Erreur de chargement des apps: {e}")
        
except Exception as e:
    print(f"❌ Erreur générale: {e}")
