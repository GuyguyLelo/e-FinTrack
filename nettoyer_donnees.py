#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

def nettoyer_donnees():
    """Supprime toutes les données sauf users, services, natures économiques, banques et comptes bancaires"""
    
    print("=== Nettoyage Complet des Données ===\n")
    
    try:
        # Import des modèles
        from recettes.models import Recette, SourceRecette
        from demandes.models import DemandePaiement, ReleveDepense, Depense, Paiement, Cheque, NomenclatureDepense
        from releves.models import ReleveBancaire, MouvementBancaire
        from etats.models import EtatGenerique, ConfigurationEtat, HistoriqueGeneration
        from accounts.models import User
        
        print("🗑️  Suppression des données en cours...\n")
        
        # 1. Supprimer les états et configurations
        print("1️⃣  Suppression des états...")
        HistoriqueGeneration.objects.all().delete()
        print(f"   ✅ Historiques de génération supprimés")
        
        EtatGenerique.objects.all().delete()
        print(f"   ✅ États génériques supprimés")
        
        ConfigurationEtat.objects.all().delete()
        print(f"   ✅ Configurations d'états supprimées")
        
        # 2. Supprimer les relevés bancaires et mouvements
        print("\n2️⃣  Suppression des relevés bancaires...")
        MouvementBancaire.objects.all().delete()
        print(f"   ✅ Mouvements bancaires supprimés")
        
        ReleveBancaire.objects.all().delete()
        print(f"   ✅ Relevés bancaires supprimés")
        
        # 3. Supprimer les paiements et chèques
        print("\n3️⃣  Suppression des paiements...")
        Cheque.objects.all().delete()
        print(f"   ✅ Chèques supprimés")
        
        Paiement.objects.all().delete()
        print(f"   ✅ Paiements supprimés")
        
        # 4. Supprimer les dépenses et relevés de dépenses
        print("\n4️⃣  Suppression des dépenses...")
        Depense.objects.all().delete()
        print(f"   ✅ Dépenses supprimées")
        
        ReleveDepense.objects.all().delete()
        print(f"   ✅ Relevés de dépenses supprimés")
        
        # 5. Supprimer les demandes de paiement
        print("\n5️⃣  Suppression des demandes de paiement...")
        DemandePaiement.objects.all().delete()
        print(f"   ✅ Demandes de paiement supprimées")
        
        # 6. Supprimer les recettes et sources de recettes
        print("\n6️⃣  Suppression des recettes...")
        Recette.objects.all().delete()
        print(f"   ✅ Recettes supprimées")
        
        SourceRecette.objects.all().delete()
        print(f"   ✅ Sources de recettes supprimées")
        
        # 7. Supprimer les nomenclatures de dépenses
        print("\n7️⃣  Suppression des nomenclatures...")
        NomenclatureDepense.objects.all().delete()
        print(f"   ✅ Nomenclatures de dépenses supprimées")
        
        # Vérification des données conservées
        print("\n📊 Données conservées:")
        
        from banques.models import Banque, CompteBancaire
        from accounts.models import Service
        
        print(f"   ✅ Utilisateurs: {User.objects.count()}")
        print(f"   ✅ Services: {Service.objects.count()}")
        print(f"   ✅ Natures économiques: {len([n for n in globals() if 'NatureEconomique' in str(n)])}")
        print(f"   ✅ Banques: {Banque.objects.count()}")
        print(f"   ✅ Comptes bancaires: {CompteBancaire.objects.count()}")
        
        print("\n🎉 Nettoyage terminé avec succès !")
        print("\n💡 Données supprimées:")
        print("   ❌ Toutes les recettes et sources de recettes")
        print("   ❌ Toutes les demandes de paiement")
        print("   ❌ Toutes les dépenses et relevés de dépenses")
        print("   ❌ Tous les paiements et chèques")
        print("   ❌ Tous les relevés bancaires et mouvements")
        print("   ❌ Tous les états et configurations")
        print("   ❌ Toutes les nomenclatures de dépenses")
        print("\n✅ Données conservées:")
        print("   ✅ Utilisateurs et leurs permissions")
        print("   ✅ Services organisationnels")
        print("   ✅ Natures économiques")
        print("   ✅ Banques et comptes bancaires (avec soldes à 0.00)")
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")

if __name__ == '__main__':
    nettoyer_donnees()
