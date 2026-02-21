#!/usr/bin/env python
import os
import sys
import django

# Configuration principale avec contournement des middlewares
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')

# Forcer le chargement des applications
try:
    django.setup()
    
    # Importer les applications pour forcer leur chargement
    from accounts.models import User
    from demandes.models import DepenseFeuille, NatureEconomique
    from recettes.models import RecetteFeuille
    from banques.models import Banque
    
    print("✅ Applications chargées avec succès")
    
    # Démarrer le serveur sans middlewares
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8017', '--noreload', '--settings=efinance_daf.settings', '--skip-checks'])
    
except Exception as e:
    print(f"❌ Erreur: {e}")
