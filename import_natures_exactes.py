#!/usr/bin/env python
"""
Script pour importer les natures économiques selon la structure exacte fournie
Basé sur la Nomenclature Budgétaire RDC 2015 - Structure hiérarchique complète
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from demandes.models import NatureEconomique

def importer_natures_economiques():
    """Importe les natures économiques avec la structure exacte fournie"""
    
    # Structure exacte basée sur les données fournies
    # Format: (code, titre, code_parent, description)
    natures_data = [
        # NIVEAU 1 - Catégories principales
        ("1", "DETTE PUBLIQUE EN CAPITAL", None, "Ensemble des engagements financiers de l'Etat"),
        ("2", "FRAIS FINANCIERS", None, "Coûts liés aux emprunts et services de la dette"),
        ("3", "DEPENSES DE PERSONNEL", None, "Rémunérations et avantages du personnel"),
        ("4", "BIENS ET MATERIELS", None, "Acquisition de biens matériels et équipements"),
        ("5", "SERVICES", None, "Prestations de services et frais divers"),
        ("6", "TRANSFERTS ET INTERVENTIONS", None, "Transferts vers tiers et interventions de l'Etat"),
        ("7", "ACQUISITION D'EQUIPEMENTS", None, "Acquisition d'équipements durables"),
        ("8", "CONSTRUCTIONS ET REHABILITATIONS", None, "Travaux de construction et rénovation"),
        ("9", "PRETS ET AVANCES", None, "Prêts et avances consentis par l'Etat"),
        
        # NIVEAU 2 - Sous-catégories (Dette publique)
        ("1-171", "DETTES INTERIEURES", "1", "Ensemble des engagements régulièrement contractés par l'Etat vis-à-vis des créanciers résidents"),
        ("1-162", "DETTES EXTERIEURES", "1", "Ensemble des engagements régulièrement contractés par l'Etat vis-à-vis des créanciers étrangers"),
        
        # NIVEAU 2 - Sous-catégories (Frais financiers)
        ("2-211", "Intérêts sur la dette intérieure", "2", None),
        ("2-212", "Intérêts moratoires", "2", None),
        ("2-213", "Intérêts titrisés", "2", None),
        ("2-221", "Intérêts sur Club de Paris", "2", None),
        ("2-222", "Intérêts sur Club de Londres", "2", None),
        ("2-223", "Intérêts sur Club de Kinshasa", "2", None),
        ("2-224", "Intérêts sur la dette multilatérale", "2", None),
        
        # NIVEAU 2 - Sous-catégories (Dépenses de personnel)
        ("3-311", "Traitement de base du personnel permanent", "3", None),
        ("3-312", "Traitement de base du personnel contractuel", "3", None),
        ("3-321", "Indemnités de transport", "3", None),
        ("3-322", "Indemnités de logement", "3", None),
        ("3-323", "Primes et indemnités permanentes", "3", None),
        ("3-324", "Indemnités de sortie et de fin de carrière", "3", None),
        ("3-325", "Primes et indemnités non permanentes", "3", None),
        ("3-326", "Frais d'installation ou d'équipement", "3", None),
        ("3-327", "Frais de rapatriement et de mutation", "3", None),
        ("3-328", "Indemnités kilométriques", "3", None),
        
        # NIVEAU 2 - Sous-catégories (Biens et matériels)
        ("4-411", "Fournitures et petits matériels", "4", None),
        ("4-414", "Produits médicaux, pharmaceutiques et vétérinaires", "4", None),
        ("4-421", "Pièces de rechange pour matériels roulants", "4", None),
        ("4-422", "Pièces de rechange pour autres équipements", "4", None),
        ("4-431", "Produits chimiques et organiques", "4", None),
        ("4-432", "Carburants et lubrifiants", "4", None),
        ("4-433", "Semences agricoles et produits agro-alimentaires", "4", None),
        
        # NIVEAU 2 - Sous-catégories (Services)
        ("5-511", "Communication et télécommunication", "5", None),
        ("5-521", "Publicité et communiqué", "5", None),
        ("5-522", "Impression, reproduction et reliure", "5", None),
        ("5-532", "Titres de voyage intérieur et extérieur", "5", None),
        ("5-541", "Location immobilière", "5", None),
        ("5-542", "Frais d'hébergement", "5", None),
        ("5-543", "Location d'équipements et matériels", "5", None),
        ("5-551", "Entretien et réparation de matériels", "5", None),
        ("5-571", "Entretien et réparation d'édifices", "5", None),
        ("5-583", "Frais de mission", "5", None),
        ("5-585", "Assurances", "5", None),
        ("5-586", "Prestations intellectuelles et études", "5", None),
        
        # NIVEAU 2 - Sous-catégories (Transferts et interventions)
        ("6-613", "Subventions aux institutions financières", "6", None),
        ("6-615", "Subventions aux entreprises publiques et para-publiques", "6", None),
        ("6-664", "Subventions et transferts", "6", None),
        
        # NIVEAU 2 - Sous-catégories (Acquisition d'équipements)
        ("7-711", "Mobilier et équipements de bureau", "7", None),
        ("7-712", "Equipements informatiques", "7", None),
        ("7-721", "Equipements médico-chirurgicaux", "7", None),
        ("7-731", "Equipements éducatifs, culturels et sportifs", "7", None),
        ("7-741", "Equipements agro-sylvo-pastoraux", "7", None),
        ("7-742", "Equipements industriels et électriques", "7", None),
        ("7-753", "Equipements de transport", "7", None),
        ("7-761", "Equipements de télécommunication", "7", None),
        ("7-762", "Equipements audio-visuels", "7", None),
        ("7-719", "Equipements divers", "7", None),
        
        # NIVEAU 2 - Sous-catégories (Constructions et réhabilitations)
        ("8-232", "Construction d'édifices et bâtiments", "8", None),
        ("8-2322", "Construction d'ouvrages hydrauliques et hydro-électriques", "8", None),
        ("8-2323", "Construction de routes, ponts, ports, aéroports et rails", "8", None),
        ("8-2324", "Construction de lignes électriques et téléphoniques", "8", None),
        ("8-2328", "Constructions diverses", "8", None),
        ("8-233", "Réhabilitation et réfection d'ouvrages", "8", None),
        
        # NIVEAU 2 - Sous-catégories (Prêts et avances)
        ("9-271", "Prêts et avances", "9", "Fonds consentis par l'Etat à une personne physique ou morale de droit public (province, ETD, établissement public, agent de l'Etat)"),
        
        # NIVEAU 3 - Sous-sous-catégories (Dettes intérieures)
        ("1-1711", "Dette Sociale", "1-171", "- Arriérés sur les dépenses de personnel en monnaie nationale\n- Arriérés sur les condamnations judiciaires et indemnisations\n- Arriérés sur les dépenses de personnel en devise"),
        ("1-1712", "Dette Commerciale", "1-171", "- Arriérés envers des fournisseurs de biens et prestations\n- Arriérés envers des entrepreneurs de travaux publics\n- Arriérés de loyers"),
        ("1-1713", "Dette Financière", "1-171", "- Certificats de dépôts en monnaie nationale\n- Bons du Trésor et billets de trésorerie\n- Avances consenties par les tiers à l'Etat\n- Arriérés de remboursement d'intérêts débiteurs consolidés BCC"),
        
        # NIVEAU 3 - Sous-sous-catégories (Dettes extérieures)
        ("1-1621", "Club de Paris", "1-162", "Dette envers les créanciers bilatéraux institutionnels (Etats et agences gouvernementales)"),
        ("1-1622", "Club de Londres", "1-162", "Dette envers les créanciers banquiers adhérents"),
        ("1-1623", "Club de Kinshasa", "1-162", "Créanciers autres que les clubs de Paris et de Londres\ny compris ceux dont la dette est née de la zaïrianisation"),
        ("1-1624", "Dette Multilatérale", "1-162", "Dette envers les institutions financières internationales\n(Banque Mondiale, FMI, etc.)"),
        
        # NIVEAU 3 - Sous-sous-catégories (Réhabilitations)
        ("8-2331", "Réhabilitation d'édifices", "8-233", None),
        ("8-2332", "Réhabilitation d'ouvrages hydrauliques", "8-233", None),
        ("8-2333", "Réhabilitation de routes et ouvrages de transport", "8-233", None),
    ]
    
    print("Début de l'import des natures économiques...")
    print("=" * 60)
    
    created_count = 0
    error_count = 0
    
    # Créer un dictionnaire pour mapper les codes aux objets créés
    nature_map = {}
    
    # Importer par ordre hiérarchique pour s'assurer que les parents existent
    for code, titre, code_parent, description in natures_data:
        try:
            # Trouver le parent si code_parent est spécifié
            parent = None
            if code_parent:
                parent = nature_map.get(code_parent)
                if not parent:
                    # Essayer de trouver dans la base de données
                    try:
                        parent = NatureEconomique.objects.get(code=code_parent)
                    except NatureEconomique.DoesNotExist:
                        print(f"⚠️  Parent non trouvé: {code_parent} pour {code}")
                        error_count += 1
                        continue
            
            # Créer la nature
            nature = NatureEconomique.objects.create(
                code=code,
                titre=titre,
                code_parent=code_parent,
                parent=parent,
                description=description,
                active=True
            )
            
            # Ajouter au mapping
            nature_map[code] = nature
            created_count += 1
            
            print(f"✅ Créé: {code} - {titre}")
            if parent:
                print(f"   └─ Parent: {parent.code} - {parent.titre}")
            if description:
                # Afficher seulement les 100 premiers caractères de la description
                desc_preview = description[:100] + "..." if len(description) > 100 else description
                print(f"   📝 {desc_preview}")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'import de {code}: {str(e)}")
            error_count += 1
    
    print("=" * 60)
    print(f"Import terminé:")
    print(f"  - {created_count} natures créées")
    print(f"  - {error_count} erreurs")
    print(f"  - Total: {NatureEconomique.objects.count()} natures économiques")
    
    # Vérification de la structure
    print("\nVérification de la structure hiérarchique:")
    print("=" * 40)
    
    # Afficher les catégories principales
    categories = NatureEconomique.objects.filter(parent__isnull=True, active=True).order_by('code')
    for cat in categories:
        print(f"📁 {cat.code} - {cat.titre}")
        
        # Afficher les sous-catégories
        sub_cats = NatureEconomique.objects.filter(parent=cat, active=True).order_by('code')
        for sub_cat in sub_cats:
            print(f"   📂 {sub_cat.code} - {sub_cat.titre}")
            
            # Afficher les sous-sous-catégories
            sub_sub_cats = NatureEconomique.objects.filter(parent=sub_cat, active=True).order_by('code')
            for sub_sub_cat in sub_sub_cats:
                print(f"      📄 {sub_sub_cat.code} - {sub_sub_cat.titre}")

if __name__ == "__main__":
    importer_natures_economiques()
