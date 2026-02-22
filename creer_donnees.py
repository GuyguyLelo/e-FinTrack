#!/usr/bin/env python
"""
Script pour créer les enregistrements manuellement avec les bons IDs
"""
import json
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from demandes.models import DepenseFeuille
from recettes.models import RecetteFeuille
from banques.models import Banque

def creer_donnees_manuellement():
    """Créer les enregistrements manuellement"""
    
    # Lire le fichier JSON corrigé
    with open('donnees_corrigees.json', 'r') as f:
        data = json.load(f)
    
    print("🔧 Création manuelle des enregistrements...")
    
    # Créer les dépenses
    depenses_crees = 0
    for item in data:
        if item.get('model') == 'demandes.depensefeuille':
            fields = item.get('fields', {})
            
            try:
                depense = DepenseFeuille.objects.create(
                    mois=fields.get('mois'),
                    annee=fields.get('annee'),
                    date=fields.get('date'),
                    libelle_depenses=fields.get('libelle_depenses'),
                    montant_fc=fields.get('montant_fc'),
                    montant_usd=fields.get('montant_usd'),
                    observation=fields.get('observation', ''),
                    banque_id=fields.get('banque'),
                    service_beneficiaire_id=1,  # Service de test
                    nature_economique_id=fields.get('nature_economique_id')
                )
                depenses_crees += 1
                print(f"   ✅ Dépense créée: {fields.get('libelle_depenses')}")
            except Exception as e:
                print(f"   ❌ Erreur création dépense: {e}")
    
    # Créer les recettes
    recettes_crees = 0
    for item in data:
        if item.get('model') == 'recettes.recettefeuille':
            fields = item.get('fields', {})
            
            try:
                recette = RecetteFeuille.objects.create(
                    mois=fields.get('mois'),
                    annee=fields.get('annee'),
                    date=fields.get('date'),
                    libelle_recette=fields.get('libelle_recette'),
                    montant_fc=fields.get('montant_fc'),
                    montant_usd=fields.get('montant_usd'),
                    banque_id=fields.get('banque')
                )
                recettes_crees += 1
                print(f"   ✅ Recette créée: {fields.get('libelle_recette')}")
            except Exception as e:
                print(f"   ❌ Erreur création recette: {e}")
    
    print(f"\n📊 Résumé:")
    print(f"   Dépenses créées: {depenses_crees}")
    print(f"   Recettes créées: {recettes_crees}")
    print(f"   Total: {depenses_crees + recettes_crees}")

if __name__ == "__main__":
    creer_donnees_manuellement()
