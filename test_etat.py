#!/usr/bin/env python3
"""
Script de test pour la génération d'états
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from etats.models import EtatGenerique
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def test_generation_etat():
    """Test la génération d'un état"""
    print("=== TEST DE GÉNÉRATION D'ÉTAT ===")
    
    try:
        # Récupérer un utilisateur
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé")
            return
        
        print(f"✅ Utilisateur trouvé: {user.username}")
        
        # Créer un état de test
        etat = EtatGenerique.objects.create(
            titre="Test Relevé Dépenses",
            type_etat="RELEVE_DEPENSE",
            description="Test de génération",
            date_debut=timezone.now().date() - timedelta(days=30),
            date_fin=timezone.now().date(),
            genere_par=user,
            statut='GENERATION'
        )
        
        print(f"✅ État créé avec ID: {etat.pk}")
        
        # Importer la vue
        from etats.views import EtatGenererView
        
        # Créer une instance de vue
        view = EtatGenererView()
        
        # Calculer les données
        print("📊 Calcul des données...")
        donnees = view.calculer_donnees(etat)
        print(f"✅ Données calculées: {donnees['count']} lignes")
        
        # Mettre à jour les totaux
        etat.total_usd = donnees.get('total_usd', 0)
        etat.total_cdf = donnees.get('total_cdf', 0)
        etat.save()
        
        # Générer le PDF
        print("📄 Génération du PDF...")
        view.generer_pdf(etat, donnees)
        
        # Vérifier le résultat
        etat.refresh_from_db()
        print(f"✅ Statut final: {etat.statut}")
        print(f"✅ Fichier PDF: {etat.fichier_pdf.name if etat.fichier_pdf else 'None'}")
        
        if etat.statut == 'GENERE' and etat.fichier_pdf:
            print("🎉 GÉNÉRATION RÉUSSIE !")
            return True
        else:
            print("❌ GÉNÉRATION ÉCHOUÉE")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generation_etat()
    sys.exit(0 if success else 1)
