#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

print("Test de base Django...")
try:
    from tableau_bord_feuilles.views_etats_feuilles import NaturesEconomiquesAPIView
    print("✅ Import NaturesEconomiquesAPIView réussi")
    
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get('/tableau-bord-feuilles/api/natures-economiques/')
    view = NaturesEconomiquesAPIView()
    response = view.get(request)
    print(f"Status: {response.status_code}")
    print(f"Content: {response.content.decode()[:100]}...")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
