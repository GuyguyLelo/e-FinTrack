#!/usr/bin/env python
import os
import sys
import django

# Configuration minimale
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings_minimal')

try:
    django.setup()
    print("✅ Django setup réussi")
    
    # Démarrer le serveur
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8017', '--noreload', '--settings=efinance_daf.settings_minimal'])
    
except Exception as e:
    print(f"❌ Erreur: {e}")
