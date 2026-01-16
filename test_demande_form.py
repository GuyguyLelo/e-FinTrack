#!/usr/bin/env python
"""
Script de test pour vérifier la création de demandes de paiement
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from demandes.models import DemandePaiement, NomenclatureDepense, NatureEconomique
from accounts.models import Service

User = get_user_model()

def test_formulaire_demande():
    """Teste le formulaire de création de demande avec toutes les données requises"""
    
    print("🧪 TEST DU FORMULAIRE DE CRÉATION DE DEMANDE")
    print("=" * 60)
    
    # Récupérer les données de test
    try:
        service_financier = Service.objects.get(nom_service='Service Financier')
        nomenclature = NomenclatureDepense.objects.first()
        nature_economique = NatureEconomique.objects.first()
        
        print(f"✅ Service Financier: {service_financier.nom_service} (ID: {service_financier.id})")
        print(f"✅ Nomenclature: {nomenclature} (ID: {nomenclature.id})")
        print(f"✅ Nature Économique: {nature_economique.code} - {nature_economique.titre} (ID: {nature_economique.id})")
        
        # Créer un client de test
        client = Client()
        
        # Se connecter comme chef de service financier
        chef_service = User.objects.get(username='chef_service')
        client.force_login(chef_service)
        
        print(f"\n👤 Utilisateur connecté: {chef_service.username} ({chef_service.get_role_display()})")
        
        # Préparer les données du formulaire
        donnees_formulaire = {
            'service_demandeur': service_financier.id,
            'nomenclature': nomenclature.id,
            'nature_economique': nature_economique.id,
            'date_demande': '2024-03-15',
            'description': 'Test de création de demande avec toutes les données requises',
            'montant': '1500.00',
            'devise': 'USD',
        }
        
        print(f"\n📋 Données du formulaire:")
        for key, value in donnees_formulaire.items():
            print(f"  • {key}: {value}")
        
        # Soumettre le formulaire
        print(f"\n🔄 Soumission du formulaire...")
        response = client.post('/demandes/creer/', donnees_formulaire)
        
        print(f"📊 Statut de la réponse: {response.status_code}")
        
        if response.status_code == 302:
            # Redirection vers la liste = succès
            print("✅ Demande créée avec succès !")
            print(f"🔄 Redirection vers: {response.url}")
            
            # Vérifier que la demande a bien été créée
            nouvelles_demandes = DemandePaiement.objects.filter(
                service_demandeur=service_financier,
                description__contains='Test de création'
            )
            if nouvelles_demandes.exists():
                demande = nouvelles_demandes.first()
                print(f"📄 Nouvelle demande: {demande.reference}")
                print(f"  • Service: {demande.service_demandeur.nom_service}")
                print(f"  • Nomenclature: {demande.nomenclature}")
                print(f"  • Nature: {demande.nature_economique}")
                print(f"  • Montant: {demande.montant} {demande.devise}")
                print(f"  • Statut: {demande.get_statut_display()}")
            else:
                print("❌ Erreur: La demande n'a pas été trouvée en base")
        else:
            print(f"❌ Erreur lors de la soumission (code: {response.status_code})")
            if hasattr(response, 'context'):
                form = response.context.get('form')
                if form and form.errors:
                    print("🚫 Erreurs du formulaire:")
                    for field, errors in form.errors.items():
                        print(f"  • {field}: {errors}")
            
            # Afficher le contenu de la réponse pour débogage
            print(f"\n📄 Contenu de la réponse (premiers 500 caractères):")
            print(response.content.decode()[:500])
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

def verifier_champs_formulaire():
    """Vérifie les champs disponibles dans le formulaire"""
    
    print("\n🔍 VÉRIFICATION DES CHAMPS DU FORMULAIRE")
    print("=" * 60)
    
    from demandes.forms import DemandePaiementForm
    
    # Créer une instance du formulaire sans utilisateur
    form = DemandePaiementForm()
    
    print("📋 Champs du formulaire:")
    for field_name, field in form.fields.items():
        required = "✅ Requis" if field.required else "⭕ Optionnel"
        print(f"  • {field_name}: {field.label} ({required})")
        
        # Afficher les choix si c'est un ChoiceField
        if hasattr(field, 'choices') and field.choices:
            print(f"    Choix disponibles:")
            choices_list = list(field.choices)
            for choice_value, choice_label in choices_list[:5]:  # Limiter à 5 pour la lisibilité
                print(f"      - {choice_value}: {choice_label}")
            if len(choices_list) > 5:
                print(f"      ... et {len(choices_list) - 5} autres choix")

if __name__ == "__main__":
    verifier_champs_formulaire()
    test_formulaire_demande()
