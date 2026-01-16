#!/usr/bin/env python
"""
Script de diagnostic complet des fixtures demandes
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from demandes.models import DemandePaiement, ReleveDepense, Depense, NomenclatureDepense, NatureEconomique, Cheque
from accounts.models import Service, User
from decimal import Decimal

def diagnostic_complet():
    """Diagnostic complet de toutes les données"""
    
    print("🔍 DIAGNOSTIC COMPLET DES FIXTURES DEMANDES")
    print("=" * 80)
    
    # 1. Services
    print("\n📋 SERVICES")
    print("-" * 40)
    services = Service.objects.all()
    for service in services:
        print(f"• {service.nom_service} (ID: {service.id}) - Actif: {service.actif}")
    
    # 2. Nomenclatures
    print("\n📚 NOMENCLATURES")
    print("-" * 40)
    nomenclatures = NomenclatureDepense.objects.all()
    for nom in nomenclatures:
        print(f"• {nom} (ID: {nom.id})")
    
    # 3. Natures Économiques
    print("\n🏷️  NATURES ÉCONOMIQUES")
    print("-" * 40)
    natures = NatureEconomique.objects.all()
    for nature in natures:
        print(f"• {nature.code} - {nature.titre} (ID: {nature.id})")
    
    # 4. Demandes de Paiement
    print("\n💸 DEMANDES DE PAIEMENT")
    print("-" * 40)
    demandes = DemandePaiement.objects.all().order_by('pk')
    print(f"Total: {demandes.count()} demandes")
    
    for demande in demandes:
        print(f"\n• {demande.reference} (PK: {demande.pk})")
        print(f"  Service: {demande.service_demandeur.nom_service if demande.service_demandeur else 'NULL'}")
        print(f"  Nomenclature: {demande.nomenclature if demande.nomenclature else 'NULL'}")
        print(f"  Nature: {demande.nature_economique.code if demande.nature_economique else 'NULL'} - {demande.nature_economique.titre if demande.nature_economique else 'NULL'}")
        print(f"  Montant: {demande.montant} {demande.devise}")
        print(f"  Statut: {demande.statut}")
        print(f"  Créée par: {demande.cree_par.username if demande.cree_par else 'NULL'}")
        print(f"  Approuvée par: {demande.approuve_par.username if demande.approuve_par else 'NULL'}")
        print(f"  Date demande: {demande.date_demande}")
        print(f"  Date soumission: {demande.date_soumission}")
    
    # 5. Relevés de Dépenses
    print("\n📄 RELEVÉS DE DÉPENSES")
    print("-" * 40)
    releves = ReleveDepense.objects.all()
    print(f"Total: {releves.count()} relevés")
    
    for releve in releves:
        print(f"\n• {releve.numero} (PK: {releve.pk})")
        print(f"  Période: {releve.periode}")
        print(f"  Demandes: {list(releve.demandes.all().values_list('reference', flat=True))}")
        print(f"  Montant CDF: {releve.montant_cdf}")
        print(f"  Montant USD: {releve.montant_usd}")
        print(f"  IPR CDF: {releve.ipr_cdf}")
        print(f"  IPR USD: {releve.ipr_usd}")
        print(f"  Net CDF: {releve.net_a_payer_cdf}")
        print(f"  Net USD: {releve.net_a_payer_usd}")
        print(f"  Validé par: {releve.valide_par.username if releve.valide_par else 'NULL'}")
        print(f"  Date validation: {releve.date_validation}")
    
    # 6. Dépenses Historiques
    print("\n💰 DÉPENSES HISTORIQUES")
    print("-" * 40)
    depenses = Depense.objects.all()
    print(f"Total: {depenses.count()} dépenses")
    
    for depense in depenses:
        print(f"\n• {depense.code_depense} (PK: {depense.pk})")
        print(f"  Mois/Année: {depense.mois}/{depense.annee}")
        print(f"  Date dépense: {depense.date_depense}")
        print(f"  Libellé: {depense.libelle_depenses}")
        print(f"  Montant FC: {depense.montant_fc}")
        print(f"  Montant USD: {depense.montant_usd}")
        print(f"  Banque: {depense.banque.nom_banque if depense.banque else 'NULL'}")
    
    # 7. Chèques
    print("\n💳 CHÈQUES")
    print("-" * 40)
    cheques = Cheque.objects.all()
    print(f"Total: {cheques.count()} chèques")
    
    for cheque in cheques:
        print(f"\n• {cheque.numero_cheque} (PK: {cheque.pk})")
        print(f"  Relevé: {cheque.releve_depense.numero if cheque.releve_depense else 'NULL'}")
        print(f"  Banque: {cheque.banque.nom_banque if cheque.banque else 'NULL'}")
        print(f"  Montant CDF: {cheque.montant_cdf}")
        print(f"  Montant USD: {cheque.montant_usd}")
        print(f"  Bénéficiaire: {cheque.beneficiaire}")
        print(f"  Statut: {cheque.statut}")
    
    # 8. Vérification des cohérences
    print("\n🔍 VÉRIFICATION DES COHÉRENCES")
    print("-" * 40)
    
    # Vérifier les références nulles
    demandes_sans_service = DemandePaiement.objects.filter(service_demandeur__isnull=True)
    if demandes_sans_service.exists():
        print(f"⚠️  {demandes_sans_service.count()} demandes sans service")
    
    demandes_sans_nomenclature = DemandePaiement.objects.filter(nomenclature__isnull=True)
    if demandes_sans_nomenclature.exists():
        print(f"⚠️  {demandes_sans_nomenclature.count()} demandes sans nomenclature")
    
    demandes_sans_nature = DemandePaiement.objects.filter(nature_economique__isnull=True)
    if demandes_sans_nature.exists():
        print(f"⚠️  {demandes_sans_nature.count()} demandes sans nature économique")
    
    # Vérifier les montants négatifs ou nuls
    demandes_montant_nul = DemandePaiement.objects.filter(montant__lte=0)
    if demandes_montant_nul.exists():
        print(f"⚠️  {demandes_montant_nul.count()} demandes avec montant nul ou négatif")
    
    print("\n✅ Diagnostic terminé !")

if __name__ == "__main__":
    diagnostic_complet()
