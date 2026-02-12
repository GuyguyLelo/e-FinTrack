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
            
            if critere_groupement == 'banque':
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
                               rightMargin=1*cm, leftMargin=1*cm, 
                               topMargin=1*cm, bottomMargin=1*cm)
            
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
            
            stats_data = [
                ['Type', 'Nombre', 'Total CDF', 'Total USD'],
                [data['type_etat'].replace('_FEUILLE', '').capitalize(), 
                 str(data['nombre']), 
                 f"{data['total_cdf']:,.2f}".replace(',', ' '), 
                 f"{data['total_usd']:,.2f}".replace(',', ' ')]
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
            
            # Créer le buffer PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                               rightMargin=1*cm, leftMargin=1*cm, 
                               topMargin=1*cm, bottomMargin=1*cm)
            
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
            
            # Tableau des regroupements
            elements.append(Paragraph("<b>DÉTAILS PAR REGROUPEMENT</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.3*cm))
            
            # En-têtes du tableau
            critere = data['critere']
            if critere == 'nature':
                headers = ['Nature Économique', 'Nombre', 'Total CDF', 'Total USD']
                groups = data['groups']
                table_data = [headers]
                for group in groups:
                    total_cdf = group.get('total_cdf', 0)
                    total_usd = group.get('total_usd', 0)
                    
                    # Convertir en nombre si c'est une chaîne
                    try:
                        total_cdf = float(total_cdf) if total_cdf else 0
                    except (ValueError, TypeError):
                        total_cdf = 0
                    
                    try:
                        total_usd = float(total_usd) if total_usd else 0
                    except (ValueError, TypeError):
                        total_usd = 0
                    
                    table_data.append([
                        str(group.get('nature_economique__titre', 'N/A')),
                        str(group.get('nombre', 0)),
                        f"{total_cdf:,.2f}".replace(',', ' '),
                        f"{total_usd:,.2f}".replace(',', ' ')
                    ])
            elif critere == 'service':
                headers = ['Service Bénéficiaire', 'Nombre', 'Total CDF', 'Total USD']
                groups = data['groups']
                table_data = [headers]
                for group in groups:
                    total_cdf = group.get('total_cdf', 0)
                    total_usd = group.get('total_usd', 0)
                    
                    # Convertir en nombre si c'est une chaîne
                    try:
                        total_cdf = float(total_cdf) if total_cdf else 0
                    except (ValueError, TypeError):
                        total_cdf = 0
                    
                    try:
                        total_usd = float(total_usd) if total_usd else 0
                    except (ValueError, TypeError):
                        total_usd = 0
                    
                    table_data.append([
                        str(group.get('service_beneficiaire__nom_service', 'N/A')),
                        str(group.get('nombre', 0)),
                        f"{total_cdf:,.2f}".replace(',', ' '),
                        f"{total_usd:,.2f}".replace(',', ' ')
                    ])
            elif critere == 'banque':
                headers = ['Banque', 'Nombre', 'Total CDF', 'Total USD']
                groups = data['groups']
                table_data = [headers]
                for group in groups:
                    total_cdf = group.get('total_cdf', 0)
                    total_usd = group.get('total_usd', 0)
                    
                    # Convertir en nombre si c'est une chaîne
                    try:
                        total_cdf = float(total_cdf) if total_cdf else 0
                    except (ValueError, TypeError):
                        total_cdf = 0
                    
                    try:
                        total_usd = float(total_usd) if total_usd else 0
                    except (ValueError, TypeError):
                        total_usd = 0
                    
                    table_data.append([
                        str(group.get('banque__nom_banque', 'N/A')),
                        str(group.get('nombre', 0)),
                        f"{total_cdf:,.2f}".replace(',', ' '),
                        f"{total_usd:,.2f}".replace(',', ' ')
                    ])
            elif critere == 'mois':
                headers = ['Mois', 'Nombre', 'Total CDF', 'Total USD']
                groups = data['groups']
                table_data = [headers]
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                for group in groups:
                    total_cdf = group.get('total_cdf', 0)
                    total_usd = group.get('total_usd', 0)
                    
                    # Convertir en nombre si c'est une chaîne
                    try:
                        total_cdf = float(total_cdf) if total_cdf else 0
                    except (ValueError, TypeError):
                        total_cdf = 0
                    
                    try:
                        total_usd = float(total_usd) if total_usd else 0
                    except (ValueError, TypeError):
                        total_usd = 0
                    
                    mois_num = group.get('mois', 0)
                    table_data.append([
                        str(mois_noms[mois_num] if mois_num < len(mois_noms) else f"Mois {mois_num}"),
                        str(group.get('nombre', 0)),
                        f"{total_cdf:,.2f}".replace(',', ' '),
                        f"{total_usd:,.2f}".replace(',', ' ')
                    ])
            
            # Créer le tableau
            table = Table(table_data, colWidths=[6*cm, 3*cm, 5*cm, 5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.5*cm))
            
            # Total général
            total_cdf = 0
            total_usd = 0
            total_nombre = 0
            
            for g in data['groups']:
                try:
                    cdf_val = float(g.get('total_cdf', 0))
                    total_cdf += cdf_val
                except (ValueError, TypeError):
                    pass
                
                try:
                    usd_val = float(g.get('total_usd', 0))
                    total_usd += usd_val
                except (ValueError, TypeError):
                    pass
                
                try:
                    nombre_val = int(g.get('nombre', 0))
                    total_nombre += nombre_val
                except (ValueError, TypeError):
                    pass
            
            total_data = [
                ['TOTAL GÉNÉRAL', str(total_nombre), 
                 f"{total_cdf:,.2f}".replace(',', ' '), 
                 f"{total_usd:,.2f}".replace(',', ' ')]
            ]
            
            total_table = Table([total_data], colWidths=[6*cm, 3*cm, 5*cm, 5*cm])
            total_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(total_table)
            
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
