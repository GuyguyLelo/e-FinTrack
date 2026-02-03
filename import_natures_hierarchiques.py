#!/usr/bin/env python
"""
Script pour importer les natures économiques depuis la Nomenclature Budgétaire RDC 2015
Pages 39 à 45 - Structure hiérarchique avec décalage
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from demandes.models import NatureEconomique

def importer_natures_economiques():
    """Importe les natures économiques avec structure hiérarchique"""
    
    # Structure basée sur la nomenclature budgétaire RDC 2015 (pages 39-45)
    # Format: (code, titre, code_parent)
    natures_data = [
        # NIVEAU 1 - Categories principales
        ("1", "DETTE PUBLIQUE", None),
        ("2", "FRAIS FINANCIERS", None),
        ("3", "DEPENSES DE PERSONNEL", None),
        ("4", "BIENS ET MATERIELS", None),
        ("5", "DEPENSES DE PRESTATIONS", None),
        ("6", "TRANSFERTS ET INTERVENTIONS DE L'ETAT", None),
        ("7", "EQUIPEMENTS", None),
        ("8", "CONSTRUCTIONS / REHABILITATION / ACQUISITIONS IMMOBILIERES", None),
        ("9", "PRETS ET AVANCES", None),
        
        # NIVEAU 2 - Sous-categories (décalées)
        # Dette publique
        ("1.1", "Dette intérieure", "1"),
        ("1.2", "Dette extérieure", "1"),
        
        # Frais financiers
        ("2.1", "Intérêts sur la dette intérieure", "2"),
        ("2.2", "Intérêts sur la dette extérieure", "2"),
        
        # Dépenses de personnel
        ("3.1", "Traitement de base du personnel", "3"),
        ("3.2", "Dépenses accessoires du personnel", "3"),
        
        # Biens et matériels
        ("4.1", "Fournitures et petits matériels", "4"),
        ("4.2", "Matériaux / pièces de rechange", "4"),
        ("4.3", "Produits chimiques / énergie / semences", "4"),
        ("4.4", "Matériels textiles", "4"),
        
        # Dépenses de prestations
        ("5.1", "Dépenses de base", "5"),
        ("5.2", "Publicité / impression", "5"),
        ("5.3", "Dépenses de transport", "5"),
        ("5.4", "Location immobilière / équipement", "5"),
        ("5.5", "Entretien et réparation matériel", "5"),
        ("5.6", "Soins vétérinaires et environnement", "5"),
        ("5.7", "Entretien ouvrages et édifices", "5"),
        ("5.8", "Autres services", "5"),
        
        # Transferts et interventions
        ("6.1", "Subventions", "6"),
        ("6.2", "Transferts", "6"),
        ("6.3", "Interventions de l'État", "6"),
        ("6.4", "Prestations sociales", "6"),
        
        # Équipements
        ("7.1", "Équipements et mobiliers", "7"),
        ("7.2", "Équipements de santé", "7"),
        ("7.3", "Équipements éducatifs / culturels / sportifs", "7"),
        ("7.4", "Équipements agro / industriels", "7"),
        ("7.5", "Équipements construction / transport", "7"),
        ("7.6", "Équipements de communication", "7"),
        ("7.7", "Équipements divers", "7"),
        ("7.8", "Équipements militaires", "7"),
        
        # Constructions
        ("8.1", "Acquisition de terrains", "8"),
        ("8.2", "Acquisition de bâtiments", "8"),
        ("8.3", "Acquisition immobilisations financières", "8"),
        ("8.4", "Construction ouvrages et édifices", "8"),
        ("8.5", "Réhabilitation / réfection / additions", "8"),
        
        # Prêts et avances
        ("9.1", "Prêts et avances", "9"),
        
        # NIVEAU 3 - Sous-sous-categories (décalées)
        # Dette intérieure
        ("1.1.1", "Dette sociale", "1.1"),
        ("1.1.2", "Dette commerciale", "1.1"),
        ("1.1.3", "Dette financière", "1.1"),
        
        # Dette extérieure
        ("1.2.1", "Club de Paris", "1.2"),
        ("1.2.2", "Club de Londres", "1.2"),
        ("1.2.3", "Club de Kinshasa", "1.2"),
        ("1.2.4", "Dette multilatérale", "1.2"),
        
        # Intérêts dette intérieure
        ("2.1.1", "Intérêts dette financière intérieure", "2.1"),
        ("2.1.2", "Intérêts moratoires", "2.1"),
        ("2.1.3", "Intérêts titrisés", "2.1"),
        
        # Intérêts dette extérieure
        ("2.2.1", "Intérêts Club de Paris", "2.2"),
        ("2.2.2", "Intérêts Club de Londres", "2.2"),
        ("2.2.3", "Intérêts Club de Kinshasa", "2.2"),
        ("2.2.4", "Intérêts dette multilatérale", "2.2"),
        
        # Traitement personnel
        ("3.1.1", "Traitement personnel permanent", "3.1"),
        ("3.1.2", "Traitement personnel contractuel", "3.1"),
        
        # Dépenses accessoires
        ("3.2.1", "Indemnité de transport", "3.2"),
        ("3.2.2", "Indemnité de logement", "3.2"),
        ("3.2.3", "Primes permanentes", "3.2"),
        ("3.2.4", "Indemnité de sortie / fin carrière", "3.2"),
        ("3.2.5", "Primes non permanentes", "3.2"),
        ("3.2.6", "Frais d'installation / mutation", "3.2"),
        ("3.2.7", "Indemnités kilométriques", "3.2"),
        
        # Fournitures et petits matériels
        ("4.1.1", "Fournitures et petits matériels", "4.1"),
        ("4.1.2", "Vaccins et inoculation", "4.1"),
        ("4.1.3", "Produits médicaux", "4.1"),
        ("4.1.4", "Outils médico-chirurgicaux", "4.1"),
        ("4.1.5", "Contraceptifs", "4.1"),
        
        # Matériaux / pièces de rechange
        ("4.2.1", "Matériaux de construction / quincaillerie", "4.2"),
        ("4.2.2", "Pièces matériels roulants", "4.2"),
        ("4.2.3", "Pièces autres équipements", "4.2"),
        
        # Produits chimiques / énergie / semences
        ("4.3.1", "Produits chimiques / organiques", "4.3"),
        ("4.3.2", "Semences et produits agroalimentaires", "4.3"),
        ("4.3.3", "Fournitures énergétiques", "4.3"),
        
        # Matériels textiles
        ("4.4.1", "Textiles et tissus", "4.4"),
        ("4.4.2", "Insignes et distinctions honorifiques", "4.4"),
        
        # Dépenses de base
        ("5.1.1", "Communication et télécommunication", "5.1"),
        ("5.1.2", "Location satellite", "5.1"),
        ("5.1.3", "Alimentation en eau", "5.1"),
        ("5.1.4", "Alimentation en énergie électrique", "5.1"),
        
        # Publicité / impression
        ("5.2.1", "Publicité", "5.2"),
        ("5.2.2", "Impression / reproduction / conservation", "5.2"),
        ("5.2.3", "Imprimés de valeur", "5.2"),
        
        # Dépenses de transport
        ("5.3.1", "Location/affrètement transport", "5.3"),
        ("5.3.2", "Titres de voyage intérieur", "5.3"),
        ("5.3.3", "Titres de voyage extérieur", "5.3"),
        
        # Location immobilière / équipement
        ("5.4.1", "Location immobilière", "5.4"),
        ("5.4.2", "Frais d'hébergement", "5.4"),
        ("5.4.3", "Location d'équipement et matériel", "5.4"),
        
        # Entretien et réparation matériel
        ("5.5.1", "Entretien matériel et équipement", "5.5"),
        ("5.5.2", "Réparation matériel et équipement", "5.5"),
        
        # Soins vétérinaires et environnement
        ("5.6.1", "Soins vétérinaires", "5.6"),
        ("5.6.2", "Soins protection environnement", "5.6"),
        
        # Entretien ouvrages et édifices
        ("5.7.1", "Entretien / réparation édifices", "5.7"),
        ("5.7.2", "Entretien ouvrages hydroélectriques / routes", "5.7"),
        
        # Autres services
        ("5.8.1", "Frais de mission intérieur", "5.8"),
        ("5.8.2", "Frais de mission extérieur", "5.8"),
        ("5.8.3", "Frais secrets de recherche", "5.8"),
        ("5.8.4", "Frais d'assurances", "5.8"),
        ("5.8.5", "Prestations intellectuelles", "5.8"),
        ("5.8.6", "Contrats d'études", "5.8"),
        ("5.8.7", "Commissions bancaires", "5.8"),
        ("5.8.8", "Autres prestations", "5.8"),
        
        # Subventions
        ("6.1.1", "Subventions budgets annexes", "6.1"),
        ("6.1.2", "Subventions institutions financières", "6.1"),
        ("6.1.3", "Subventions entreprises publiques", "6.1"),
        ("6.1.4", "Subventions entreprises privées", "6.1"),
        ("6.1.5", "Subventions à des tiers", "6.1"),
        
        # Transferts
        ("6.2.1", "Transferts ambassades", "6.2"),
        ("6.2.2", "Transferts services déconcentrés", "6.2"),
        ("6.2.3", "Transferts provinces et ETD", "6.2"),
        ("6.2.4", "Transfert Caisse Nationale Péréquation", "6.2"),
        ("6.2.5", "Transfert établissements publics nationaux", "6.2"),
        ("6.2.6", "Bourses d'études", "6.2"),
        ("6.2.7", "Rétrocession", "6.2"),
        ("6.2.8", "Liste civile", "6.2"),
        ("6.2.9", "Contributions diverses", "6.2"),
        
        # Interventions de l'État
        ("6.3.1", "Fonds spécial d'intervention", "6.3"),
        ("6.3.2", "Intervention catastrophes / calamités", "6.3"),
        ("6.3.3", "Aide, secours, indemnisation", "6.3"),
        ("6.3.4", "Interventions économiques / sociales", "6.3"),
        
        # Prestations sociales
        ("6.4.1", "Pensions / rentes", "6.4"),
        ("6.4.2", "Honorariat / éméritat", "6.4"),
        ("6.4.3", "Allocations familiales", "6.4"),
        ("6.4.4", "Frais médicaux et pharmaceutiques", "6.4"),
        ("6.4.5", "Frais funéraires", "6.4"),
        
        # Équipements et mobiliers
        ("7.1.1", "Mobiliers / équipements bureau", "7.1"),
        ("7.1.2", "Équipements informatiques", "7.1"),
        
        # Équipements de santé
        ("7.2.1", "Equipements médico-chirurgicaux", "7.2"),
        
        # Équipements éducatifs / culturels / sportifs
        ("7.3.1", "Équipements éducatifs / sportifs", "7.3"),
        
        # Équipements agro / industriels
        ("7.4.1", "Équipement agro-sylvo-pastoral", "7.4"),
        ("7.4.2", "Équipement industriel / électrique", "7.4"),
        ("7.4.3", "Acquisition d'animaux", "7.4"),
        
        # Équipements construction / transport
        ("7.5.1", "Équipements de construction", "7.5"),
        ("7.5.2", "Équipements de transport", "7.5"),
        ("7.5.3", "Équipements de manutention", "7.5"),
        
        # Équipements de communication
        ("7.6.1", "Équipements téléphoniques / radios", "7.6"),
        ("7.6.2", "Équipements photo / vidéo", "7.6"),
        
        # Équipements divers
        ("7.7.1", "Équipements divers", "7.7"),
        
        # Équipements militaires
        ("7.8.1", "Équipements militaires", "7.8"),
        
        # Acquisition de terrains
        ("8.1.1", "Acquisition de terrains", "8.1"),
        
        # Acquisition de bâtiments
        ("8.2.1", "Acquisition bâtiments", "8.2"),
        
        # Acquisition immobilisations financières
        ("8.3.1", "Prise de participation", "8.3"),
        ("8.3.2", "Garanties et cautionnements", "8.3"),
        
        # Construction ouvrages et édifices
        ("8.4.1", "Construction édifices / bâtiments", "8.4"),
        ("8.4.2", "Construction ouvrages hydrauliques / hydroélectriques", "8.4"),
        ("8.4.3", "Construction routes / ponts / ports / aéroports", "8.4"),
        ("8.4.4", "Construction lignes électriques / téléphoniques", "8.4"),
        ("8.4.8", "Constructions diverses", "8.4"),
        
        # Réhabilitation / réfection / additions
        ("8.5.1", "Réhabilitation édifices", "8.5"),
        ("8.5.2", "Réhabilitation ouvrages hydrauliques", "8.5"),
        ("8.5.3", "Réhabilitation routes / pistes / ports / rails", "8.5"),
        
        # Prêts et avances
        ("9.1.1", "Prêts et avances", "9.1"),
    ]
    
    print("Début de l'import des natures économiques...")
    print("=" * 60)
    
    created_count = 0
    updated_count = 0
    error_count = 0
    
    # Créer un dictionnaire pour mapper les codes aux objets créés
    nature_map = {}
    
    # Importer par ordre hiérarchique pour s'assurer que les parents existent
    for code, titre, code_parent in natures_data:
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
            
            # Créer ou mettre à jour la nature
            nature, created = NatureEconomique.objects.update_or_create(
                code=code,
                defaults={
                    "titre": titre,
                    "code_parent": code_parent,
                    "parent": parent,
                    "active": True
                }
            )
            
            # Ajouter au mapping
            nature_map[code] = nature
            
            if created:
                created_count += 1
                print(f"✅ Créé: {code} - {titre}")
                if parent:
                    print(f"   └─ Parent: {parent.code} - {parent.titre}")
            else:
                updated_count += 1
                print(f"🔄 Mis à jour: {code} - {titre}")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'import de {code}: {str(e)}")
            error_count += 1
    
    print("=" * 60)
    print(f"Import terminé:")
    print(f"  - {created_count} natures créées")
    print(f"  - {updated_count} natures mises à jour")
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
