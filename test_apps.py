#!/usr/bin/env python
import os
import sys
import django

# Configuration minimale
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')

# Forcer le chargement des applications essentielles uniquement
try:
    django.setup()
    
    # Importer les applications pour forcer leur chargement
    from accounts.models import User
    from demandes.models import DepenseFeuille, NatureEconomique
    from recettes.models import RecetteFeuille
    from banques.models import Banque
    
    print("✅ Applications chargées avec succès")
    
    # Test d'authentification
    from django.contrib.auth import authenticate
    user = authenticate(username='DirDaf', password='DirDaf123!')
    if user:
        print(f"✅ Authentification réussie: {user.username}")
        print(f"✅ Rôle: {user.role}")
        print(f"✅ Actif: {user.is_active}")
    else:
        print("❌ Authentification échouée")
        
except Exception as e:
    print(f"❌ Erreur générale: {e}")
