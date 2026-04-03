#!/usr/bin/env python
"""
Test pour valider la nouvelle logique de DepenseFeuille
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
from demandes.forms import DepenseFeuilleDirectForm, DepenseFeuilleWorkflowForm
from demandes.models import DepenseFeuille
from accounts.models import User
from decimal import Decimal
from django.utils import timezone

def test_nouvelle_logique():
    """Test la nouvelle logique de DepenseFeuille"""
    print("🧪 TEST DE LA NOUVELLE LOGIQUE DEPENSEFEUILLE")
    print("=" * 60)
    
    factory = RequestFactory()
    view = DepenseFeuilleCreateView()
    view.object = None
    
    # Test des différents types d'utilisateurs
    test_cases = [
        ('SuperAdmin', 'workflow', DepenseFeuilleWorkflowForm, True),
        ('AdminDaf', 'direct', DepenseFeuilleDirectForm, False),
        ('DirDaf', 'direct', DepenseFeuilleDirectForm, False),
        ('DivDaf', 'direct', DepenseFeuilleDirectForm, False),
        ('OpsDaf', 'direct', DepenseFeuilleDirectForm, False),
        ('Operateur', 'workflow', DepenseFeuilleWorkflowForm, False),
    ]
    
    print("📋 Test des formulaires selon le type d'utilisateur:")
    print("-" * 60)
    print(f"{'Utilisateur':15} | {'Mode':8} | {'Formulaire':25} | {'Workflow'}")
    print("-" * 60)
    
    for username, expected_mode, expected_form, is_superuser in test_cases:
        try:
            user = User.objects.get(username=username)
            request = factory.get('/demandes/depenses/feuille/creer/')
            request.user = user
            view.request = request
            
            # Test du formulaire
            form_class = view.get_form_class()
            is_correct_form = form_class == expected_form
            
            # Test du contexte
            context = view.get_context_data()
            actual_mode = context.get('mode')
            is_workflow = context.get('is_workflow')
            is_daf_user = context.get('is_daf_user')
            
            status = "✅" if is_correct_form else "❌"
            workflow_status = "✅" if is_workflow == (expected_mode == 'workflow') else "❌"
            
            print(f"{username:15} | {actual_mode:8} | {form_class.__name__:25} | {workflow_status}")
            
            if not is_correct_form:
                print(f"   Erreur: attendu {expected_form.__name__}, obtenu {form_class.__name__}")
            
        except User.DoesNotExist:
            print(f"{username:15} | {'N/A':8} | {'Non trouvé':25} | ❌")

def test_stockage_donnees():
    """Test le stockage des données selon le type d'utilisateur"""
    print("\n🧪 TEST DE STOCKAGE DES DONNÉES")
    print("=" * 40)
    
    # Test DAF (direct - champs paiement nuls)
    print("📊 Test DAF (mode direct):")
    try:
        user_daf = User.objects.get(username='AdminDaf')
        depense_daf = DepenseFeuille.objects.create(
            mois=4, annee=2026, date=timezone.now().date(),
            libelle_depenses="Test DAF direct",
            montant_fc=Decimal('100.00'),
            montant_usd=Decimal('0.00'),
            observation="Test mode DAF direct"
            # Pas de champs paiement -> seront nuls
        )
        
        print(f"   ✅ Dépense DAF créée: {depense_daf}")
        print(f"   📝 Demande: {depense_daf.demande} (NULL attendu)")
        print(f"   📝 Relevé: {depense_daf.releve_depense} (NULL attendu)")
        print(f"   📝 Payé par: {depense_daf.paiement_par} (NULL attendu)")
        print(f"   📝 Bénéficiaire: '{depense_daf.beneficiaire}' (vide attendu)")
        print(f"   📝 Date paiement: {depense_daf.date_paiement} (NULL attendu)")
        print(f"   📝 Référence: '{depense_daf.reference_paiement}' (vide attendu)")
        
        depense_daf.delete()
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test utilisateur normal (workflow - champs paiement remplis)
    print("\n📊 Test Utilisateur Normal (mode workflow):")
    try:
        user_normal = User.objects.get(username='Operateur')
        
        # Créer une demande pour le test
        from demandes.models import DemandePaiement
        from accounts.models import Service
        service = Service.objects.first()  # Prendre le premier service disponible
        demande = DemandePaiement.objects.create(
            reference="TEST-001",
            description="Test demande",
            montant=Decimal('200.00'),
            devise='CDF',
            service_demandeur=service,  # Ajout du service requis
            cree_par=user_normal
        )
        
        depense_normal = DepenseFeuille.objects.create(
            mois=4, annee=2026, date=timezone.now().date(),
            libelle_depenses="Test utilisateur normal",
            montant_fc=Decimal('200.00'),
            montant_usd=Decimal('0.00'),
            observation="Test mode workflow",
            # Champs paiement remplis
            demande=demande,
            paiement_par=user_normal,
            beneficiaire="Test Bénéficiaire",
            date_paiement=timezone.now()
        )
        
        print(f"   ✅ Dépense normale créée: {depense_normal}")
        print(f"   📝 Demande: {depense_normal.demande} (rempli attendu)")
        print(f"   📝 Relevé: {depense_normal.releve_depense} (NULL autorisé)")
        print(f"   📝 Payé par: {depense_normal.paiement_par} (rempli attendu)")
        print(f"   📝 Bénéficiaire: '{depense_normal.beneficiaire}' (rempli attendu)")
        print(f"   📝 Date paiement: {depense_normal.date_paiement} (rempli attendu)")
        print(f"   📝 Référence: '{depense_normal.reference_paiement}' (généré attendu)")
        
        depense_normal.delete()
        demande.delete()
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def test_affichage_liste():
    """Test l'affichage dans les listes"""
    print("\n🧪 TEST D'AFFICHAGE EN LISTE")
    print("=" * 40)
    
    # Créer les deux types de dépenses
    try:
        user_daf = User.objects.get(username='AdminDaf')
        user_normal = User.objects.get(username='Operateur')
        
        # Dépense DAF
        depense_daf = DepenseFeuille.objects.create(
            mois=4, annee=2026, date=timezone.now().date(),
            libelle_depenses="Dépense DAF test",
            montant_fc=Decimal('100.00')
        )
        
        # Dépense utilisateur normal
        from demandes.models import DemandePaiement
        from accounts.models import Service
        service = Service.objects.first()  # Prendre le premier service disponible
        demande = DemandePaiement.objects.create(
            reference="TEST-002",
            description="Test demande",
            montant=Decimal('200.00'),
            devise='CDF',
            service_demandeur=service,  # Ajout du service requis
            cree_par=user_normal
        )
        
        depense_normal = DepenseFeuille.objects.create(
            mois=4, annee=2026, date=timezone.now().date(),
            libelle_depenses="Dépense workflow test",
            montant_fc=Decimal('200.00'),
            demande=demande,
            paiement_par=user_normal,
            beneficiaire="Test Benef"
        )
        
        print("📋 Affichage des dépenses:")
        for depense in DepenseFeuille.objects.all():
            print(f"   {depense}")
        
        # Nettoyage
        depense_daf.delete()
        depense_normal.delete()
        demande.delete()
        
        print("   ✅ Test terminé avec succès")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    test_nouvelle_logique()
    test_stockage_donnees()
    test_affichage_liste()
    
    print("\n🎯 RÉSUMÉ DE LA NOUVELLE LOGIQUE:")
    print("=" * 50)
    print("📊 Table DepenseFeuille = Stockage UNIQUE")
    print("👥 Users DAF -> Saisie directe (champs paiement = NULL)")
    print("👥 Users Normaux -> Interface paiement (champs paiement remplis)")
    print("👥 SuperAdmin -> Interface complète")
    print("🎯 Toutes les données sont dans DepenseFeuille")
    print("🔍 Les champs paiement sont NULL pour les DAF")
    print("📋 L'affichage différencie les deux modes")
