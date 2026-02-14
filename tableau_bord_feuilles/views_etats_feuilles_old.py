from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q, Count
from django.utils import timezone
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from datetime import datetime

# Imports pour PDF
try:
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from io import BytesIO
    from urllib.parse import unquote
    REPORTLAB_AVAILABLE = True
except ImportError as e:
    REPORTLAB_AVAILABLE = False
    print(f"WARNING: ReportLab n'est pas disponible: {e}. Les rapports PDF ne fonctionneront pas.")

from demandes.models import DepenseFeuille, NatureEconomique
from recettes.models import RecetteFeuille
from banques.models import Banque
from accounts.models import Service


@method_decorator(csrf_exempt, name='dispatch')
class EtatsFeuillesPreviewView(LoginRequiredMixin, View):
    """Vue pour le preview des états feuilles"""
    
    def post(self, request, *args, **kwargs):
        try:
            print("=== DÉBUT DE LA REQUÊTE ===")
            print("POST data reçu:", dict(request.POST))
            
            # Récupérer les paramètres
            type_etat = request.POST.get('type_etat')
            print(f"Type état: {type_etat}")
            
            if not type_etat:
                return JsonResponse({'success': False, 'error': 'Type d\'état manquant'})
            
            # Gérer les nouveaux types d'états personnalisés
            if type_etat in ['depense_par_nature', 'depense_par_mois', 'rapport_par_banque', 
                           'synthese_par_banque', 'synthese_par_depenses']:
                return self._handle_nouveaux_etats(request, type_etat)
            elif type_etat in ['recette_du_mois', 'recette_par_banque', 'synthese_recettes']:
                return self._handle_etats_recettes(request, type_etat)
            
            # Appliquer les mêmes filtres que la vue PDF (cohérence preview / génération)
            if type_etat == 'DEPENSE_FEUILLE':
                # LOGIQUE SIMPLE DIRECTE - sans fonction externe
                queryset = DepenseFeuille.objects.all()
                print(f"Total initial DepenseFeuille: {queryset.count()}")
                
                # Récupérer les filtres
                mois = request.POST.get('mois_depenses')  # Changé : get() au lieu de getlist()
                annee = request.POST.get('annee_depenses')
                natures = request.POST.get('natures_depenses')
                services = request.POST.get('services_depenses')
                banques = request.POST.get('banques_depenses')
                montant_min = request.POST.get('montant_min_depenses')
                montant_max = request.POST.get('montant_max_depenses')
                observation = request.POST.get('observation_depenses')
                
                print(f"Filtres reçus - Mois: {mois}, Année: {annee}, Nature: {natures}, Service: {services}, Banque: {banques}")
                
                # Appliquer les filtres
                if mois and mois.isdigit() and mois != '':
                    queryset = queryset.filter(mois=int(mois))
                    print(f"✅ Filtré par mois: {mois} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucun mois sélectionné ou 'Toutes'")
                
                if annee and annee.isdigit() and annee != '':
                    queryset = queryset.filter(annee=int(annee))
                    print(f"✅ Filtré par annee: {annee} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucune année sélectionnée ou 'Toutes'")
                
                # Logique simple pour les ChoiceField
                if natures and natures.isdigit() and natures != '':
                    queryset = queryset.filter(nature_economique_id=int(natures))
                    print(f"✅ Filtré par nature: {natures} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucune nature sélectionnée ou 'Toutes'")
                
                if services and services.isdigit() and services != '':
                    queryset = queryset.filter(service_beneficiaire_id=int(services))
                    print(f"✅ Filtré par service: {services} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucun service sélectionné ou 'Toutes'")
                
                if banques and banques.isdigit() and banques != '':
                    queryset = queryset.filter(banque_id=int(banques))
                    print(f"✅ Filtré par banque: {banques} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucune banque sélectionnée ou 'Toutes'")
                
                if montant_min and str(montant_min).replace('.', '').replace('-', '').isdigit():
                    queryset = queryset.filter(montant_fc__gte=Decimal(str(montant_min)))
                    print(f"✅ Filtré par montant_min: {montant_min} -> {queryset.count()} résultats")
                
                if montant_max and str(montant_max).replace('.', '').replace('-', '').isdigit():
                    queryset = queryset.filter(montant_fc__lte=Decimal(str(montant_max)))
                    print(f"✅ Filtré par montant_max: {montant_max} -> {queryset.count()} résultats")
                
                if observation and observation.strip():
                    queryset = queryset.filter(observation__icontains=observation.strip())
                    print(f"✅ Filtré par observation: {observation} -> {queryset.count()} résultats")
                
                # Limiter pour le preview (avec pagination)
                total_count = queryset.count()
                print(f"🔍 AVANT pagination: {total_count} résultats totaux")
                
                page = int(request.POST.get('page', 1))
                page_size = 50
                start = (page - 1) * page_size
                end = start + page_size
                
                print(f"📊 Pagination params: page={page}, start={start}, end={end}, page_size={page_size}")
                
                queryset = queryset.order_by('-date')[start:end]
                print(f"📊 Pagination: page {page}, {queryset.count()}/{total_count} résultats affichés")
                
                lignes = []
                total_cdf = Decimal('0.00')
                total_usd = Decimal('0.00')
                
                for dep in queryset:
                    lignes.append({
                        'date': dep.date.strftime('%d/%m/%Y'),
                        'libelle_depenses': dep.libelle_depenses[:100],
                        'nature_economique': dep.nature_economique.titre if dep.nature_economique else '',
                        'service_beneficiaire': dep.service_beneficiaire.nom_service if dep.service_beneficiaire else '',
                        'banque': dep.banque.nom_banque if dep.banque else '',
                        'montant_fc': float(dep.montant_fc),
                        'montant_usd': float(dep.montant_usd),
                        'observation': dep.observation[:100] if dep.observation else '',
                    })
                    total_cdf += dep.montant_fc
                    total_usd += dep.montant_usd
                
                print(f"📊 Détails: {len(lignes)} lignes traitées, Total CDF: {total_cdf}, Total USD: {total_usd}")
                
            elif type_etat == 'RECETTE_FEUILLE':
                from tableau_bord_feuilles.views_rapports import _queryset_recettes_filtre
                queryset = _queryset_recettes_filtre(request)
                total_count = queryset.count()
                page = int(request.POST.get('page', 1))
                page_size = 50
                start = (page - 1) * page_size
                end = start + page_size
                
                queryset = queryset.order_by('-date')[start:end]
                print(f"📊 Pagination recettes: page {page}, {queryset.count()}/{total_count} résultats affichés")
                
                lignes = []
                total_cdf = Decimal('0.00')
                total_usd = Decimal('0.00')
                
                for rec in queryset:
                    lignes.append({
                        'date': rec.date.strftime('%d/%m/%Y'),
                        'libelle_recette': rec.libelle_recette[:100],
                        'banque': rec.banque.nom_banque if rec.banque else '',
                        'montant_fc': float(rec.montant_fc),
                        'montant_usd': float(rec.montant_usd),
                    })
                    total_cdf += rec.montant_fc
                    total_usd += rec.montant_usd
                
                print(f"📊 Résultat recettes: {len(lignes)} lignes, Total CDF: {total_cdf}, Total USD: {total_usd}")
            else:
                return JsonResponse({'success': False, 'error': 'Type d\'état non valide'})
            
            print(f"Résultat FINAL: {len(lignes)} lignes, Total CDF: {total_cdf}, Total USD: {total_usd}")
            print("=== FIN DE LA REQUÊTE ===")
            
            return JsonResponse({
                'success': True,
                'lignes': lignes,
                'count': len(lignes),
                'total_count': total_count,  # Ajout du nombre total
                'page': page,
                'page_size': page_size,
                'has_next': end < total_count,
                'total_cdf': float(total_cdf),
                'total_usd': float(total_usd),
            })
            
        except Exception as e:
            print(f"ERREUR CAPTURÉE: {str(e)}")
            import traceback
            print("TRACEBACK COMPLET:")
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': f'Erreur: {str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class EtatsFeuillesGenererView(LoginRequiredMixin, View):
    """Vue pour générer les états feuilles"""
    
    def post(self, request, *args, **kwargs):
        try:
            format_sortie = request.POST.get('format_sortie', 'PDF')
            type_etat = request.POST.get('type_etat')
            type_rapport = request.POST.get('type_rapport', 'DETAILLE')  # DETAILLE, GROUPE, SYNTHESE
            
            print(f"Génération rapport: {type_etat}, format: {format_sortie}, type: {type_rapport}")
            
            if type_rapport == 'SYNTHESE':
                # Rapport synthétique - juste les totaux
                return self._generer_synthese(request, type_etat, format_sortie)
            elif type_rapport == 'GROUPE':
                # Rapport regroupé
                critere_groupement = request.POST.get('critere_groupement', 'nature')
                return self._generer_groupe(request, type_etat, critere_groupement, format_sortie)
            else:
                # Rapport détaillé (existant)
                if format_sortie == 'PDF':
                    if type_etat == 'RECETTE_FEUILLE':
                        return JsonResponse({'success': True, 'etat_id': 'recette_pdf'})
                    elif type_etat == 'DEPENSE_FEUILLE':
                        return JsonResponse({'success': True, 'etat_id': 'depense_pdf'})
                    else:
                        return JsonResponse({'success': True, 'etat_id': 'tableau_general_pdf'})
                else:
                    return JsonResponse({'success': False, 'error': 'Export Excel non encore implémenté'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _generer_synthese(self, request, type_etat, format_sortie):
        """Générer un rapport synthétique avec juste les totaux"""
        from decimal import Decimal
        from django.db.models import Sum, Q
        
        annee = request.POST.get('annee_depenses') or request.POST.get('annee_recettes')
        mois = request.POST.get('mois_depenses') or request.POST.get('mois_recettes')
        
        print(f"Synthèse - Année: {annee}, Mois: {mois}, Type: {type_etat}")
        
        # Construire les filtres
        filtres = Q()
        if annee and annee.isdigit() and annee != '':
            filtres &= Q(annee=int(annee))
        if mois and mois.isdigit() and mois != '':
            filtres &= Q(mois=int(mois))
        
        if type_etat == 'DEPENSE_FEUILLE':
            queryset = DepenseFeuille.objects.filter(filtres)
            resultats = queryset.aggregate(
                total_cdf=Sum('montant_fc'),
                total_usd=Sum('montant_usd'),
                nombre=Count('id')
            )
            titre = f"SYNTHÈSE DES DÉPENSES"
            if annee:
                titre += f" - {annee}"
            if mois and mois.isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                titre += f" - {mois_noms[int(mois)]}"
        else:
            queryset = RecetteFeuille.objects.filter(filtres)
            resultats = queryset.aggregate(
                total_cdf=Sum('montant_fc'),
                total_usd=Sum('montant_usd'),
                nombre=Count('id')
            )
            titre = f"SYNTHÈSE DES RECETTES"
            if annee:
                titre += f" - {annee}"
            if mois and mois.isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                titre += f" - {mois_noms[int(mois)]}"
        
        # Préparer les données pour le template
        data = {
            'titre': titre,
            'total_cdf': resultats['total_cdf'] or Decimal('0'),
            'total_usd': resultats['total_usd'] or Decimal('0'),
            'nombre': resultats['nombre'] or 0,
            'annee': annee,
            'mois': mois,
            'type_etat': type_etat
        }
        
        print(f"Données synthèse: {data}")
        
        if format_sortie == 'PDF':
            return JsonResponse({
                'success': True, 
                'type': 'SYNTHESE',
                'data': data
            })
        else:
            return JsonResponse({'success': False, 'error': 'Export Excel non encore implémenté'})
    
    def _generer_groupe(self, request, type_etat, critere_groupement, format_sortie):
        """Générer un rapport regroupé par critère"""
        from django.db.models import Sum, Count
        from collections import defaultdict
        
        annee = request.POST.get('annee_depenses') or request.POST.get('annee_recettes')
        mois = request.POST.get('mois_depenses') or request.POST.get('mois_recettes')
        
        print(f"Groupe - Critère: {critere_groupement}, Année: {annee}, Mois: {mois}, Type: {type_etat}")
        
        # Construire les filtres
        filtres = {}
        if annee and annee.isdigit() and annee != '':
            filtres['annee'] = int(annee)
        if mois and mois.isdigit() and mois != '':
            filtres['mois'] = int(mois)
        
        if type_etat == 'DEPENSE_FEUILLE':
            queryset = DepenseFeuille.objects.filter(**filtres)
            
            if critere_groupement == 'nature':
                groups = queryset.values('nature_economique__titre').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('nature_economique__titre')
                titre = f"DÉPENSES PAR NATURE ÉCONOMIQUE"
            elif critere_groupement == 'service':
                groups = queryset.values('service_beneficiaire__nom_service').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('service_beneficiaire__nom_service')
                titre = f"DÉPENSES PAR SERVICE BÉNÉFICIAIRE"
            elif critere_groupement == 'banque':
                groups = queryset.values('banque__nom_banque').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('banque__nom_banque')
                titre = f"DÉPENSES PAR BANQUE"
            elif critere_groupement == 'mois':
                groups = queryset.values('mois').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('mois')
                titre = f"DÉPENSES PAR MOIS"
            else:
                return JsonResponse({'success': False, 'error': 'Critère de regroupement non valide'})
                
        else:  # RECETTE_FEUILLE
            queryset = RecetteFeuille.objects.filter(**filtres)
            
            if critere_groupement == 'nature':
                groups = queryset.values('source_recette__nom').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('source_recette__nom')
                titre = f"RECETTES PAR SOURCE"
            elif critere_groupement == 'banque':
                groups = queryset.values('banque__nom_banque').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('banque__nom_banque')
                titre = f"RECETTES PAR BANQUE"
            elif critere_groupement == 'mois':
                groups = queryset.values('mois').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('mois')
                titre = f"RECETTES PAR MOIS"
            else:
                return JsonResponse({'success': False, 'error': 'Critère de regroupement non valide pour les recettes'})
        
        # Ajouter la période au titre
        if annee:
            titre += f" - {annee}"
        if mois and mois.isdigit():
            mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                          'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            titre += f" - {mois_noms[int(mois)]}"
        
        # Préparer les données
        data = {
            'titre': titre,
            'groups': list(groups),
            'critere': critere_groupement,
            'annee': annee,
            'mois': mois,
            'type_etat': type_etat
        }
        
        print(f"Données groupe: {len(data['groups'])} groupes trouvés")
        
        if format_sortie == 'PDF':
            return JsonResponse({
                'success': True, 
                'type': 'GROUPE',
                'data': data
            })
        else:
            return JsonResponse({'success': False, 'error': 'Export Excel non encore implémenté'})


@method_decorator(csrf_exempt, name='dispatch')
class RapportSynthesePDFView(LoginRequiredMixin, View):
    """Vue pour générer les rapports synthétiques en PDF"""
    
    def get(self, request, *args, **kwargs):
        if not REPORTLAB_AVAILABLE:
            return HttpResponse("ReportLab n'est pas disponible. Veuillez l'installer avec: pip install reportlab", content_type='text/plain')
        
        try:
            # Récupérer les données depuis l'URL
            from urllib.parse import unquote
            data_json = request.GET.get('data', '{}')
            data = json.loads(unquote(data_json))
            
            print(f"Génération PDF synthèse: {data}")
            
            # Créer le buffer PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                               rightMargin=0.5*cm, leftMargin=0.5*cm, 
                               topMargin=0.8*cm, bottomMargin=0.8*cm)
            
            styles = getSampleStyleSheet()
            elements = []
            
            # Titre
            titre_style = styles['Title']
            elements.append(Paragraph(data['titre'], titre_style))
            elements.append(Spacer(1, 0.5*cm))
            
            # Période
            periode = ""
            if data.get('annee'):
                periode = f"Année: {data['annee']}"
            if data.get('mois') and data['mois'].isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                periode += f" - {mois_noms[int(data['mois'])]}"
            
            if periode:
                elements.append(Paragraph(f"<b>Période:</b> {periode}", styles['Normal']))
                elements.append(Spacer(1, 0.5*cm))
            
            # Statistiques principales
            elements.append(Paragraph("<b>STATISTIQUES PRINCIPALES</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.3*cm))
            
            # Convertir les montants en nombres
            try:
                total_cdf = float(data['total_cdf']) if data['total_cdf'] else 0
            except (ValueError, TypeError):
                total_cdf = 0
            
            try:
                total_usd = float(data['total_usd']) if data['total_usd'] else 0
            except (ValueError, TypeError):
                total_usd = 0
            
            stats_data = [
                ['Type', 'Nombre', 'Total CDF', 'Total USD'],
                [data['type_etat'].replace('_FEUILLE', '').capitalize(), 
                 str(data['nombre']), 
                 f"{total_cdf:,.2f}".replace(',', ' '), 
                 f"{total_usd:,.2f}".replace(',', ' ')]
            ]
            
            stats_table = Table(stats_data, colWidths=[4*cm, 3*cm, 5*cm, 5*cm])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(stats_table)
            elements.append(Spacer(1, 1*cm))
            
            # Générer le PDF
            doc.build(elements)
            
            # Préparer la réponse
            pdf_value = buffer.getvalue()
            buffer.close()
            
            response = HttpResponse(pdf_value, content_type='application/pdf')
            filename = f"synthese_{data['type_etat'].lower()}_{data.get('annee', 'tout')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"Erreur génération PDF synthèse: {e}")
            import traceback
            traceback.print_exc()
            return HttpResponse(f"Erreur: {str(e)}", content_type='text/plain')


@method_decorator(csrf_exempt, name='dispatch')
class RapportGroupePDFView(LoginRequiredMixin, View):
    """Vue pour générer les rapports regroupés en PDF"""
    
    def get(self, request, *args, **kwargs):
        if not REPORTLAB_AVAILABLE:
            return HttpResponse("ReportLab n'est pas disponible. Veuillez l'installer avec: pip install reportlab", content_type='text/plain')
        
        try:
            # Récupérer les données depuis l'URL
            from urllib.parse import unquote
            data_json = request.GET.get('data', '{}')
            data = json.loads(unquote(data_json))
            
            print(f"Génération PDF groupe: {data}")
            
            # Récupérer le type d'état dès le début
            type_etat = data.get('type_etat', 'DEPENSE_FEUILLE')
            
            # Définir le type de titre selon le type d'état
            titre_type = "Relevé des recettes" if type_etat == 'RECETTE_FEUILLE' else "Relevé des dépenses"
            
            # Créer le buffer PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                               rightMargin=0.5*cm, leftMargin=0.5*cm, 
                               topMargin=0.8*cm, bottomMargin=0.8*cm)
            
            styles = getSampleStyleSheet()
            elements = []
            
            # Titre personnalisé selon le critère
            critere = data['critere']
            # Adapter les libellés de critères selon le type d'état
            if type_etat == 'RECETTE_FEUILLE':
                critere_labels = {
                    'nature': 'Source de recette',
                    'service': 'Service Bénéficiaire', 
                    'banque': 'Banque',
                    'mois': 'Mois'
                }
            else:
                critere_labels = {
                    'nature': 'Nature Économique',
                    'service': 'Service Bénéficiaire', 
                    'banque': 'Banque',
                    'mois': 'Mois'
                }
            
            titre = f"{titre_type} par {critere_labels.get(critere, critere)}"
            if data.get('mois') and data['mois'].isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                titre += f" du {mois_noms[int(data['mois'])]} {data.get('annee', '')}"
            elif data.get('annee'):
                titre += f" de l'année {data['annee']}"
            
            titre_style = styles['Title']
            elements.append(Paragraph(titre, titre_style))
            elements.append(Spacer(1, 0.5*cm))
            
            # Période
            periode = ""
            if data.get('annee'):
                periode = f"Année: {data['annee']}"
            if data.get('mois') and data['mois'].isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                periode += f" - {mois_noms[int(data['mois'])]}"
            
            if periode:
                elements.append(Paragraph(f"<b>Période:</b> {periode}", styles['Normal']))
                elements.append(Spacer(1, 0.5*cm))
            
            # Importer les modèles selon le type d'état
            if type_etat == 'RECETTE_FEUILLE':
                from recettes.models import RecetteFeuille, SourceRecette
                from banques.models import Banque
                ModelFeuille = RecetteFeuille
            else:
                from demandes.models import DepenseFeuille, NatureEconomique, Service
                from banques.models import Banque
                ModelFeuille = DepenseFeuille
            
            # Traiter chaque regroupement avec détails
            groups = data['groups']
            
            for group in groups:
                # Récupérer le libellé du regroupement selon le type d'état
                if critere == 'nature':
                    if type_etat == 'RECETTE_FEUILLE':
                        groupe_libelle = str(group.get('source_recette__nom', 'N/A'))
                        groupe_id = group.get('source_recette_id')
                    else:
                        groupe_libelle = str(group.get('nature_economique__titre', 'N/A'))
                        groupe_id = group.get('nature_economique_id')
                elif critere == 'service':
                    # Pour les recettes, le service n'est pas applicable
                    if type_etat == 'RECETTE_FEUILLE':
                        continue  # Skip ce groupe pour les recettes
                    groupe_libelle = str(group.get('service_beneficiaire__nom_service', 'N/A'))
                    groupe_id = group.get('service_beneficiaire_id')
                elif critere == 'banque':
                    groupe_libelle = str(group.get('banque__nom_banque', 'N/A'))
                    groupe_id = group.get('banque_id')
                elif critere == 'mois':
                    mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                                  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                    mois_num = group.get('mois', 0)
                    groupe_libelle = mois_noms[mois_num] if mois_num < len(mois_noms) else f"Mois {mois_num}"
                    groupe_id = mois_num
                else:
                    continue
                
                # Afficher le libellé du regroupement
                elements.append(Paragraph(f"<b>{groupe_libelle.upper()}</b>", styles['Heading2']))
                elements.append(Spacer(1, 0.3*cm))
                
                # Récupérer les données détaillées pour ce regroupement
                donnees = ModelFeuille.objects.all()
                
                # Filtrer par période
                if data.get('annee'):
                    donnees = donnees.filter(annee=data['annee'])
                if data.get('mois') and data['mois'].isdigit():
                    donnees = donnees.filter(mois=int(data['mois']))
                
                # Filtrer par critère de regroupement selon le type d'état
                if critere == 'nature' and groupe_id:
                    if type_etat == 'RECETTE_FEUILLE':
                        donnees = donnees.filter(source_recette_id=groupe_id)
                    else:
                        donnees = donnees.filter(nature_economique_id=groupe_id)
                elif critere == 'service' and groupe_id:
                    donnees = donnees.filter(service_beneficiaire_id=groupe_id)
                elif critere == 'banque' and groupe_id:
                    donnees = donnees.filter(banque_id=groupe_id)
                elif critere == 'mois' and groupe_id:
                    donnees = donnees.filter(mois=groupe_id)
                
                # Préparer les données du tableau détaillé selon le type
                if type_etat == 'RECETTE_FEUILLE':
                    headers = ['Date', 'Libellé recette', 'Montant CDF', 'Montant USD']
                else:
                    headers = ['Date', 'Libellé dépense', 'Montant CDF', 'Montant USD']
                table_data = [headers]
                
                total_cdf_groupe = 0
                total_usd_groupe = 0
                
                for item in donnees.order_by('date'):
                    montant_cdf = item.montant_fc or 0
                    montant_usd = item.montant_usd or 0
                    
                    total_cdf_groupe += montant_cdf
                    total_usd_groupe += montant_usd
                    
                    # Adapter le libellé selon le type (augmenter la longueur)
                    if type_etat == 'RECETTE_FEUILLE':
                        libelle = item.libelle_recette[:150]
                    else:
                        libelle = item.libelle_depenses[:150]
                    
                    table_data.append([
                        item.date.strftime('%d/%m/%Y'),
                        libelle,
                        f"{montant_cdf:,.2f}".replace(',', ' ') if montant_cdf > 0 else '0,00',
                        f"{montant_usd:,.2f}".replace(',', ' ') if montant_usd > 0 else '0,00'
                    ])
                
                # Créer le tableau détaillé
                if len(table_data) > 1:  # S'il y a des dépenses
                    table = Table(table_data, colWidths=[2.5*cm, 10*cm, 4.5*cm, 4.5*cm])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('FONTSIZE', (0, 1), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    
                    elements.append(table)
                    elements.append(Spacer(1, 0.3*cm))
                    
                    # Afficher le total du groupe
                    total_data = [
                        ['TOTAL', '', 
                         f"{total_cdf_groupe:,.2f}".replace(',', ' '), 
                         f"{total_usd_groupe:,.2f}".replace(',', ' ')]
                    ]
                    
                    total_table = Table(total_data, colWidths=[2.5*cm, 10*cm, 4.5*cm, 4.5*cm])
                    total_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    
                    elements.append(total_table)
                else:
                    # Aucune dépense pour ce regroupement
                    elements.append(Paragraph("Aucune dépense trouvée pour ce regroupement.", styles['Normal']))
                
                # Saut de page entre les regroupements (sauf pour le dernier)
                elements.append(Spacer(1, 1*cm))
            
            # Générer le PDF
            doc.build(elements)
            
            # Préparer la réponse
            pdf_value = buffer.getvalue()
            buffer.close()
            
            response = HttpResponse(pdf_value, content_type='application/pdf')
            filename = f"rapport_groupe_{data['critere']}_{data.get('annee', 'tout')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"Erreur génération PDF groupe: {e}")
            import traceback
            traceback.print_exc()
            return HttpResponse(f"Erreur: {str(e)}", content_type='text/plain')
