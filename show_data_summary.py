#!/usr/bin/env python
"""
Script pour afficher un résumé complet des données du projet e-FinTrack
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User, Service
from banques.models import Banque, CompteBancaire
from demandes.models import DemandePaiement, ReleveDepense, Depense, NatureEconomique
from recettes.models import Recette
from releves.models import ReleveBancaire, MouvementBancaire
from rapprochements.models import RapprochementBancaire

def afficher_resume():
    """Affiche un résumé complet des données"""
    
    print("=" * 80)
    print("📊 RÉSUMÉ COMPLET DES DONNÉES E-FINTRACK")
    print("=" * 80)
    
    # Utilisateurs et Services
    print("\n👥 UTILISATEURS ET SERVICES")
    print("-" * 40)
    services = Service.objects.all()
    users = User.objects.all()
    
    print(f"Services: {services.count()}")
    for service in services:
        print(f"  • {service.nom_service} ({service.membres.count()} membres)")
    
    print(f"\nUtilisateurs: {users.count()}")
    for user in users[:10]:  # Limiter à 10 pour la lisibilité
        print(f"  • {user.username} - {user.get_role_display()} - {user.service}")
    
    # Banques et Comptes
    print("\n🏦 BANQUES ET COMPTES")
    print("-" * 40)
    banques = Banque.objects.all()
    comptes = CompteBancaire.objects.all()
    
    print(f"Banques: {banques.count()}")
    for banque in banques:
        print(f"  • {banque.nom_banque} ({banque.comptes.count()} comptes)")
        for compte in banque.comptes.all():
            print(f"    - {compte.intitule_compte} ({compte.devise}): {compte.solde_courant} {compte.devise}")
    
    # Demandes de Paiement
    print("\n💸 DEMANDES DE PAIEMENT")
    print("-" * 40)
    demandes = DemandePaiement.objects.all()
    releves_dep = ReleveDepense.objects.all()
    
    print(f"Demandes de paiement: {demandes.count()}")
    for demande in demandes:
        print(f"  • {demande.reference} - {demande.montant} {demande.devise} - {demande.get_statut_display()}")
        print(f"    {demande.description[:60]}...")
    
    print(f"\nRelevés de dépenses: {releves_dep.count()}")
    for releve in releves_dep:
        print(f"  • {releve.numero} - Net: {releve.get_total_general()} USD")
    
    # Natures Économiques
    print("\n📋 NATURES ÉCONOMIQUES")
    print("-" * 40)
    natures = NatureEconomique.objects.all()
    print(f"Natures économiques: {natures.count()}")
    for nature in natures:
        print(f"  • {nature.code} - {nature.titre}")
    
    # Recettes
    print("\n💰 RECETTES")
    print("-" * 40)
    recettes = Recette.objects.all()
    
    print(f"Recettes: {recettes.count()}")
    total_usd = sum(r.montant_usd for r in recettes)
    total_cdf = sum(r.montant_cdf for r in recettes)
    print(f"Total USD: {total_usd:,.2f}")
    print(f"Total CDF: {total_cdf:,.2f}")
    
    for recette in recettes:
        statut = "✅ Validée" if recette.valide else "⏳ En attente"
        print(f"  • {recette.reference} - {recette.montant_usd} USD / {recette.montant_cdf} CDF - {statut}")
        print(f"    {recette.description[:50]}...")
    
    # Relevés Bancaires
    print("\n📄 RELEVÉS BANCAIRES")
    print("-" * 40)
    releves = ReleveBancaire.objects.all()
    mouvements = MouvementBancaire.objects.all()
    
    print(f"Relevés bancaires: {releves.count()}")
    for releve in releves:
        statut = "✅ Validé" if releve.valide else "⏳ En attente"
        print(f"  • {releve.banque.nom_banque} ({releve.devise}) - {statut}")
        print(f"    Période: {releve.periode_debut} au {releve.periode_fin}")
        print(f"    Solde: {releve.solde_banque} {releve.devise}")
    
    print(f"\nMouvements bancaires: {mouvements.count()}")
    for mouvement in mouvements[:5]:  # Limiter à 5 pour la lisibilité
        print(f"  • {mouvement.get_type_mouvement_display()} - {mouvement.montant} {mouvement.devise}")
        print(f"    {mouvement.description[:40]}...")
    
    # Rapprochements
    print("\n🔄 RAPPROCHEMENTS BANCAIRES")
    print("-" * 40)
    rapprochements = RapprochementBancaire.objects.all()
    
    print(f"Rapprochements: {rapprochements.count()}")
    for rappro in rapprochements:
        statut = "✅ Validé" if rappro.valide else "⏳ En attente"
        ecart_display = f"Écart: {rappro.ecart} {rappro.devise}" if rappro.ecart != 0 else "✅ Aucun écart"
        print(f"  • {rappro.banque.nom_banque} ({rappro.devise}) - {rappro.periode_mois}/{rappro.periode_annee}")
        print(f"    {statut} - {ecart_display}")
        if rappro.commentaire:
            print(f"    💬 {rappro.commentaire[:50]}...")
    
    # Statistiques générales
    print("\n📈 STATISTIQUES GÉNÉRALES")
    print("-" * 40)
    
    total_recettes_usd = sum(r.montant_usd for r in recettes)
    total_recettes_cdf = sum(r.montant_cdf for r in recettes)
    total_depenses_usd = sum(d.montant for d in demandes if d.devise == 'USD')
    total_depenses_cdf = sum(d.montant for d in demandes if d.devise == 'CDF')
    
    print(f"💰 Recettes totales:")
    print(f"    USD: {total_recettes_usd:,.2f}")
    print(f"    CDF: {total_recettes_cdf:,.2f}")
    
    print(f"\n💸 Dépenses totales (demandes):")
    print(f"    USD: {total_depenses_usd:,.2f}")
    print(f"    CDF: {total_depenses_cdf:,.2f}")
    
    print(f"\n🏦 Soldes bancaires:")
    for compte in comptes:
        print(f"    {compte.intitule_compte}: {compte.solde_courant} {compte.devise}")
    
    print("\n" + "=" * 80)
    print("✅ FIN DU RAPPORT - Toutes les données sont accessibles!")
    print("=" * 80)

if __name__ == "__main__":
    afficher_resume()
