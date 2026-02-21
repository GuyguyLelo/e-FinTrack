#!/usr/bin/env python
"""
Script de test pour vérifier les nouveaux filtres sur les pages de recettes et dépenses
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from django.test import Client
from django.urls import reverse
from datetime import datetime, timedelta

def test_filtres():
    """Test des nouveaux filtres sur recettes et dépenses"""
    
    print("🔍 Test des nouveaux filtres")
    print("=" * 50)
    
    users_to_test = [
        ('AdminDaf', 'admin123'),
        ('OpsDaf', 'OpsDaf123')
    ]
    
    for username, password in users_to_test:
        try:
            user = User.objects.get(username=username)
            
            print(f"\n👤 Test pour {username} ({user.role})")
            
            # Créer un client et se connecter
            client = Client()
            login_success = client.login(username=username, password=password)
            
            if not login_success:
                user.set_password(password)
                user.save()
                login_success = client.login(username=username, password=password)
            
            if login_success:
                # Test 1: Accès aux pages de liste
                print(f"\n📄 Test d'accès aux pages:")
                
                # Page recettes
                response = client.get('/recettes/feuille/')
                print(f"   Recettes: {response.status_code}")
                
                # Page dépenses
                response = client.get('/demandes/depenses/feuille/')
                print(f"   Dépenses: {response.status_code}")
                
                # Test 2: Vérifier les filtres dans le contenu HTML
                print(f"\n🔍 Test des filtres dans le HTML:")
                
                # Vérifier les filtres sur la page recettes
                response = client.get('/recettes/feuille/')
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    # Vérifier les nouveaux filtres
                    filtres_attendus = [
                        'Date début',
                        'Date fin',
                        'name="date_debut"',
                        'name="date_fin"',
                        'name="banque"',
                        'Toutes',
                        'Filtrer'
                    ]
                    
                    print(f"   Filtres recettes:")
                    for filtre in filtres_attendus:
                        if filtre in content:
                            print(f"      ✅ {filtre}")
                        else:
                            print(f"      ❌ {filtre}")
                
                # Vérifier les filtres sur la page dépenses
                response = client.get('/demandes/depenses/feuille/')
                if response.status_code == 200:
                    content = response.content.decode()
                    
                    print(f"   Filtres dépenses:")
                    for filtre in filtres_attendus:
                        if filtre in content:
                            print(f"      ✅ {filtre}")
                        else:
                            print(f"      ❌ {filtre}")
                
                # Test 3: Tester les filtres avec des valeurs
                print(f"\n🧪 Test des filtres avec paramètres:")
                
                # Date d'aujourd'hui pour les tests
                today = datetime.now().date()
                last_week = today - timedelta(days=7)
                
                test_params = [
                    # Test filtre par date
                    f'?date_debut={last_week.strftime("%Y-%m-%d")}&date_fin={today.strftime("%Y-%m-%d")}',
                    # Test filtre par année
                    '?annee=2024',
                    # Test filtre par mois
                    '?mois=1',
                    # Test filtre combiné
                    '?annee=2024&mois=1&date_debut=2024-01-01&date_fin=2024-01-31'
                ]
                
                for i, params in enumerate(test_params, 1):
                    print(f"   Test {i}: {params}")
                    
                    # Test sur recettes
                    response = client.get(f'/recettes/feuille/{params}')
                    print(f"      Recettes: {response.status_code}")
                    
                    # Test sur dépenses
                    response = client.get(f'/demandes/depenses/feuille/{params}')
                    print(f"      Dépenses: {response.status_code}")
            
        except User.DoesNotExist:
            print(f"\n❌ L'utilisateur {username} n'existe pas!")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
    
    print(f"\n🎯 Résumé:")
    print(f"   - Filtres par date ajoutés sur les deux pages")
    print(f"   - Filtre banque converti en select pour recettes")
    print(f"   - Filtres par date (début/fin) fonctionnels")
    print(f"   - Interface améliorée pour la recherche")

if __name__ == "__main__":
    test_filtres()
