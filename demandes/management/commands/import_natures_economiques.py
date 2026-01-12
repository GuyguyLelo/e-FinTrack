"""
Commande pour importer les natures économiques
"""
from django.core.management.base import BaseCommand
from demandes.models import NatureEconomique


class Command(BaseCommand):
    help = 'Importe les natures économiques dans la base de données'

    def handle(self, *args, **options):
        data = [
            # ----- 1 DETTE PUBLIQUE -----
            ("1", "DETTE PUBLIQUE EN CAPITAL", ""),
            ("1-171", "Dette intérieure", ""),
            ("1-1711", "Dette sociale", ""),
            ("1-1712", "Dette commerciale", ""),
            ("1-1713", "Dette financière", ""),
            ("1-162", "Dette extérieure", ""),
            ("1-1621", "Club de Paris", ""),
            ("1-1622", "Club de Londres", ""),
            ("1-1623", "Club de Kinshasa", ""),
            ("1-1624", "Dette multilatérale", ""),

            # ----- 2 FRAIS FINANCIERS -----
            ("2", "FRAIS FINANCIERS", ""),
            ("2-671", "Intérêts sur la dette intérieure", ""),
            ("2-6711", "Intérêts dette financière intérieure", ""),
            ("2-6712", "Intérêts moratoires", ""),
            ("2-6713", "Intérêts titrisés", ""),
            ("2-672", "Intérêts sur la dette extérieure", ""),
            ("2-6721", "Intérêts Club de Paris", ""),
            ("2-6722", "Intérêts Club de Londres", ""),
            ("2-6723", "Intérêts Club de Kinshasa", ""),
            ("2-6724", "Intérêts dette multilatérale", ""),

            # ----- 3 DEPENSES DE PERSONNEL -----
            ("3", "DEPENSES DE PERSONNEL", ""),
            ("3-661", "Traitement de base du personnel", ""),
            ("3-6611", "Traitement personnel permanent", ""),
            ("3-6612", "Traitement personnel contractuel", ""),
            ("3-662", "Dépenses accessoires du personnel", ""),
            ("3-6621", "Indemnité de transport", ""),
            ("3-6622", "Indemnité de logement", ""),
            ("3-6623", "Primes permanentes", ""),
            ("3-6624", "Indemnité de sortie / fin carrière", ""),
            ("3-6625", "Primes non permanentes", ""),
            ("3-6626", "Frais d'installation / mutation", ""),
            ("3-6627", "Indemnités kilométriques", ""),

            # ----- 4 BIENS ET MATÉRIELS -----
            ("4", "BIENS ET MATERIELS", ""),
            ("4-601", "Fournitures et petits matériels", ""),
            ("4-6011", "Fournitures et petits matériels", ""),
            ("4-6012", "Vaccins et inoculation", ""),
            ("4-6013", "Produits médicaux", ""),
            ("4-6014", "Outils médico-chirurgicaux", ""),
            ("4-6015", "Contraceptifs", ""),
            ("4-602", "Matériaux / pièces de rechange", ""),
            ("4-6021", "Matériaux de construction / quincaillerie", ""),
            ("4-6022", "Pièces matériels roulants", ""),
            ("4-6023", "Pièces autres équipements", ""),
            ("4-604", "Produits chimiques / énergie / semences", ""),
            ("4-6041", "Produits chimiques / organiques", ""),
            ("4-6042", "Semences et produits agroalimentaires", ""),
            ("4-6043", "Fournitures énergétiques", ""),
            ("4-605", "Matériels textiles", ""),
            ("4-6051", "Textiles et tissus", ""),
            ("4-6052", "Insignes et distinctions honorifiques", ""),

            # ----- 5 PRESTATIONS -----
            ("5", "DEPENSES DE PRESTATIONS", ""),
            ("5-611", "Dépenses de base", ""),
            ("5-6111", "Communication et télécommunication", ""),
            ("5-6112", "Location satellite", ""),
            ("5-6113", "Alimentation en eau", ""),
            ("5-6114", "Alimentation en énergie électrique", ""),
            ("5-612", "Publicité / impression", ""),
            ("5-6121", "Publicité", ""),
            ("5-6122", "Impression / reproduction / conservation", ""),
            ("5-6123", "Imprimés de valeur", ""),
            ("5-613", "Dépenses de transport", ""),
            ("5-6131", "Location/affrètement transport", ""),
            ("5-6132", "Titres de voyage intérieur", ""),
            ("5-6133", "Titres de voyage extérieur", ""),
            ("5-614", "Location immobilière / équipement", ""),
            ("5-6141", "Location immobilière", ""),
            ("5-6142", "Frais d'hébergement", ""),
            ("5-6143", "Location d'équipement et matériel", ""),
            ("5-615", "Entretien et réparation matériel", ""),
            ("5-6151", "Entretien matériel et équipement", ""),
            ("5-6152", "Réparation matériel et équipement", ""),
            ("5-616", "Soins vétérinaires et environnement", ""),
            ("5-6161", "Soins vétérinaires", ""),
            ("5-6162", "Soins protection environnement", ""),
            ("5-617", "Entretien ouvrages et édifices", ""),
            ("5-6171", "Entretien / réparation édifices", ""),
            ("5-6172", "Entretien ouvrages hydroélectriques / routes", ""),
            ("5-618", "Autres services", ""),
            ("5-6181", "Frais de mission intérieur", ""),
            ("5-6182", "Frais de mission extérieur", ""),
            ("5-6183", "Frais secrets de recherche", ""),
            ("5-6184", "Frais d'assurances", ""),
            ("5-6185", "Prestations intellectuelles", ""),
            ("5-6186", "Contrats d'études", ""),
            ("5-6187", "Commissions bancaires", ""),
            ("5-6188", "Autres prestations", ""),

            # ----- 6 TRANSFERTS -----
            ("6", "TRANSFERTS ET INTERVENTIONS DE L'ETAT", ""),
            ("6-641", "Subventions", ""),
            ("6-6411", "Subventions budgets annexes", ""),
            ("6-6412", "Subventions institutions financières", ""),
            ("6-6413", "Subventions entreprises publiques", ""),
            ("6-6414", "Subventions entreprises privées", ""),
            ("6-6415", "Subventions à des tiers", ""),
            ("6-642", "Transferts", ""),
            ("6-6421", "Transferts ambassades", ""),
            ("6-6422", "Transferts services déconcentrés", ""),
            ("6-6423", "Transferts provinces et ETD", ""),
            ("6-6424", "Transfert Caisse Nationale Péréquation", ""),
            ("6-6425", "Transfert établissements publics nationaux", ""),
            ("6-6426", "Bourses d'études", ""),
            ("6-6427", "Rétrocession", ""),
            ("6-6428", "Liste civile", ""),
            ("6-6429", "Contributions diverses", ""),
            ("6-643", "Interventions de l'État", ""),
            ("6-6431", "Fonds spécial d'intervention", ""),
            ("6-6432", "Intervention catastrophes / calamités", ""),
            ("6-6433", "Aide, secours, indemnisation", ""),
            ("6-6434", "Interventions économiques / sociales", ""),
            ("6-644", "Prestations sociales", ""),
            ("6-6441", "Pensions / rentes", ""),
            ("6-6442", "Honorariat / éméritat", ""),
            ("6-6443", "Allocations familiales", ""),
            ("6-6444", "Frais médicaux et pharmaceutiques", ""),
            ("6-6445", "Frais funéraires", ""),

            # ----- 7 ÉQUIPEMENTS -----
            ("7", "EQUIPEMENTS", ""),
            ("7-241", "Équipements et mobiliers", ""),
            ("7-2411", "Mobiliers / équipements bureau", ""),
            ("7-2412", "Équipements informatiques", ""),
            ("7-242", "Équipements de santé", ""),
            ("7-2421", "Equipements médico-chirurgicaux", ""),
            ("7-243", "Équipements éducatifs / culturels / sportifs", ""),
            ("7-2431", "Équipements éducatifs / sportifs", ""),
            ("7-244", "Équipements agro / industriels", ""),
            ("7-2441", "Équipement agro-sylvo-pastoral", ""),
            ("7-2442", "Équipement industriel / électrique", ""),
            ("7-2443", "Acquisition d'animaux", ""),
            ("7-245", "Équipements construction / transport", ""),
            ("7-2451", "Équipements de construction", ""),
            ("7-2452", "Équipements de transport", ""),
            ("7-2453", "Équipements de manutention", ""),
            ("7-246", "Équipements de communication", ""),
            ("7-2461", "Équipements téléphoniques / radios", ""),
            ("7-2462", "Équipements photo / vidéo", ""),
            ("7-248", "Équipements divers", ""),
            ("7-2481", "Équipements divers", ""),
            ("7-257", "Équipements militaires", ""),
            ("7-2571", "Équipements militaires", ""),

            # ----- 8 CONSTRUCTIONS -----
            ("8", "CONSTRUCTIONS / REHABILITATION / ACQUISITIONS IMMOBILIERES", ""),
            ("8-221", "Acquisition de terrains", ""),
            ("8-2211", "Acquisition de terrains", ""),
            ("8-231", "Acquisition de bâtiments", ""),
            ("8-2311", "Acquisition bâtiments", ""),
            ("8-261", "Acquisition immobilisations financières", ""),
            ("8-2611", "Prise de participation", ""),
            ("8-2612", "Garanties et cautionnements", ""),
            ("8-232", "Construction ouvrages et édifices", ""),
            ("8-2321", "Construction édifices / bâtiments", ""),
            ("8-2322", "Construction ouvrages hydrauliques / hydroélectriques", ""),
            ("8-2323", "Construction routes / ponts / ports / aéroports", ""),
            ("8-2324", "Construction lignes électriques / téléphoniques", ""),
            ("8-2328", "Constructions diverses", ""),
            ("8-233", "Réhabilitation / réfection / additions", ""),
            ("8-2331", "Réhabilitation édifices", ""),
            ("8-2332", "Réhabilitation ouvrages hydrauliques", ""),
            ("8-2333", "Réhabilitation routes / pistes / ports / rails", ""),

            # ----- 9 PRÊTS -----
            ("9", "PRETS ET AVANCES", ""),
            ("9-271", "Prêts et avances", ""),
            ("9-2711", "Prêts et avances", ""),
        ]

        def get_parent(code):
            """Trouve le parent d'une nature économique basé sur son code"""
            if "-" not in code:
                return None
            parent_code = "-".join(code.split("-")[:-1])
            try:
                return NatureEconomique.objects.get(code=parent_code)
            except NatureEconomique.DoesNotExist:
                return None

        self.stdout.write(self.style.WARNING('Début de l\'import des natures économiques...'))
        
        created_count = 0
        updated_count = 0
        
        for code, title, desc in data:
            parent = get_parent(code)
            nature, created = NatureEconomique.objects.update_or_create(
                code=code,
                defaults={
                    "titre": title,
                    "description": desc if desc else None,
                    "parent": parent
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Créé: {code} - {title}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Mis à jour: {code} - {title}'))
        
        total = NatureEconomique.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Import terminé avec succès !\n'
            f'  - {created_count} natures créées\n'
            f'  - {updated_count} natures mises à jour\n'
            f'  - Total: {total} natures économiques dans la base'
        ))







