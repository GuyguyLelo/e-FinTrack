#!/usr/bin/env python
"""
Script pour créer des données de test pour toutes les tables sauf paiements et utilisateurs
"""
import os
import django
from decimal import Decimal
from datetime import date, timedelta, datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

# Import des modèles
from accounts.models import Service
from banques.models import Banque, CompteBancaire
from demandes.models import NomenclatureDepense, NatureEconomique, DemandePaiement, ReleveDepense, Depense, Cheque
from recettes.models import Recette
from releves.models import ReleveBancaire, MouvementBancaire
from rapprochements.models import RapprochementBancaire

def create_test_data():
    """Créer des données de test pour toutes les tables"""
    
    print("Création des données de test...")
    
    # 1. Services (compléter les services existants)
    print("\n1. Services...")
    services_data = [
        {'nom_service': 'Direction Administrative', 'description': 'Gestion administrative', 'actif': True},
        {'nom_service': 'Direction Technique', 'description': 'Gestion technique', 'actif': True},
        {'nom_service': 'Direction Commerciale', 'description': 'Gestion commerciale', 'actif': True},
    ]
    
    services = []
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            nom_service=service_data['nom_service'],
            defaults=service_data
        )
        services.append(service)
        print(f"  - {service.nom_service} {'(créé)' if created else '(existe déjà)'}")
    
    # 2. Banques
    print("\n2. Banques...")
    banques_data = [
        {'nom_banque': 'BCDC', 'adresse': 'Kinshasa, Avenue des Aviateurs', 'telephone': '+243812345678', 'email': 'contact@bcdc.cd'},
        {'nom_banque': 'TMB', 'adresse': 'Kinshasa, Boulevard du 30 Juin', 'telephone': '+243812345679', 'email': 'contact@tmb.cd'},
        {'nom_banque': 'RAWBANK', 'adresse': 'Kinshasa, Avenue de la Justice', 'telephone': '+243812345680', 'email': 'contact@rawbank.cd'},
    ]
    
    banques = []
    for banque_data in banques_data:
        banque, created = Banque.objects.get_or_create(
            nom_banque=banque_data['nom_banque'],
            defaults=banque_data
        )
        banques.append(banque)
        print(f"  - {banque.nom_banque} {'(créée)' if created else '(existe déjà)'}")
    
    # 3. Comptes bancaires
    print("\n3. Comptes bancaires...")
    comptes_data = [
        {'banque': banques[0], 'numero_compte': 'BCDC001', 'intitule_compte': 'Compte principal DGRAD', 'solde_initial': Decimal('50000000.00'), 'devise': 'CDF', 'date_ouverture': date(2023, 1, 1), 'actif': True},
        {'banque': banques[1], 'numero_compte': 'TMB001', 'intitule_compte': 'Compte USD DGRAD', 'solde_initial': Decimal('25000000.00'), 'devise': 'USD', 'date_ouverture': date(2023, 1, 1), 'actif': True},
        {'banque': banques[2], 'numero_compte': 'RAW001', 'intitule_compte': 'Compte reserve DGRAD', 'solde_initial': Decimal('15000000.00'), 'devise': 'CDF', 'date_ouverture': date(2023, 1, 1), 'actif': True},
    ]
    
    comptes = []
    for compte_data in comptes_data:
        compte, created = CompteBancaire.objects.get_or_create(
            numero_compte=compte_data['numero_compte'],
            defaults=compte_data
        )
        comptes.append(compte)
        print(f"  - {compte.numero_compte} {'(créé)' if created else '(existe déjà)'}")
    
    # 4. Nomenclatures de dépenses
    print("\n4. Nomenclatures de dépenses...")
    nomenclatures_data = [
        {'annee': 2024, 'date_publication': date(2024, 1, 15), 'statut': 'EN_COURS'},
        {'annee': 2023, 'date_publication': date(2023, 1, 10), 'statut': 'DEPASSE'},
        {'annee': 2025, 'date_publication': date(2025, 1, 20), 'statut': 'EN_COURS'},
    ]
    
    nomenclatures = []
    for nom_data in nomenclatures_data:
        nom, created = NomenclatureDepense.objects.get_or_create(
            annee=nom_data['annee'],
            date_publication=nom_data['date_publication'],
            defaults=nom_data
        )
        nomenclatures.append(nom)
        print(f"  - Nomenclature {nom.annee} {'(créée)' if created else '(existe déjà)'}")
    
    # 5. Natures économiques
    print("\n5. Natures économiques...")
    natures_data = [
        {'code': '1.1.1', 'titre': 'Frais de personnel', 'description': 'Salaires et primes'},
        {'code': '1.2.1', 'titre': 'Frais de fonctionnement', 'description': 'Frais courants'},
        {'code': '2.1.1', 'titre': 'Investissements', 'description': 'Acquisitions d\'équipements'},
        {'code': '1.1.2', 'titre': 'Frais de formation', 'description': 'Formations du personnel'},
        {'code': '1.2.2', 'titre': 'Frais de transport', 'description': 'Déplacements et missions'},
        {'code': '2.1.2', 'titre': 'Investissements informatiques', 'description': 'Matériel informatique'},
    ]
    
    natures = []
    for nature_data in natures_data:
        nature, created = NatureEconomique.objects.get_or_create(
            code=nature_data['code'],
            defaults=nature_data
        )
        natures.append(nature)
        print(f"  - {nature.code} - {nature.titre} {'(créée)' if created else '(existe déjà)'}")
    
    # 6. Demandes de paiement
    print("\n6. Demandes de paiement...")
    from accounts.models import User
    
    # Récupérer quelques utilisateurs existants
    dg_user = User.objects.filter(role='DG').first()
    daf_user = User.objects.filter(role='DAF').first()
    chef_service_user = User.objects.filter(role='CHEF_SERVICE').first()
    
    demandes_data = [
        {
            'service_demandeur': services[0],
            'nomenclature': nomenclatures[0],
            'nature_economique': natures[0],
            'description': 'Paiement des salaires du mois de Janvier 2024',
            'montant': Decimal('15000000.00'),
            'devise': 'CDF',
            'date_demande': date(2024, 1, 15),
            'statut': 'VALIDEE_DG',
            'cree_par': chef_service_user,
            'approuve_par': dg_user,
            'date_approbation': datetime(2024, 1, 16, 10, 30),
        },
        {
            'service_demandeur': services[1],
            'nomenclature': nomenclatures[0],
            'nature_economique': natures[1],
            'description': 'Achat de matériel de bureau',
            'montant': Decimal('2500.00'),
            'devise': 'USD',
            'date_demande': date(2024, 1, 20),
            'statut': 'VALIDEE_DF',
            'cree_par': chef_service_user,
            'approuve_par': daf_user,
            'date_approbation': datetime(2024, 1, 21, 14, 15),
        },
        {
            'service_demandeur': services[2],
            'nomenclature': nomenclatures[1],
            'nature_economique': natures[2],
            'description': 'Acquisition de nouveaux ordinateurs',
            'montant': Decimal('8000.00'),
            'devise': 'USD',
            'date_demande': date(2023, 12, 10),
            'statut': 'EN_ATTENTE',
            'cree_par': chef_service_user,
        },
        {
            'service_demandeur': services[0],
            'nomenclature': nomenclatures[2],
            'nature_economique': natures[3],
            'description': 'Formation du personnel sur les nouvelles procédures',
            'montant': Decimal('5000.00'),
            'devise': 'USD',
            'date_demande': date(2024, 2, 5),
            'statut': 'VALIDEE_DG',
            'cree_par': chef_service_user,
            'approuve_par': dg_user,
            'date_approbation': datetime(2024, 2, 6, 9, 45),
        },
        {
            'service_demandeur': services[1],
            'nomenclature': nomenclatures[0],
            'nature_economique': natures[4],
            'description': 'Mission à Lubumbashi pour inspection',
            'montant': Decimal('3500000.00'),
            'devise': 'CDF',
            'date_demande': date(2024, 1, 25),
            'statut': 'VALIDEE_DF',
            'cree_par': chef_service_user,
            'approuve_par': daf_user,
            'date_approbation': datetime(2024, 1, 26, 11, 20),
        },
        {
            'service_demandeur': services[2],
            'nomenclature': nomenclatures[2],
            'nature_economique': natures[5],
            'description': 'Serveurs et équipements réseau',
            'montant': Decimal('12000.00'),
            'devise': 'USD',
            'date_demande': date(2024, 2, 10),
            'statut': 'EN_ATTENTE',
            'cree_par': chef_service_user,
        },
    ]
    
    demandes = []
    for demande_data in demandes_data:
        demande, created = DemandePaiement.objects.get_or_create(
            description=demande_data['description'],
            service_demandeur=demande_data['service_demandeur'],
            defaults=demande_data
        )
        demandes.append(demande)
        print(f"  - {demande.reference} - {demande.description[:50]}... {'(créée)' if created else '(existe déjà)'}")
    
    # 7. Relevés de dépenses
    print("\n7. Relevés de dépenses...")
    releves_data = [
        {
            'periode': date(2024, 1, 31),
            'observation': 'Relevé des dépenses de Janvier 2024',
            'valide_par': daf_user,
        },
        {
            'periode': date(2023, 12, 31),
            'observation': 'Relevé des dépenses de Décembre 2023',
            'valide_par': daf_user,
        },
        {
            'periode': date(2024, 2, 29),
            'observation': 'Relevé des dépenses de Février 2024',
            'valide_par': dg_user,
        },
    ]
    
    releves = []
    for releve_data in releves_data:
        releve, created = ReleveDepense.objects.get_or_create(
            periode=releve_data['periode'],
            defaults=releve_data
        )
        releves.append(releve)
        print(f"  - {releve.numero or 'En cours'} - {releve.periode} {'(créé)' if created else '(existe déjà)'}")
    
    # Ajouter des demandes aux relevés
    if len(releves) >= 2 and len(demandes) >= 4:
        releves[0].demandes.add(demandes[0], demandes[1])  # Janvier 2024
        releves[1].demandes.add(demandes[2])  # Décembre 2023
        releves[2].demandes.add(demandes[3], demandes[4])  # Février 2024
        
        # Calculer les totaux
        for releve in releves:
            releve.calculer_total()
            print(f"    -> {len(releve.demandes.all())} demandes ajoutées au relevé de {releve.periode}")
    
    # 8. Dépenses historiques
    print("\n8. Dépenses historiques...")
    depenses_data = [
        {
            'code_depense': 'DEP-2024-001',
            'mois': 1,
            'annee': 2024,
            'date_depense': date(2024, 1, 20),
            'nomenclature': nomenclatures[0],
            'libelle_depenses': 'Achat de fournitures de bureau',
            'banque': banques[0],
            'montant_fc': Decimal('2500000.00'),
            'montant_usd': Decimal('0.00'),
            'observation': 'Fournitures pour le trimestre',
        },
        {
            'code_depense': 'DEP-2024-002',
            'mois': 1,
            'annee': 2024,
            'date_depense': date(2024, 1, 25),
            'nomenclature': nomenclatures[0],
            'libelle_depenses': 'Maintenance des véhicules',
            'banque': banques[1],
            'montant_fc': Decimal('0.00'),
            'montant_usd': Decimal('1500.00'),
            'observation': 'Entretien mensuel',
        },
        {
            'code_depense': 'DEP-2023-012',
            'mois': 12,
            'annee': 2023,
            'date_depense': date(2023, 12, 15),
            'nomenclature': nomenclatures[1],
            'libelle_depenses': 'Achat d\'ordinateurs',
            'banque': banques[2],
            'montant_fc': Decimal('0.00'),
            'montant_usd': Decimal('8000.00'),
            'observation': 'Renouvellement du parc informatique',
        },
    ]
    
    depenses = []
    for depense_data in depenses_data:
        depense, created = Depense.objects.get_or_create(
            code_depense=depense_data['code_depense'],
            defaults=depense_data
        )
        depenses.append(depense)
        print(f"  - {depense.code_depense} - {depense.libelle_depenses[:50]}... {'(créée)' if created else '(existe déjà)'}")
    
    # 9. Chèques
    print("\n9. Chèques...")
    if len(releves) >= 2 and len(banques) >= 2:
        cheques_data = [
            {
                'releve_depense': releves[0],
                'banque': banques[0],
                'montant_cdf': releves[0].net_a_payer_cdf,
                'montant_usd': Decimal('0.00'),
                'date_emission': date.today(),
                'beneficiaire': 'Fournisseur A',
                'observation': 'Paiement des factures de Janvier',
                'cree_par': daf_user,
            },
            {
                'releve_depense': releves[1],
                'banque': banques[1],
                'montant_cdf': Decimal('0.00'),
                'montant_usd': releves[1].net_a_payer_usd,
                'date_emission': date.today(),
                'beneficiaire': 'Fournisseur B',
                'observation': 'Paiement des investissements',
                'cree_par': daf_user,
            },
            {
                'releve_depense': releves[2],
                'banque': banques[2],
                'montant_cdf': releves[2].net_a_payer_cdf,
                'montant_usd': releves[2].net_a_payer_usd,
                'date_emission': date.today(),
                'beneficiaire': 'Fournisseur C',
                'observation': 'Paiement multiple',
                'cree_par': dg_user,
            },
        ]
        
        cheques = []
        for cheque_data in cheques_data:
            cheque, created = Cheque.objects.get_or_create(
                releve_depense=cheque_data['releve_depense'],
                defaults=cheque_data
            )
            cheques.append(cheque)
            print(f"  - {cheque.numero_cheque or 'En cours'} {'(créé)' if created else '(existe déjà)'}")
    
    # 10. Recettes
    print("\n10. Recettes...")
    recettes_data = [
        {
            'reference': 'REC-2024-001',
            'banque': banques[0],
            'compte_bancaire': comptes[0],
            'source_recette': 'DROITS_ADMINISTRATIFS',
            'description': 'Collecte des taxes de Janvier',
            'montant_cdf': Decimal('50000000.00'),
            'montant_usd': Decimal('0.00'),
            'date_encaissement': date(2024, 1, 15),
            'valide': True,
            'enregistre_par': dg_user,
            'valide_par': daf_user,
        },
        {
            'reference': 'REC-2024-002',
            'banque': banques[1],
            'compte_bancaire': comptes[1],
            'source_recette': 'REDEVANCES',
            'description': 'Redevances des licences',
            'montant_cdf': Decimal('0.00'),
            'montant_usd': Decimal('15000.00'),
            'date_encaissement': date(2024, 1, 20),
            'valide': True,
            'enregistre_par': daf_user,
            'valide_par': dg_user,
        },
        {
            'reference': 'REC-2023-012',
            'banque': banques[2],
            'compte_bancaire': comptes[2],
            'source_recette': 'AUTRES',
            'description': 'Amendes de Décembre',
            'montant_cdf': Decimal('0.00'),
            'montant_usd': Decimal('8000.00'),
            'date_encaissement': date(2023, 12, 28),
            'valide': True,
            'enregistre_par': dg_user,
            'valide_par': daf_user,
        },
    ]
    
    recettes = []
    for recette_data in recettes_data:
        recette, created = Recette.objects.get_or_create(
            reference=recette_data['reference'],
            defaults=recette_data
        )
        recettes.append(recette)
        print(f"  - {recette.reference} - {recette.source_recette} {'(créée)' if created else '(existe déjà)'}")
    
    # 11. Relevés bancaires
    print("\n11. Relevés bancaires...")
    releves_bancaires_data = [
        {
            'banque': banques[0],
            'compte_bancaire': comptes[0],
            'periode_debut': date(2024, 1, 1),
            'periode_fin': date(2024, 1, 31),
            'total_recettes': Decimal('50000000.00'),
            'total_depenses': Decimal('8000000.00'),
            'observations': 'Relevé BCDC Janvier 2024',
            'saisi_par': chef_service_user,
        },
        {
            'banque': banques[1],
            'compte_bancaire': comptes[1],
            'periode_debut': date(2024, 1, 1),
            'periode_fin': date(2024, 1, 31),
            'total_recettes': Decimal('15000000.00'),
            'total_depenses': Decimal('1500000.00'),
            'observations': 'Relevé TMB Janvier 2024',
            'saisi_par': chef_service_user,
        },
        {
            'banque': banques[2],
            'compte_bancaire': comptes[2],
            'periode_debut': date(2023, 12, 1),
            'periode_fin': date(2023, 12, 31),
            'total_recettes': Decimal('10000000.00'),
            'total_depenses': Decimal('1000000.00'),
            'observations': 'Relevé RAWBANK Décembre 2023',
            'saisi_par': chef_service_user,
        },
    ]
    
    releves_bancaires = []
    for rb_data in releves_bancaires_data:
        rb, created = ReleveBancaire.objects.get_or_create(
            banque=rb_data['banque'],
            compte_bancaire=rb_data['compte_bancaire'],
            periode_debut=rb_data['periode_debut'],
            periode_fin=rb_data['periode_fin'],
            defaults=rb_data
        )
        releves_bancaires.append(rb)
        print(f"  - {rb.banque.nom_banque} {rb.periode_debut} au {rb.periode_fin} {'(créé)' if created else '(existe déjà)'}")
    
    # 12. Mouvements bancaires
    print("\n12. Mouvements bancaires...")
    if len(releves_bancaires) >= 2 and len(recettes) >= 2 and len(demandes) >= 2:
        mouvements_data = [
            {
                'releve': releves_bancaires[0],
                'type_mouvement': 'DEPENSE',
                'reference_operation': 'BCD-001',
                'description': 'Paiement fournisseur A',
                'montant': Decimal('3000000.00'),
                'date_operation': date(2024, 1, 15),
                'beneficiaire_ou_source': 'Fournisseur A',
                'lie_a_recette': None,
                'lie_a_demande': demandes[0],
            },
            {
                'releve': releves_bancaires[1],
                'type_mouvement': 'RECETTE',
                'reference_operation': 'TMB-001',
                'description': 'Encaissement client B',
                'montant': Decimal('15000.00'),
                'date_operation': date(2024, 1, 20),
                'beneficiaire_ou_source': 'Client B',
                'lie_a_recette': recettes[1],
                'lie_a_demande': None,
            },
            {
                'releve': releves_bancaires[2],
                'type_mouvement': 'DEPENSE',
                'reference_operation': 'RAW-001',
                'description': 'Achat équipement',
                'montant': Decimal('8000.00'),
                'date_operation': date(2023, 12, 15),
                'beneficiaire_ou_source': 'Fournisseur informatique',
                'lie_a_recette': None,
                'lie_a_demande': demandes[2],
            },
        ]
        
        mouvements = []
        for mv_data in mouvements_data:
            mv, created = MouvementBancaire.objects.get_or_create(
                reference_operation=mv_data['reference_operation'],
                releve=mv_data['releve'],
                defaults=mv_data
            )
            mouvements.append(mv)
            print(f"  - {mv.reference_operation} - {mv.description[:40]}... {'(créé)' if created else '(existe déjà)'}")
    
    # 13. Rapprochements bancaires
    print("\n13. Rapprochements bancaires...")
    if len(releves_bancaires) >= 2 and len(mouvements) >= 2:
        rapprochements_data = [
            {
                'banque': releves_bancaires[0].banque,
                'compte_bancaire': releves_bancaires[0].compte_bancaire,
                'periode_mois': 1,
                'periode_annee': 2024,
                'solde_banque': Decimal('42000000.00'),
                'solde_interne': Decimal('41950000.00'),
                'releve_bancaire': releves_bancaires[0],
                'observateur': daf_user,
                'commentaire': 'Petit écart à analyser',
                'valide': False,
            },
            {
                'banque': releves_bancaires[1].banque,
                'compte_bancaire': releves_bancaires[1].compte_bancaire,
                'periode_mois': 1,
                'periode_annee': 2024,
                'solde_banque': Decimal('23500000.00'),
                'solde_interne': Decimal('23500000.00'),
                'releve_bancaire': releves_bancaires[1],
                'observateur': dg_user,
                'commentaire': 'Rapprochement parfait',
                'valide': True,
            },
            {
                'banque': releves_bancaires[2].banque,
                'compte_bancaire': releves_bancaires[2].compte_bancaire,
                'periode_mois': 12,
                'periode_annee': 2023,
                'solde_banque': Decimal('14000000.00'),
                'solde_interne': Decimal('13980000.00'),
                'releve_bancaire': releves_bancaires[2],
                'observateur': daf_user,
                'commentaire': 'Écart en cours d\'investigation',
                'valide': False,
            },
        ]
        
        rapprochements = []
        for rapp_data in rapprochements_data:
            rapp, created = RapprochementBancaire.objects.get_or_create(
                banque=rapp_data['banque'],
                compte_bancaire=rapp_data['compte_bancaire'],
                periode_mois=rapp_data['periode_mois'],
                periode_annee=rapp_data['periode_annee'],
                defaults=rapp_data
            )
            rapprochements.append(rapp)
            print(f"  - {rapp.banque.nom_banque} {rapp.periode_mois}/{rapp.periode_annee} {'(créé)' if created else '(existe déjà)'}")
    
    print("\n✅ Données de test créées avec succès !")
    print("\nRésumé des données créées :")
    print(f"- Services: {len(services)}")
    print(f"- Banques: {len(banques)}")
    print(f"- Comptes bancaires: {len(comptes)}")
    print(f"- Nomenclatures: {len(nomenclatures)}")
    print(f"- Natures économiques: {len(natures)}")
    print(f"- Demandes de paiement: {len(demandes)}")
    print(f"- Relevés de dépenses: {len(releves)}")
    print(f"- Dépenses: {len(depenses)}")
    print(f"- Chèques: {len(cheques) if 'cheques' in locals() else 0}")
    print(f"- Recettes: {len(recettes)}")
    print(f"- Relevés bancaires: {len(releves_bancaires)}")
    print(f"- Mouvements bancaires: {len(mouvements) if 'mouvements' in locals() else 0}")
    print(f"- Rapprochements bancaires: {len(rapprochements) if 'rapprochements' in locals() else 0}")

if __name__ == '__main__':
    create_test_data()
