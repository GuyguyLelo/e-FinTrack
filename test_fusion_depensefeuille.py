#!/usr/bin/env python
"""
Script de test pour la fusion DepenseFeuille et Paiement
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from decimal import Decimal
from django.utils import timezone
from accounts.models import User, Service
from banques.models import Banque
from demandes.models import DepenseFeuille, DemandePaiement, NatureEconomique

def test_mode_direct():
    """Test du mode direct"""
    print("🧪 Test du mode DIRECT")
    print("=" * 50)
    
    # Création d'une dépense en mode direct
    depense = DepenseFeuille.objects.create(
        mois=4,
        annee=2026,
        date=timezone.now().date(),
        libelle_depenses="Test dépense direct",
        montant_fc=Decimal('100.00'),
        montant_usd=Decimal('0.00'),
        observation="Test mode direct"
    )
    
    print(f"✅ Dépense créée : {depense}")
    print(f"   Mode direct : {depense.is_mode_direct}")
    print(f"   Mode workflow : {depense.is_mode_workflow}")
    print(f"   Est payée : {depense.est_payee}")
    print(f"   Montant total : {depense.montant_total}")
    
    # Test des méthodes
    print(f"   Montant CDF : {depense.get_montant_in_devise('CDF')}")
    print(f"   Montant USD : {depense.get_montant_in_devise('USD')}")
    
    depense.delete()
    print("✅ Dépense supprimée")
    print()

def test_mode_workflow():
    """Test du mode workflow"""
    print("🧪 Test du mode WORKFLOW")
    print("=" * 50)
    
    # Création d'une dépense en mode workflow (avec demande)
    user = User.objects.first()
    
    # D'abord créer une demande de paiement si elle n'existe pas
    from demandes.models import DemandePaiement
    demande = DemandePaiement.objects.create(
        reference="TEST-001",
        description="Test demande pour workflow",
        montant=Decimal('200.00'),
        devise='CDF',
        service_demandeur=Service.objects.first() if Service.objects.exists() else None,
        cree_par=user  # Ajout du créateur requis
    )
    
    depense = DepenseFeuille.objects.create(
        mois=4,
        annee=2026,
        date=timezone.now().date(),
        libelle_depenses="Test dépense workflow",
        montant_fc=Decimal('200.00'),
        montant_usd=Decimal('0.00'),
        observation="Test mode workflow",
        beneficiaire="Test Bénéficiaire",
        paiement_par=user,
        date_paiement=timezone.now(),
        demande=demande  # Lien avec une demande = mode workflow
    )
    
    print(f"✅ Dépense créée : {depense}")
    print(f"   Mode direct : {depense.is_mode_direct}")
    print(f"   Mode workflow : {depense.is_mode_workflow}")
    print(f"   Est payée : {depense.est_payee}")
    print(f"   Bénéficiaire : {depense.beneficiaire}")
    print(f"   Payé par : {depense.paiement_par}")
    print(f"   Référence paiement : {depense.reference_paiement}")
    print(f"   Demande liée : {depense.demande}")
    
    depense.delete()
    demande.delete()
    print("✅ Dépense et demande supprimées")
    print()

def test_affichage_liste():
    """Test de l'affichage en liste"""
    print("🧪 Test de l'affichage en liste")
    print("=" * 50)
    
    # Création des deux types de dépenses
    depense_direct = DepenseFeuille.objects.create(
        mois=4, annee=2026, date=timezone.now().date(),
        libelle_depenses="Dépense direct test",
        montant_fc=Decimal('100.00')
    )
    
    depense_workflow = DepenseFeuille.objects.create(
        mois=4, annee=2026, date=timezone.now().date(),
        libelle_depenses="Dépense workflow test",
        montant_fc=Decimal('200.00'),
        beneficiaire="Test Benef",
        paiement_par=User.objects.first()
    )
    
    # Affichage
    print("📋 Liste des dépenses :")
    for depense in DepenseFeuille.objects.all():
        print(f"   {depense}")
    
    # Nettoyage
    depense_direct.delete()
    depense_workflow.delete()
    print("✅ Nettoyage effectué")
    print()

def main():
    """Fonction principale"""
    print("🚀 Tests de la fusion DepenseFeuille et Paiement")
    print("=" * 60)
    print()
    
    try:
        # Vérification des prérequis
        if User.objects.exists():
            print("✅ Utilisateurs trouvés")
        else:
            print("❌ Aucun utilisateur trouvé")
            return
            
        if Banque.objects.exists():
            print("✅ Banques trouvées")
        else:
            print("⚠️ Aucune banque trouvée (création d'une banque de test)")
            Banque.objects.create(nom_banque="Banque Test", active=True)
        
        # Exécution des tests
        test_mode_direct()
        test_mode_workflow()
        test_affichage_liste()
        
        print("🎉 Tous les tests sont passés avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors des tests : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
